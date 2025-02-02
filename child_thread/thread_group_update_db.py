# 线程组 - 更新数据库（更新本地缓存的漫画信息数据库和图片信息数据库）


from PySide6.QtCore import QObject, Signal

from child_thread.thread_analyse_comics_info import ThreadAnalyseComicsInfo
from child_thread.thread_calc_hash import ThreadCalcHash


class ThreadGroupUpdateDB(QObject):
    """线程组 - 更新数据库（更新本地缓存的漫画信息数据库和图片信息数据库）"""
    signal_step = Signal(str, name='当前步骤的名称')
    signal_rate = Signal(str, name='内部进度')
    signal_finished = Signal(object, name='结束')

    def __init__(self, parent=None):
        super().__init__(parent)
        # 分析漫画信息
        self.thread_analyse_comics_info = ThreadAnalyseComicsInfo()
        self.thread_analyse_comics_info.signal_finished.connect(self._start_thread_calc_hash)
        self.thread_analyse_comics_info.signal_step.connect(self.update_schedule_total)
        self.thread_analyse_comics_info.signal_rate.connect(self.update_schedule_step)

        # 计算漫画中图片的hash
        self.thread_calc_hash = ThreadCalcHash()
        self.thread_calc_hash.signal_finished.connect(self.signal_finished.emit)
        self.thread_calc_hash.signal_step.connect(self.update_schedule_total)
        self.thread_calc_hash.signal_rate.connect(self.update_schedule_step)

    def start(self, comics: list):
        self._start_thread_analyse_comics_info(comics)

    def stop(self):
        """设置子线程的停止参数"""
        self.thread_analyse_comics_info.set_stop()
        self.thread_calc_hash.set_stop()

    def _start_thread_analyse_comics_info(self, comics: list):
        """启用子线程-分析漫画信息"""
        self.thread_analyse_comics_info.set_comics(comics)
        self.thread_analyse_comics_info.start()

    def _start_thread_calc_hash(self, comics: list):
        """启用子线程-计算图片hash"""
        self.thread_calc_hash.set_comics(comics)
        self.thread_calc_hash.start()

    def update_schedule_total(self, text: str):
        """更新总进度"""
        self.signal_step.emit(text)

    def update_schedule_step(self, text: str):
        """更新步骤进度"""
        self.signal_rate.emit(text)
