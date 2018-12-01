from util.Config import Config
import requests
import urllib
import urllib.request
import json
import time

class Danmu(object):
    def __init__(self):
        self.config = Config()
        self.http_config = {
            'getUrl': 'http://api.live.bilibili.com/ajax/msg',
            'sendUrl': 'http://api.live.bilibili.com/msg/send',
            'header': {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh,en-US;q=0.9,en;q=0.8,zh-TW;q=0.7,zh-CN;q=0.6",
                "Cookie": self.config.get('cookie', 'danmu'),
                "Host": "api.live.bilibili.com",
                "Referer": "http://live.bilibili.com/" + self.config.get('roomId'),
                "User-Agent": self.config.get('User-Agent', 'headers')
            }
        }
        self.send_lock = False

    def get(self):
        """获取弹幕（单次上限10条）"""
        room_id = self.config.get('roomId')
        post_data = {'token:': '', 'csrf_token:': '', 'roomid': room_id}
        response = requests.post(
            url = self.http_config['getUrl'],
            data = post_data,
            headers = self.http_config['header']
        ).json()
        # 获取最后的弹幕时间
        config_time = self.config.get(module='danmu', key='timestamp')
        config_time = float(config_time) if config_time else 0

        if 'code' in response and response['code'] == 0:
            # 解析弹幕
            result = []
            for danmu in response['data']['room']:
                # 判断弹幕是否被处理过
                current_time = time.mktime(time.strptime(danmu['timeline'], "%Y-%m-%d %H:%M:%S"))
                if config_time >= current_time:
                    continue

                self.config.set(module='danmu', key='timestamp', value=current_time)
                result.append({
                    'name': danmu['nickname'],
                    'time': danmu['timeline'],
                    'uid': str(danmu['uid']),
                    'text': danmu['text']
                })
            return result
        else:
            raise Exception('Cookie 无效')

    def send(self, text):
        """发送弹幕"""
        elapsed_time = 0
        while self.send_lock:
            time.sleep(1)
            # 判断等待超时
            elapsed_time += 1
            if (elapsed_time > 30):
                return None

        # 将超过20字的弹幕切片后发送
        length_limit = 20
        if len(text) > length_limit:
            for i in range(0, len(text), length_limit):
                self.send(text[i:i + length_limit])
                time.sleep(1.5)
            return True

        # 准备数据
        self.send_lock = True
        try:
            room_id = self.config.get('roomId')
            post_data = {
                'color': '16777215',
                'csrf_token': self.config.get("csrf_token", 'danmu'),
                'fontsize': '25',
                'mode': '1',
                'msg': text,
                'rnd': '1543573073',
                'roomid': room_id
            }
            # 发送请求
            response = requests.post(
                url = self.http_config['sendUrl'],
                data = post_data,
                headers = self.http_config['header']
            ).json()
            return 'code' in response and response['code'] == 0
        except Exception as e:
            raise e
        finally:
            self.send_lock = False
