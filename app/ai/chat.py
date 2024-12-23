import requests
from ..config import config
from .. import log

logger = log.setup_logger(__name__)


# 聊天功能---调用gpt模型
class Ai_msg:

    def __init__(self):
        self.chat_url = config.chat_url
        self.chat_apikey = config.chat_apikey
        self.headers = config.headers
        self.error_reply = config.error_reply

    def chat_gpt(self, msg, model):
        url = self.chat_url
        self.headers["Sec-Fetch-Mode"] = "cors"
        self.headers["Authorization"] = "Bearer " + self.chat_apikey
        data = {
            "model": model,
            "messages": msg,
            "max_tokens": 6000,
            "stream": False,
        }
        req = requests.post(url, headers=self.headers, json=data, timeout=120)
        try:
            rep = req.json()["choices"][0]["message"]["content"]
            return rep
        except Exception as e:
            logger.error("gpt请求失败: %s", str(e))
            return self.error_reply
