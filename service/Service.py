import threading, time
import ctypes

class Service(object):
    """基础服务"""

    def start(self):
        """将循环变量标记为True，启动线程"""
        self.threadRun = True
        threading.Thread(target=self.__run).start()

    def __run(self):
        """持续运行run()函数"""
        while self.threadRun:
            self.run()

    def run(self):
        """占位，被子类的run()覆盖"""
        self.stop()
        raise Exception('未实现 service 的 run 函数')

    def stop(self):
        """停止运行"""
        self.threadRun = False

