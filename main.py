import pathlib
import shutil

from yoba_automization import yo

from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QWidget
import sys
import os


class SizeDirectory:
    def __init__(self, jpg, mp4, ai, root):
        self.jpg_dir_path = jpg
        self.mp4_dir_path = mp4
        self.ai_dir_path = ai
        self.root = root


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.default_render_attributes = {'extension': 'mp4', 'duration': 5, 'fade': False}

    def _add_label(self, label_name: str, text: str = None, point: QPoint = None):
        setattr(self, label_name, QtWidgets.QLabel(self))
        print(label_name)
        if text:
            self.__getattribute__(label_name).setText(text)
            self.__getattribute__(label_name).adjustSize()
        if point:
            self.__getattribute__(label_name).move(point)

    def initUI(self):
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
        self.choose_path_btn = QtWidgets.QPushButton(self)
        self.choose_path_btn.setText('Выбрать директорию')
        self.choose_path_btn.adjustSize()
        self.choose_path_btn.move(10, 30)
        self.choose_path_btn.clicked.connect(self.choose_path)

        self.render_digital_btn = QtWidgets.QPushButton(self)
        self.render_digital_btn.setText('Рендер digital')
        self.render_digital_btn.adjustSize()
        self.render_digital_btn.move(350, 30)
        self.render_digital_btn.clicked.connect(self.render_digital)

        self.complex_render_digital_btn = QtWidgets.QPushButton(self)
        self.complex_render_digital_btn.setText('Рендер + Каталогизация digital')
        self.complex_render_digital_btn.adjustSize()
        self.complex_render_digital_btn.move(350, 55)
        self.complex_render_digital_btn.clicked.connect(self.complex_digital_render)

    def create_directory(self, file_name):
        if ".jpg" in file_name or '.ai' in file_name:
            size_dir_path = os.path.join(self.working_directory, (file_name.replace('.jpg', '')).replace('.ai', ''))
            mp4_dir_path = os.path.join(size_dir_path, "Видео")
            jpg_dir_path = os.path.join(size_dir_path, "JPG")
            ai_dir_path = os.path.join(size_dir_path, "Исходники")
            print("CREATING\n", size_dir_path, "\n", mp4_dir_path, "\n", jpg_dir_path, "\n", ai_dir_path)
            try:
                os.mkdir(size_dir_path)
                os.mkdir(mp4_dir_path)
                os.mkdir(jpg_dir_path)
                os.mkdir(ai_dir_path)
            except FileExistsError:
               pass
            return SizeDirectory(jpg_dir_path, mp4_dir_path, ai_dir_path, size_dir_path)

    def complex_digital_render(self):
        for root, dirs, files in os.walk(self.working_directory):
            for file_name in files:
                size_dir = self.create_directory(file_name)
                file_path = os.path.join(pathlib.Path(root), file_name)
                if '.jpg' in file_name:
                    shutil.move(file_path, size_dir.jpg_dir_path)
                    render_attributes = self.parse_file_name(str(file_path))
                    input_file_path = os.path.join(size_dir.jpg_dir_path, file_name)
                    size = yo.Size(input_file_path=input_file_path,
                                   video_extension=render_attributes['extension'],
                                   video_duration=render_attributes['duration'])
                    try:
                        size.create_preview()
                        size.render_video()
                    except:
                        pass
                if '.ai' in file_name:
                    shutil.move(file_path, size_dir.ai_dir_path)

    def parse_file_name(self, name: str):
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
                render_attributes = self.parse_file_name(str(jpg_path))
                mp4_path = os.path.join(pathlib.Path(root).parent, "Видео", files[0].replace('jpg', 'mp4'))
                size = yo.Size(input_file_path=jpg_path,
                        video_extension=render_attributes['extension'],
                        video_duration=render_attributes['duration'])
                try:
                    size.create_preview()
                    size.render_video()
                except:
                    pass

    def choose_path(self):
        self.working_directory = str(QFileDialog.getExistingDirectory(self.path_window, "Выберите директорию с размерами"))
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
            for dir in dirs:
                if dir.upper() == "JPG":
                    self.stats['digitals'] += 1
                if dir.capitalize() == "Принт":
                    self.stats['prints'] += 1
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
