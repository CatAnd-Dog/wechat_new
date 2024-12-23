from .. import log
from ..config import Menu, headers, BaseUrl
import requests

# 创建日志记录器，名字通常是当前文件名
logger = log.setup_logger(__name__)


# 创建菜单
class Func:
    def __init__(self):
        self.menu = Menu
        self.base_url = BaseUrl
        self.headers = headers

    def create_menu(self, access_token):
        url = f"{self.base_url}/menu/create?access_token={access_token}"
        req = requests.post(url, headers=self.headers, json=self.menu)
        try:
            rep = req.json()
            if rep["errcode"] == 0:
                logger.info("菜单创建成功")
            else:
                logger.error("菜单创建失败：%s", rep["errmsg"])
        except Exception as e:
            logger.error("菜单创建失败: %s", str(e))

    def delete_menu(self, access_token):
        url = f"{self.base_url}/menu/delete?access_token={access_token}"
        req = requests.get(url)
        try:
            rep = req.json()
            if rep["errcode"] == 0:
                logger.info("菜单删除成功")
            else:
                logger.error("菜单删除失败：%s", rep["errmsg"])
        except Exception as e:
            logger.error("菜单删除失败: %s", str(e))


func = Func()
