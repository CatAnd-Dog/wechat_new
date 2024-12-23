from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, Response
import hashlib
from app.log import setup_logger
from app import config
from typing import Any
from xml.etree import ElementTree as ET
import time
from contextlib import asynccontextmanager
from app.rediscach import redis_client
import requests
from app.func.menu import func

loggger = setup_logger(__name__)


app = FastAPI(
    title="OpaoChat API",
    summary="用于OpaoChat的API",
    description="没有描述",
    version="1.0.0",
    docs_url="/opao",
    contact={
        "name": "Opao",
        "url": "https://chat.opao.xyz",
        "email": "user@example.com",
    },
)


# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 验证微信服务器的URL
async def verify_server_url(request: Request):
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    if not signature or not timestamp or not nonce:
        raise HTTPException(status_code=403, detail="Forbidden")
    tmp_arr = [config.wx_token, timestamp, nonce]
    tmp_arr.sort()
    tmp_str = "".join(tmp_arr)
    tmp_str = hashlib.sha1(tmp_str.encode("utf-8")).hexdigest()
    if not tmp_str == signature:
        raise HTTPException(status_code=403, detail="Forbidden")


# 处理xml消息
async def parse_xml_msg(xml_data):
    root = ET.fromstring(xml_data)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg


# 获取access_token
async def get_access_token():
    access_token = await redis_client.get_access_token()
    return access_token


# 刷新access_token
async def refresh_access_token():
    url = f"{config.base_url}/stable_token"
    data = {
        "grant_type": "client_credential",
        "appid": config.appid,
        "secret": config.appsecret,
        "force_refresh": False,
    }
    try:
        req = requests.post(url, json=data)
        if req.status_code != 0:
            raise HTTPException(status_code=500, detail="获取access_token失败")
        access_token = req.json()["access_token"]
        await redis_client.set_access_token(access_token)
        loggger.info("刷新access_token成功")
        return access_token
    except Exception as e:
        loggger.error("刷新access_token失败: %s", str(e))
        raise HTTPException(status_code=500, detail="获取access_token失败")


# 构造回复给用户的文本消息
def build_text_response(msg, content):
    resp_msg = f"""
        <xml>
        <ToUserName><![CDATA[{msg['FromUserName']}]]></ToUserName>
        <FromUserName><![CDATA[{msg['ToUserName']}]]></FromUserName>
        <CreateTime>{int(time.time())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
        </xml>
    """
    return resp_msg


# 启动和关闭时执行的操作
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时运行的代码
    # 连接redis
    await redis_client.connect()
    # 获取access_token
    access_token = await refresh_access_token()
    # 创建菜单
    func.create_menu(access_token)
    loggger.info("Application is starting up")
    yield
    # 关闭时运行的代码
    await redis_client.close()
    loggger.info("Application is shutting down")


# 挂载一个主页路由
@app.get("/")
async def test():
    return {"message": "Powered by OpaoChat，https://chat.opao.xyz"}


# 挂载wechat路由---用于微信服务器验证
@app.get("/wechat")
async def wechat_verify(request: Request, verify: None = Depends(verify_server_url)):
    echostr = request.args.get("echostr")
    return echostr


# 挂载wechat路由---用于消息处理
@app.post("/wechat")
async def wechat_msg(request: Request, verify: None = Depends(verify_server_url)):
    xml_data = await request.body()
    msg = await parse_xml_msg(xml_data)
    user = msg["FromUserName"]
    msg_type = msg["MsgType"]
    if msg_type == "text":
        content = msg["Content"]
        resp_msg = build_text_response(msg, content)
        return Response(content=resp_msg, media_type="application/xml")
