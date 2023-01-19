import pathlib
import shutil
from PIL import Image
from ffmpeg.ffmpeg_api import FfmpegGenerator
from imagemagick.imagemagick_api import RenderOptions, ImageMagickProcessor
from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
import sys
import os
from loguru import logger as log

# bug fix


class SizeDirectory:
    def __init__(self, jpg, mp4, ai, root):
        self.jpg_dir_path = jpg
        self.mp4_dir_path = mp4
        self.ai_dir_path = ai
        self.root = root


class MainWindow(QMainWindow):
    def __init__(self, logger):
        super(MainWindow, self).__init__()
        self.logger = logger
        self.working_directory = None
        self.bad_jpg_warning = None
        self.path_window = None
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

    def _invoke_window(self, window_name: str):
        setattr(self, window_name, QMainWindow())

    def _add_message_box(self, box_name: str, text: str, inf_text: str, title: str, icon: QMessageBox):
        setattr(self, box_name, QMessageBox())
        self.__getattribute__(box_name).setIcon(icon)
        self.__getattribute__(box_name).setText(text)
        self.__getattribute__(box_name).setInformativeText(inf_text)
        self.__getattribute__(box_name).setWindowTitle(title)
        self.__getattribute__(box_name).setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def _init_ui(self):
        self._add_message_box(box_name='bad_jpg_warning',
                              text=f"Кажется в одном из .jpg файлов есть лишние пиксели!\n"
                                   "(Или в разрешении есть нечетное число)",
                              inf_text="",
                              title=f"Ошибка работы ffmpeg!",
                              icon=QMessageBox.Critical)

        self._invoke_window('path_window')

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

        self._add_button(button_name='render_print_btn',
                         text='Рендер принта',
                         point=QPoint(350, 80),
                         on_click=self.render_print)

    def _generate_paths(self, file_name: str):
        size_dir_path = os.path.join(self.working_directory, (file_name.replace('.jpg', '')).replace('.ai', ''))
        mp4_dir_path = os.path.join(size_dir_path, "Видео")
        jpg_dir_path = os.path.join(size_dir_path, "JPG")
        ai_dir_path = os.path.join(size_dir_path, "Исходники")
        return SizeDirectory(jpg_dir_path, mp4_dir_path, ai_dir_path, size_dir_path)

    def _generate_dirs(self, sd: SizeDirectory):
        self.logger.debug("CREATING\n", sd.root, "\n", sd.mp4_dir_path, "\n", sd.jpg_dir_path, "\n", sd.ai_dir_path)
        os.mkdir(sd.root)
        os.mkdir(sd.mp4_dir_path)
        os.mkdir(sd.jpg_dir_path)
        os.mkdir(sd.ai_dir_path)

    @staticmethod
    def _file_is_img_or_ai(file_name):
        return ".jpg" in file_name or '.ai' in file_name

    def create_directory(self, file_name) -> SizeDirectory:
        if self._file_is_img_or_ai(file_name):
            sd = self._generate_paths(file_name)
            try:
                self._generate_dirs(sd)
            except FileExistsError:
                self.logger.debug(f"Dirs for {file_name} already exists!")
            return sd

    @staticmethod
    def check_size(size: tuple) -> bool:
        return size[0] % 2 == 0 and size[1] % 2 == 0

    def check_pixels(self, file_path, file_name):
        img_file = Image.open(fp=file_path)
        if self.check_size(img_file.size) is False:
            self.bad_jpg_warning.seText(f"{file_name} кажется в .jpg файле есть лишние пиксели!\n"
                                        "(Или в разрешении есть нечетное число)")
            self.bad_jpg_warning.setInformativeText(f"Путь к файлу: {file_path}")
            self.bad_jpg_warning.setWindowTitle(f"Лишние пиксели в {file_name}!")
            self.bad_jpg_warning.exec_()

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
                    ffmpeg_gen = FfmpegGenerator(input_file_path=input_file_path,
                                                 video_extension=render_attributes['extension'],
                                                 video_duration=render_attributes['duration'])
                    try:
                        ffmpeg_gen.create_preview()
                        ffmpeg_gen.render_video()
                    except [FileExistsError, FileNotFoundError]:
                        pass
                if '.ai' in file_name:
                    shutil.move(file_path, size_dir.ai_dir_path)

    @staticmethod
    def parse_file_name(name: str) -> dict:
        render_attributes = {'extension': 'mp4', 'duration': 5, 'fade': False, 'additional_attributes': ""}
        if "avi" in name.lower():
            render_attributes['extension'] = 'avi'
        if 'sec' in name.lower():
            render_attributes['duration'] = name.split("sec")[0].strip().split(" ")[-1]
        if 'wmv' in name.lower():
            render_attributes['extension'] = 'wmv'
            render_attributes['additional_attributes'] = "-qscale 2 -vcodec msmpeg4"
        if 'fade' in name.lower():
            render_attributes['fade'] = True
        return render_attributes

    def get_full_size_and_short_size_from_path(self, path):
        escaped_working_dir = self.working_directory.replace("/", "\\")
        full_size = path.replace(escaped_working_dir, "")
        full_size = full_size.replace("\\Исходники\\Illustrator 2020.eps", "")
        full_size = full_size.replace("\\", "")
        return full_size.split(" ")[0], full_size

    @staticmethod
    def ppi_table(size: str) -> int:
        size = size.replace("х", "x")
        length = int(size.split("x")[0])
        width = int(size.split("x")[1])

        if 2.5 < length / width:
            return 150
        if 1.75 < length / width < 2.5:
            return 720
        if 1.5 < length / width <= 1.75:
            return 900
        if 0.7 < length / width <= 1.5:
            return 1100
        if 0.5 < length / width <= 0.7:
            return 900
        if 0.3 < length / width <= 0.5:
            return 1100

    def get_render_options(self, path: str) -> RenderOptions:
        directory = pathlib.Path(path.replace("Illustrator 2020.eps", "")).parent
        short_size, full_size = self.get_full_size_and_short_size_from_path(path)
        render_ppi = self.ppi_table(short_size)
        return RenderOptions(input_file_options=f"-colorspace cmyk -units pixelsperinch -density {render_ppi}",
                             output_file_options="-compress lzw -colorspace cmyk",
                             directory=directory,
                             full_size=full_size)

    def render_digital(self):
        for root, dirs, files in os.walk(self.working_directory):
            if self._in_jpg_directory(root):
                jpg_path = os.path.join(pathlib.Path(root), files[0])
                self.check_pixels(jpg_path, files[0])
                render_attributes = self.parse_file_name(str(jpg_path))
                ffmpeg_gen = FfmpegGenerator(input_file_path=jpg_path,
                                             video_extension=render_attributes['extension'],
                                             video_duration=render_attributes['duration'],
                                             additional_attributes=render_attributes['additional_attributes'])
                try:
                    ffmpeg_gen.create_preview()
                    ffmpeg_gen.render_video()
                except Exception as e:
                    log.debug(e)

    @staticmethod
    def _in_origin_directory(root):
        return "Исходники" == root[-9::]

    @staticmethod
    def _in_jpg_directory(root):
        return "JPG" == root[-3::]

    def render_print(self):
        for root, dirs, files in os.walk(self.working_directory):
            if self._in_origin_directory(root):
                if len(files) >= 2 and ".eps" in files[1]:
                    log.debug(f"Input file: {os.path.join(pathlib.Path(root), files[1])}")
                    eps_path = os.path.join(pathlib.Path(root), files[1])
                    render_options = self.get_render_options(str(eps_path))
                    im_processor = ImageMagickProcessor(input_file_path=eps_path, render_options=render_options)
                    try:
                        im_processor.render()
                        im_processor.render_preview()
                    except Exception as e:
                        log.debug(e)

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
        self.stats = {'digitals': 0,
                      'prints': 0}
        for root, dirs, files in os.walk(self.working_directory):
            for file in files:
                if ".ai" in file:
                    self.stats['digitals'] += 1
                if '.eps' in file:
                    self.stats['prints'] += 1
                    self.stats['digitals'] -= 1
        self.display_statistic()


def window():
    log.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')
    app = QApplication(sys.argv)
    win = MainWindow(log)
    win.setGeometry(1000, 400, 800, 200)
    win.setWindowTitle("LM Ad Render")
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        window()
        input()
    except Exception as e:
        log.debug(e)
