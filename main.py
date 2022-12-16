import pathlib
import shutil

from PIL import Image

from ffmpeg.ffmpeg_api import FfmpegGenerator

from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
import sys
import os
from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 KB', compression='zip')


class SizeDirectory:
    def __init__(self, jpg, mp4, ai, root):
        self.jpg_dir_path = jpg
        self.mp4_dir_path = mp4
        self.ai_dir_path = ai
        self.root = root


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.working_directory = None
        self._init_ui()
        self.default_render_attributes = {'extension': 'mp4', 'duration': 5, 'fade': False}
        self.stats = {'digitals': 0,
                      'prints': 0}

    def _add_label(self, label_name: str, text: str = None, point: QPoint = None):
        setattr(self, label_name, QtWidgets.QLabel(self))
        if text:
            self.__getattribute__(label_name).setText(text)
            self.__getattribute__(label_name).adjustSize()
        if point:
            self.__getattribute__(label_name).move(point)

    def _add_button(self, button_name: str, text: str = None, point: QPoint = None, on_click=None):
        setattr(self, button_name, QtWidgets.QPushButton(self))
        if text:
            self.__getattribute__(button_name).setText(text)
            self.__getattribute__(button_name).adjustSize()
        if point:
            self.__getattribute__(button_name).move(point)
        if on_click:
            self.__getattribute__(button_name).clicked.connect(on_click)

    def _init_ui(self):
        self._add_label(label_name='label_about_path',
                        text='Путь к папке с макетами:',
                        point=QPoint(10, 10))
        self._add_label(label_name='label_path',
                        text='',
                        point=QPoint(150, 10))

        self._add_label(label_name='label_about_digital',
                        text='Количество digital макетов: ',
                        point=QPoint(150, 30))
        self._add_label(label_name='label_about_print',
                        text='Количество print макетов: ',
                        point=QPoint(150, 60))

        self.path_window = QMainWindow()
        self._add_button(button_name='choose_path_btn',
                         text='Выбрать директорию',
                         point=QPoint(10, 30),
                         on_click=self.choose_path)
        self._add_button(button_name='render_digital_btn',
                         text='Рендер digital',
                         point=QPoint(350, 30),
                         on_click=self.render_digital)

        self._add_button(button_name='complex_render_digital_btn',
                         text='Рендер + Каталогизация digital',
                         point=QPoint(350, 55),
                         on_click=self.complex_digital_render)

    def create_directory(self, file_name) -> SizeDirectory:
        if ".jpg" in file_name or '.ai' in file_name:
            size_dir_path = os.path.join(self.working_directory, (file_name.replace('.jpg', '')).replace('.ai', ''))
            mp4_dir_path = os.path.join(size_dir_path, "Видео")
            jpg_dir_path = os.path.join(size_dir_path, "JPG")
            ai_dir_path = os.path.join(size_dir_path, "Исходники")
            logger.debug("CREATING\n", size_dir_path, "\n", mp4_dir_path, "\n", jpg_dir_path, "\n", ai_dir_path)
            try:
                os.mkdir(size_dir_path)
                os.mkdir(mp4_dir_path)
                os.mkdir(jpg_dir_path)
                os.mkdir(ai_dir_path)
            except FileExistsError:
                pass
            return SizeDirectory(jpg_dir_path, mp4_dir_path, ai_dir_path, size_dir_path)

    @staticmethod
    def check_size(size: tuple) -> bool:
        return size[0] % 2 == 0 and size[1] % 2 == 0

    def check_pixels(self, file_path, file_name):
        img_file = Image.open(fp=file_path)
        if self.check_size(img_file.size) is False:
            warning = QMessageBox()
            warning.setIcon(QMessageBox.Critical)
            warning.setText(f"{file_name} кажется в .jpg файле есть лишние пиксели!\n"
                            f"(Или в разрешении есть нечетное число)")
            warning.setInformativeText(f"Путь к файлу: {file_path}")
            warning.setWindowTitle(f"Лишние пиксели в {file_name}!")
            warning.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            warning.exec_()

    def complex_digital_render(self):
        for root, dirs, files in os.walk(self.working_directory):
            for file_name in files:
                size_dir = self.create_directory(file_name)
                file_path = os.path.join(pathlib.Path(root), file_name)
                if '.jpg' in file_name:
                    self.check_pixels(file_path, file_name)
                    shutil.move(file_path, size_dir.jpg_dir_path)
                    render_attributes = self.parse_file_name(str(file_path))
                    input_file_path = os.path.join(size_dir.jpg_dir_path, file_name)
                    size = FfmpegGenerator(input_file_path=input_file_path,
                                           video_extension=render_attributes['extension'],
                                           video_duration=render_attributes['duration'])
                    try:
                        size.create_preview()
                        size.render_video()
                    except [FileExistsError, FileNotFoundError]:
                        pass
                if '.ai' in file_name:
                    shutil.move(file_path, size_dir.ai_dir_path)

    @staticmethod
    def parse_file_name(name: str) -> dict:
        render_attributes = {'extension': 'mp4', 'duration': 5, 'fade': False}
        if "avi" in name.lower():
            render_attributes['extension'] = 'avi'
        if 'sec' in name.lower():
            render_attributes['duration'] = name.split("sec")[0].strip().split(" ")[-1]
        if 'fade' in name.lower():
            render_attributes['fade'] = True
        return render_attributes

    def render_digital(self):
        for root, dirs, files in os.walk(self.working_directory):
            if "JPG" == root[-3::]:
                jpg_path = os.path.join(pathlib.Path(root), files[0])
                self.check_pixels(jpg_path, files[0])
                render_attributes = self.parse_file_name(str(jpg_path))
                size = FfmpegGenerator(input_file_path=jpg_path,
                                       video_extension=render_attributes['extension'],
                                       video_duration=render_attributes['duration'])
                try:
                    size.create_preview()
                    size.render_video()
                except [FileExistsError, FileNotFoundError]:
                    pass

    def choose_path(self):
        self.working_directory = str(
            QFileDialog.getExistingDirectory(self.path_window, "Выберите директорию с размерами"))
        self.label_path.setText(self.working_directory)
        self.label_path.adjustSize()
        self.calculate_statistic()

    def display_statistic(self):
        self.label_about_print.setText('Количество print макетов: ' + str(self.stats['prints']))
        self.label_about_print.adjustSize()
        self.label_about_digital.setText('Количество digital макетов: ' + str(self.stats['digitals']))
        self.label_about_digital.adjustSize()

    def calculate_statistic(self):

        for root, dirs, files in os.walk(self.working_directory):
            for directory in dirs:
                if directory.upper() == "JPG":
                    self.stats['digitals'] += 1
                if directory.capitalize() == "Принт":
                    self.stats['prints'] += 1
            if self.stats['digitals'] == 0:
                for file in files:
                    if ".ai" in file:
                        self.stats['digitals'] += 1
                    if '.eps' in file:
                        self.stats['prints'] += 1
                        self.stats['digitals'] -= 1
        self.display_statistic()


def window():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setGeometry(1000, 400, 800, 200)
    win.setWindowTitle("mp4_renderer")
    win.show()
    sys.exit(app.exec_())


window()
