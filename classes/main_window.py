from classes import QMainWindow, uic, QtWidgets, QPoint, QMessageBox, QFileDialog, walk, path, mkdir, Image, pathlib, \
    shutil, FfmpegProcessor, RenderOptions, ImageMagickProcessor


class SizeDirectory:
    def __init__(self, jpg, mp4, ai, root):
        self.jpg_dir_path = jpg
        self.mp4_dir_path = mp4
        self.ai_dir_path = ai
        self.root = root


class MainWindow(QMainWindow):
    def __init__(self, logger):
        super(MainWindow, self).__init__()
        uic.loadUi(f"{pathlib.Path('').parent.absolute()}\\ui\\MainWindow.ui", self)
        self._logger = logger
        self.label_about_digital = None
        self.label_about_print = None
        self.working_directory = None
        self.bad_jpg_warning = None
        self.path_window = None
        self.label_path = None
        self._init_ui()
        self.stats = {'digitals': 0,
                      'prints': 0}

    def _add_label(self, label_name: str, text: str = None, point: QPoint = None) -> None:
        setattr(self, label_name, QtWidgets.QLabel(self))
        if text:
            self.__getattribute__(label_name).setText(text)
            self.__getattribute__(label_name).adjustSize()
        if point:
            self.__getattribute__(label_name).move(point)

    def _add_button(self, button_name: str, text: str = None, point: QPoint = None, on_click=None) -> None:
        setattr(self, button_name, QtWidgets.QPushButton(self))
        if text:
            self.__getattribute__(button_name).setText(text)
            self.__getattribute__(button_name).adjustSize()
        if point:
            self.__getattribute__(button_name).move(point)
        if on_click:
            self.__getattribute__(button_name).clicked.connect(on_click)

    def _invoke_window(self, window_name: str) -> None:
        setattr(self, window_name, QMainWindow())

    def _add_message_box(self, box_name: str, text: str, inf_text: str, title: str, icon: QMessageBox) -> None:
        setattr(self, box_name, QMessageBox())
        self.__getattribute__(box_name).setIcon(icon)
        self.__getattribute__(box_name).setText(text)
        self.__getattribute__(box_name).setInformativeText(inf_text)
        self.__getattribute__(box_name).setWindowTitle(title)
        self.__getattribute__(box_name).setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def _init_ui(self) -> None:
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
                         on_click=self._choose_path)
        self._add_button(button_name='render_digital_btn',
                         text='Рендер digital',
                         point=QPoint(350, 30),
                         on_click=self.render_digital)

        self._add_button(button_name='complex_render_digital_btn',
                         text='Рендер + Каталогизация digital',
                         point=QPoint(350, 55),
                         on_click=self._complex_digital_render)

        self._add_button(button_name='render_print_btn',
                         text='Рендер принта',
                         point=QPoint(350, 80),
                         on_click=self.render_print)

    def _choose_path(self):
        self.working_directory = str(
            QFileDialog.getExistingDirectory(self.path_window, "Выберите директорию с размерами"))
        self.label_path.setText(self.working_directory)
        self.label_path.adjustSize()
        self._calculate_statistic()

    def _display_statistic(self):
        self.label_about_print.setText('Количество print макетов: ' + str(self.stats['prints']))
        self.label_about_print.adjustSize()
        self.label_about_digital.setText('Количество digital макетов: ' + str(self.stats['digitals']))
        self.label_about_digital.adjustSize()

    def _calculate_statistic(self):
        self.stats = {'digitals': 0,
                      'prints': 0}
        for root, dirs, files in walk(self.working_directory):
            for file in files:
                if ".ai" in file:
                    self.stats['digitals'] += 1
                if '.eps' in file:
                    self.stats['prints'] += 1
                    self.stats['digitals'] -= 1
        self._display_statistic()

    def _generate_paths(self, file_name: str) -> SizeDirectory:
        size_dir_path = path.join(self.working_directory, (file_name.replace('.jpg', '')).replace('.ai', ''))
        mp4_dir_path = path.join(size_dir_path, "Видео")
        jpg_dir_path = path.join(size_dir_path, "JPG")
        ai_dir_path = path.join(size_dir_path, "Исходники")
        return SizeDirectory(jpg_dir_path, mp4_dir_path, ai_dir_path, size_dir_path)

    def _generate_dirs(self, sd: SizeDirectory) -> None:
        self._logger.debug("CREATING\n", sd.root, "\n", sd.mp4_dir_path, "\n", sd.jpg_dir_path, "\n", sd.ai_dir_path)
        mkdir(sd.root)
        mkdir(sd.mp4_dir_path)
        mkdir(sd.jpg_dir_path)
        mkdir(sd.ai_dir_path)

    def _create_directory(self, file_name) -> SizeDirectory:
        if self._file_is_img_or_ai(file_name):
            sd = self._generate_paths(file_name)
            try:
                self._generate_dirs(sd)
            except FileExistsError:
                self._logger.debug(f"Dirs for {file_name} already exists!")
            return sd

    @staticmethod
    def _file_is_img_or_ai(file_name: str) -> bool:
        return ".jpg" in file_name or '.ai' in file_name

    @staticmethod
    def _check_digital_image_dimensions(size: tuple) -> bool:
        return size[0] % 2 == 0 and size[1] % 2 == 0

    def _check_pixels(self, file_path: str, file_name: str) -> None:
        img_file = Image.open(fp=file_path)
        if self._check_digital_image_dimensions(img_file.size) is False:
            self.bad_jpg_warning.seText(f"{file_name} кажется в .jpg файле есть лишние пиксели!\n"
                                        "(Или в разрешении есть нечетное число)")
            self.bad_jpg_warning.setInformativeText(f"Путь к файлу: {file_path}")
            self.bad_jpg_warning.setWindowTitle(f"Лишние пиксели в {file_name}!")
            self.bad_jpg_warning.exec_()

    @staticmethod
    def _get_render_options_digital(name: str) -> dict:
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

    def _complex_digital_render(self) -> None:
        for root, dirs, files in walk(self.working_directory):
            for file_name in files:
                size_dir = self._create_directory(file_name)
                file_path = path.join(pathlib.Path(root), file_name)
                if '.jpg' in file_name:
                    self._check_pixels(file_path, file_name)
                    shutil.move(file_path, size_dir.jpg_dir_path)
                    render_attributes = self._get_render_options_digital(str(file_path))
                    input_file_path = path.join(size_dir.jpg_dir_path, file_name)
                    ffmpeg_gen = FfmpegProcessor(input_file_path=input_file_path,
                                                 video_extension=render_attributes['extension'],
                                                 video_duration=render_attributes['duration'],
                                                 additional_attributes=render_attributes['additional_attributes'])
                    try:
                        ffmpeg_gen.create_preview()
                        ffmpeg_gen.render_video()
                    except [FileExistsError, FileNotFoundError]:
                        pass
                if '.ai' in file_name:
                    shutil.move(file_path, size_dir.ai_dir_path)

    def render_digital(self) -> None:
        for root, dirs, files in walk(self.working_directory):
            if self._in_jpg_directory(root):
                jpg_path = path.join(pathlib.Path(root), files[0])
                self._check_pixels(jpg_path, files[0])
                render_attributes = self._get_render_options_digital(str(jpg_path))
                ffmpeg_gen = FfmpegProcessor(input_file_path=jpg_path,
                                             video_extension=render_attributes['extension'],
                                             video_duration=render_attributes['duration'],
                                             additional_attributes=render_attributes['additional_attributes'])
                try:
                    ffmpeg_gen.create_preview()
                    ffmpeg_gen.render_video()
                except Exception as exc:
                    self._logger.debug(str(exc.args))

    def get_full_size_and_short_size_from_path(self, path_string: str) -> tuple:
        escaped_working_dir = self.working_directory.replace("/", "\\")
        full_size = path_string.replace(escaped_working_dir, "")
        full_size = full_size.replace("\\Исходник\\Illustrator 2020.eps", "")
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

    @staticmethod
    def _in_jpg_directory(root: str) -> bool:
        return "JPG" == root[-3::] or "jpg" == root[-3::]

    def _get_render_options_print(self, file_path: str) -> RenderOptions:
        directory = pathlib.Path(file_path.replace("Illustrator 2020.eps", "")).parent
        short_size, full_size = self.get_full_size_and_short_size_from_path(file_path)
        render_ppi = self.ppi_table(short_size)
        return RenderOptions(input_file_options=f"-colorspace cmyk -units pixelsperinch -density {render_ppi}",
                             output_file_options="-compress lzw -colorspace cmyk",
                             directory=directory,
                             full_size=full_size)

    @staticmethod
    def _in_origin_directory(root: str) -> bool:
        return "Исходник" in root[-9::] or "исходник" in root[-9::]

    @staticmethod
    def _get_eps_file(files: list[pathlib.Path]) -> tuple[bool, int]:
        for i in range(0, len(files)):
            if ".eps" in files[i]:
                return True, i
        return False, -1

    def render_print(self):
        for root, dirs, files in walk(self.working_directory):
            if self._in_origin_directory(root):
                eps_file_in_directory, eps_file_index = self._get_eps_file(files)
                if eps_file_in_directory:
                    self._logger.debug(f"Input file: {path.join(pathlib.Path(root), files[eps_file_index])}")
                    eps_path = path.join(pathlib.Path(root), files[eps_file_index])
                    render_options = self._get_render_options_print(str(eps_path))
                    im_processor = ImageMagickProcessor(input_file_path=eps_path, render_options=render_options)
                    try:
                        im_processor.render()
                        im_processor.render_preview()
                    except Exception as exc:
                        self._logger.debug(str(exc.args))