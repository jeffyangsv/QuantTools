from QUANTAXIS.QASetting.QALocalize import cache_path
import os
import time
import json
import requests
import datetime
from QUANTTOOLS.Message.message_func.setting import QAPRO_ID,CORPID,CORPSECRET,AGENTID

# 下面的参数自行填写
# user, strategy_id, account, code, direction, offset, price, volume, 

class WeChat:
    def __init__(self):
        self.CORPID = CORPID  # 企业ID，在管理后台获取
        self.CORPSECRET = CORPSECRET  # 自建应用的Secret，每个自建应用里都有单独的secret
        self.AGENTID = AGENTID  # 应用ID，在后台应用中获取
        self.TOUSER = "@all"  # 接收者用户名,多个用户用|分割

    def _get_access_token(self):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        values = {
            "corpid": self.CORPID,
            "corpsecret": self.CORPSECRET,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def get_access_token(self):
        try:
            with open(cache_path + os.sep + "access_token.conf", "r") as f:
                t, access_token = f.read().split()
        except:
            with open(cache_path + os.sep + "access_token.conf", "w") as f:
                access_token = self._get_access_token()
                cur_time = time.time()
                f.write("\t".join([str(cur_time), access_token]))
                return access_token
        else:
            cur_time = time.time()
            if 0 < cur_time - float(t) < 7260:
                return access_token
            else:
                with open(cache_path + os.sep + "access_token.conf", "w") as f:
                    access_token = self._get_access_token()
                    f.write("\t".join([str(cur_time), access_token]))
                    return access_token

    def send_data(self, message):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        send_values = {
            "touser": self.TOUSER,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {"content": message},
            "safe": "0",
        }
        send_msges = bytes(json.dumps(send_values), "utf-8")
        respone = requests.post(send_url, send_msges)
        respone = respone.json()  # 当返回的数据是json串的时候直接用.json即可将respone转换成字典
        return respone["errmsg"]

def send_actionnotice(strategy_id,
                      account,
                      code,
                      direction,
                      offset,
                      volume,
                      price=None,
                      user = QAPRO_ID,
                      now = str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))):
    try:
        # requests.post("http://www.yutiansut.com/signal?user_id={user}&template=xiadan_report&strategy_id={strategy_id}&realaccount={account}&code={code}&order_direction={direction}&order_offset={offset}&price={price}&volume={volume}&order_time={now}".format(user = user, strategy_id = strategy_id, account = account, code = code, direction= direction, offset= offset, price = price, volume = volume, now =now))
        remind_message = f"""用户ID：{user}
                    策略ID：{strategy_id}
                    账号：{account}
                    代码：{code}
                    描述： {direction}
                    order_offset： {offset}
                    价格： {price}
                    数量： {volume}
                    订单时间： {now}
                """.replace(
            " ", ""
        )
        wechat = WeChat()
        wechat.send_data(remind_message)
    except:
        pass

if __name__ == '__main__':
    pass
    # send_actionnotice('strategy001','testaccount','000001','directionxxx','offset','12.68','2000')