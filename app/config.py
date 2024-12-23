import os
from dotenv import load_dotenv
from . import log


# 创建日志记录器，名字通常是当前文件名
logger = log.setup_logger(__name__)

load_dotenv()


# 基础配置
wx_token = os.getenv("WX_TOKEN", "")
appid = os.getenv("APPID", "")
appsecret = os.getenv("APPSECRET", "")
contact = os.getenv("CONTACT", "https://oneperfect.cn")

if not wx_token or not appid or not appsecret:
    logger.error("请检查环境变量配置是否正确！")
    exit(1)

# 聊天配置
chat_url = os.getenv("CHAT_URL", "")
chat_apikey = os.getenv("APIKEY", "")

# 默认模型和回复
chat_model = os.getenv("DEFAILT_MODEL", "gpt-4o-mini")
img_model = os.getenv("IMG_MODEL", chat_model)


error_reply = os.getenv("ERROR_REPLY", "获取回复内容失败，请稍后再试。")


# 请求头、基础URL、菜单配置
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}
BaseUrl = "https://api.weixin.qq.com/cgi-bin"
Menu = {
    "button": [
        {"type": "click", "name": "查询id", "key": "MyId"},
        {
            "name": "指令",
            "sub_button": [
                {
                    "type": "click",
                    "name": "清除记录",
                    "key": "clean",
                },
                {"type": "click", "name": "所有指令", "key": "AllCmd"},
            ],
        },
        {"name": "联系我们", "type": "view", "url": contact},
    ]
}


# redis配置
redis_url = os.getenv("REDIS_URL", "redis://WechatRedis:6379/0")
redis_connections = int(os.getenv("REDIS_CONNECTIONS", 10))
