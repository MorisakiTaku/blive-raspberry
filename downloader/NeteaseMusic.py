from downloader.NeteaseEncryptor import NeteaseEncryptor
from util.Config import Config
import requests
import json
import time

class NeteaseMusic(object):

    def __init__(self):
        all_config = Config()
        self.headers = {
            'User-Agent': all_config.get(key='User-Agent', module='headers'),
            'Cookie':     all_config.get(key='Cookie',     module='headers')
        }

    def prepare(self, data):
        """将post数据转换为网易云的密文"""
        str_ = json.dumps(data)
        encrypt = NeteaseEncryptor(str_)
        return encrypt.get_data()

    def search(self, keyword, singer=None):
        """按歌曲名和歌手搜索歌曲"""
        response = requests.post(
            url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token=',
            data = self.prepare({
                "s": keyword,
                "type": "1",
                "limit": "30",
                "csrf_token": ""
            }),
            headers = self.headers
        ).json()
        # 解析response
        if 'code' in response and response['code'] == 200:
            result = []
            # 遍历歌曲
            for song in response['result']['songs']:
                # 遍历歌手
                song['singer'] = ''
                isSelect = True
                for artist in song['ar']:
                    if singer and artist['name'] == singer:
                        song['singer'] = singer
                        isSelect = True
                    elif singer:
                        isSelect = False
                    else:
                        isSelect = True
                        song['singer'] += artist['name'] + ' '
                if isSelect:
                    song['singer'] = song['singer'].strip()
                    result.append(song)
            return result
        else:
            return []

    def search_single(self, keyword, singer=None):
        """取搜索结果的第一首"""
        result = self.search(keyword, singer)
        if result:
            return result[0]
        else:
            return None

    def get_url(self, song_ids):
        """批量获取歌曲的下载链接"""
        response = requests.post(
            url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token=',
            data = self.prepare({
                'ids': [song_ids],
                'br': 192000,
                'csrf_token': ''
            }),
            headers = self.headers
        ).json()
        # 解析response
        if 'code' in response and response['code'] == 200:
            if 'data' in response:
                return response['data']
            else:
                return []
        else:
            return None

    def get_single_url(self, song_id):
        """取下载链接的第一条"""
        result = self.get_url(song_id)
        if result == None:
            return result
        elif len(result) == 0:
            return {}
        else:
            return result[0]

    def download(self, song_id, filename=None, callback=None):
        """根据id下载歌曲"""
        # 取时间戳作为歌曲临时文件名
        if not filename:
            filename = str(int(time.time()))
        # 获取歌曲并下载
        musicResult = self.get_single_url(song_id)
        if musicResult and 'url' in musicResult:
            musicUrl = musicResult['url']
            filename = './downloader/download/%s.mp3' % filename
            response = requests.get(musicUrl, headers=self.headers, timeout=600).content
            with open(filename, 'wb') as mp3:
                mp3.write(response)
            return filename
        else:
            return False

    def get_info(self, song_id):
        """通过ID获取歌曲信息"""
        response = requests.post(
            url = 'https://music.163.com/weapi/v3/song/detail?csrf_token=',
            data = self.prepare({
                'c': json.dumps([{'id': song_id }]),
                'csrf_token': ''
            }),
            headers = self.headers
        ).json()
        if 'code' in response and response['code'] == 200:
            if 'songs' in response and response['songs']:
                song = response['songs'][0]
                return song
            else:
                return False
        else:
            return False

    def get_lyric(self, song_id):
        """获取歌词"""
        response = requests.post(
            url = 'https://music.163.com/weapi/song/lyric?csrf_token=',
            data = self.prepare({
                'id': song_id,
                'os': 'pc',
                'lv': -1,
                'kv': -1,
                'tv': -1,
                'csrf_token': ''
            }),
            headers = self.headers
        ).json()
        if 'code' in response and response['code'] == 200:
            result = {
                'lyric': '',
                'tlyric': ''
            }
            # 获取原歌词
            if 'lrc' in response and 'lyric' in response['lrc']:
                result['lyric'] = response['lrc']['lyric']
            else:
                return False
            # 获取歌词翻译
            if 'tlyric' in response and 'lyric' in response['tlyric']:
                result['tlyric'] = response['tlyric']['lyric']

            return result
        else:
            return False