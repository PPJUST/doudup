# 子线程-进一步分析漫画的信息
import os
from functools import partial
from multiprocessing import Pool

from child_thread.thread_pattern import ThreadPattern
from class_ import class_comic_info
from class_.class_comic_info import ComicInfo
from module import function_config_similar_option, function_normal


class ThreadAnalyseComicsInfo(ThreadPattern):
    """分析漫画的信息"""

    def __init__(self):
        super().__init__()
        self._step = '分析漫画信息'
        self.comics = []

    def set_comics(self, comics: list):
        self.comics = list(comics)

    def run(self):
        super().run()
        # 遍历列表，提取信息
        comics_data = self.multi_analyse(self.comics)
        """未使用多进程的原版方法
        # 遍历列表，提取信息
        comics_data = {}
        for index, comic in enumerate(self.comics, start=1):
            if self._stop_code:
                break
            self.signal_rate.emit(f'{index}/{len(self.comics)}')
            comic_info_class = ComicInfo(comic)
            comics_data[comic] = comic_info_class
        """
        # 更新本地缓存
        class_comic_info.update_db(comics_data)
        # 结束后发送信号
        self.finished(self.comics.copy())
        # 结束后重置参数
        self.comics.clear()

    def multi_analyse(self, comics: list):
        """多进程提取信息"""
        # 获取相似度算法设置
        threads_count = function_config_similar_option.threads.get()

        # 启用多进程
        comics_data = {}
        cache_comic_info_dict = class_comic_info.read_db()
        with Pool(processes=threads_count) as pool:
            # 使用partial固定部分参数
            calculate_partial = partial(self.get_comic_info_class, cache_comic_info_dict=cache_comic_info_dict)
            # 设置多进程任务：pool.imap()为异步传参，imap中的第一个参数为执行的函数，第二个参数为可迭代对象（用于传参）
            for index, comic_info in enumerate(pool.imap(calculate_partial, comics)):
                if self._stop_code:
                    break
                self.signal_rate.emit(f'{index + 1}/{len(comics)}')
                if comic_info:
                    the_key = comics[index]
                    comics_data[the_key] = comic_info

        return comics_data

    @staticmethod
    def get_comic_info_class(comic, cache_comic_info_dict: dict):
        """用于多线程，将类的赋值中转为函数的调用"""
        print('分析漫画', comic)
        if os.path.exists(comic):
            # 跳过缓存中已存在的漫画（文件大小一致的）
            if comic in cache_comic_info_dict:
                cache_comic_info: ComicInfo = cache_comic_info_dict[comic]
                # 验证文件大小
                local_size = function_normal.get_size(comic)
                cache_size = cache_comic_info.filesize
                if local_size == cache_size:
                    return cache_comic_info
            # 不存在于缓存中，则正常计算
            return ComicInfo(comic)
        else:
            return None
