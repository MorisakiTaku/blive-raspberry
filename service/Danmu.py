from downloader.NeteaseMusic import *

from service.Service import Service
from util.Danmu import Danmu
from util.Log import Log

from util.Queue import DownloadQueue
import time

class DanmuService(Service):

    def __init__(self):
        self.danmu = Danmu()
        self.log = Log('Danmu Service')
        self.command = _Operation()
        self.command_map = {
            '点歌': self.command.order_song,
            'Nami': ''
        }

    def run(self):
        try:
            self.parse_danmu()
            time.sleep(10)
        except Exception as e:
            self.log.error(e)

    def parse_danmu(self):
        """解析弹幕"""
        danmu_list = self.danmu.get()
        if danmu_list:
            for danmu in danmu_list:
                self.log.debug('%s: %s' % (danmu['name'], danmu['text']))
                self.danmu_map_func(danmu)

    def danmu_map_func(self, danmu):
        """将对应的指令映射到对应的Action上"""
        text = danmu['text']
        for key in self.command_map.keys():
            # 遍历查询comand是否存在 若存在则反射到对应的Action
            if text.find(key) == 0:
                danmu['command'] = danmu['text'][len(key): len(danmu['text'])].strip()
                self.command_map[key](danmu)
                break


class _Operation(object):

    def __init__(self):
        self.danmu = Danmu()
        self.log = Log('Danmu Service')
        self.downloader = NeteaseMusic()

    def order_song(self, danmu):
        """点歌台"""
        # 如果命令全为数字，跳转到id点歌
        if danmu['command'].isdigit():
            song = self._order_song_id(danmu)
        # 否则按照歌名点歌
        else:
            song = self._order_song_name(danmu)

        if song:
            self.danmu.send('%s 点歌成功' % song['name'])
            DownloadQueue.put({
                    'type': 'music',
                    'id': song['id'],
                    'name': song['name'],
                    'singer': song['ar'][0]['name'],
                    'username': danmu['name']
            })
        else:
            self.danmu.send('找不到%s' % danmu['command'])
            self.log.info('找不到%s' % danmu['command'])

    def _order_song_name(self, danmu):
        """通过歌名点歌"""
        self.log.info('%s 点歌 [%s]' % (danmu['name'], danmu['command']))
        detail = danmu['command'].split('-')
        if len(detail) == 1:
            # 按歌曲名点歌
            song = self.downloader.search_single(danmu['command'].strip())
        elif len(detail) == 2:
            # 按歌曲名-歌手点歌
            song = self.downloader.search_single(detail[0].strip(), detail[1].strip())
        else:
            # 无效命令
            song = {}
        return song

    def _order_song_id(self, danmu):
        """通过id点歌"""
        self.log.info('%s id点歌 [%s]' % (danmu['name'], danmu['command']))
        song = self.downloader.get_info(danmu['command'].strip())
        return song
