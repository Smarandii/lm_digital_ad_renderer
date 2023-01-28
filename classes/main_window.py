from classes import QMainWindow, uic, QtWidgets, QPoint, QMessageBox, QFileDialog, walk, path, mkdir, Image, pathlib, \
    shutil, FfmpegProcessor, RenderOptions, ImageMagickProcessor


class SizeDirectory:
    def __init__(self, jpg, mp4, ai, root):
        self.jpg_dir_path = jpg
        self.mp4_dir_path = mp4
        self.ai_dir_path = ai
        self.root = root


class MainWindow(QMainWindow):
    DIGITAL = "digital"
    PRINT = "print"

    def __init__(self, logger):
        super(MainWindow, self).__init__()
        uic.loadUi(f"{pathlib.Path('').parent.absolute()}\\ui\\MainWindow.ui", self)
        self.progress_bar.hide()
        self.progress_bar.setValue(0)
        self.render_print_btn.clicked.connect(self._render_print)
        self.render_digital_btn.clicked.connect(self._render_digital)
        self.complex_render_digital_btn.clicked.connect(self._complex_digital_render)
        self.choose_path_btn.clicked.connect(self._choose_path)
        self._init_table()
        self._init_ui()
        self._logger = logger
        self.bad_jpg_warning = None
        self.render_list = {self.PRINT: [],
                            self.DIGITAL: []}

    def _invoke_window(self, window_name: str) -> None:
        setattr(self, window_name, QMainWindow())

    def _add_message_box(self, box_name: str, text: str, inf_text: str, title: str, icon: QMessageBox) -> None:
        setattr(self, box_name, QMessageBox())
        self.__getattribute__(box_name).setIcon(icon)
        self.__getattribute__(box_name).setText(text)
        self.__getattribute__(box_name).setInformativeText(inf_text)
        self.__getattribute__(box_name).setWindowTitle(title)
        self.__getattribute__(box_name).setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

    def _init_table(self):
        self.table_of_sizes.setColumnCount(2)
        self.table_of_sizes.setHorizontalHeaderLabels(
            ["Рамер макета (шxв)\nНАЗВАНИЕ ПАПКИ", "DPI / Длительность"])

        self.table_of_sizes.setColumnWidth(0, 300)
        self.table_of_sizes.setColumnWidth(1, 200)

    def _init_ui(self) -> None:

        self._invoke_window('path_window')
        self._add_message_box(box_name='bad_jpg_warning',
                              text=f"Кажется в одном из .jpg файлов есть лишние пиксели!\n"
                                   "(Или в разрешении есть нечетное число)",
                              inf_text="",
                              title=f"Ошибка работы ffmpeg!",
                              icon=QMessageBox.Critical)

    def _choose_path(self):
        self.working_directory = str(
            QFileDialog.getExistingDirectory(self.path_window, "Выберите директорию с размерами"))
        self.label_path.setText(self.working_directory)
        self.label_path.adjustSize()
        self._find_sizes_to_display()

    def _define_size_type(self, full_dir_path):
        for root, dirs, files in walk(full_dir_path):
            for dir_ in dirs:
                if "Принт" in dir_:
                    return self.PRINT
                if "Видео" in dir_:
                    return self.DIGITAL
            for file in files:
                if ".jpg" in file:
                    return self.DIGITAL
                if '.eps' in file:
                    return self.PRINT

    def _add_to_render_list(self, directory_name, full_dir_path, size_type, render_options):
        self.render_list[size_type].append(
            {
                "size_name": directory_name,
                "full_dir_path": full_dir_path,
                "render_options": render_options
            }
        )

    def _add_to_table(self, size_type, directory_name, full_dir_path, i):

        if size_type == self.DIGITAL:
            render_options = self._get_render_options_digital(directory_name)
            self._add_to_render_list(directory_name, full_dir_path, size_type, render_options)
            name_item = QtWidgets.QTableWidgetItem(directory_name)
            self.table_of_sizes.setItem(i, 0, name_item)
            duration_item = QtWidgets.QTableWidgetItem(str(render_options['duration']) + " sec")
            self.table_of_sizes.setItem(i, 1, duration_item)

        if size_type == self.PRINT:
            render_options = self._get_render_options_print(str(full_dir_path))
            self._add_to_render_list(directory_name, full_dir_path, size_type, render_options)
            name_item = QtWidgets.QTableWidgetItem(directory_name)
            self.table_of_sizes.setItem(i, 0, name_item)
            dpi = render_options.get_density() // 10
            dpi_item = QtWidgets.QTableWidgetItem(str(dpi) + " dpi")
            self.table_of_sizes.setItem(i, 1, dpi_item)

    def _insert_sizes_in_table(self, dirs):
        self.table_of_sizes.setRowCount(len(dirs))
        for i, directory_name in enumerate(dirs):
            full_dir_path = pathlib.Path(self.working_directory, directory_name)
            size_type = self._define_size_type(full_dir_path)
            self._add_to_table(size_type, directory_name, full_dir_path, i)

    def _find_sizes_to_display(self):
        for root, dirs, files in walk(self.working_directory):
            self._insert_sizes_in_table(dirs)
            break

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

    def _render_digital(self) -> None:
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_bar.setRange(0, len(self.render_list[self.DIGITAL]))
        i = 0
        for root, dirs, files in walk(self.working_directory):
            if self._in_jpg_directory(root):
                jpg_path = path.join(pathlib.Path(root), files[0])
                self._check_pixels(jpg_path, files[0])
                render_attributes = self._get_render_options_digital(str(jpg_path))
                ffmpeg_gen = FfmpegProcessor(input_file_path=jpg_path,
                                             video_extension=render_attributes['extension'],
                                             video_duration=render_attributes['duration'],
                                             additional_attributes=render_attributes['additional_attributes'])
                i += 1
                self.progress_bar.setValue(i)
                try:
                    ffmpeg_gen.create_preview()
                    ffmpeg_gen.render_video()
                except Exception as exc:
                    self._logger.debug(str(exc.args))
        self.progress_bar.hide()

    def _get_full_size_and_short_size_from_path(self, path_string: str) -> tuple:
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
        short_size, full_size = self._get_full_size_and_short_size_from_path(file_path)
        render_ppi = self.ppi_table(short_size)
        return RenderOptions(input_file_options=f"-colorspace cmyk -units pixelsperinch -density {render_ppi}",
                             output_file_options="-compress lzw -colorspace cmyk",
                             directory=directory,
                             full_size=full_size)

    @staticmethod
    def _in_origin_directory(root: str) -> bool:
        return "Исходник" in root[-9::] or "исходник" in root[-9::]

    @staticmethod
    def _get_eps_file(files: list[str]) -> tuple[bool, int]:
        for i in range(0, len(files)):
            if ".eps" in files[i]:
                return True, i
        return False, -1

    def _render_print(self) -> None:
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_bar.setRange(0, len(self.render_list[self.PRINT]) * 2)
        i = 0
        for root, dirs, files in walk(self.working_directory):
            if self._in_origin_directory(root):
                eps_file_in_directory, eps_file_index = self._get_eps_file(files)
                if eps_file_in_directory:
                    self._logger.debug(f"Input file: {path.join(pathlib.Path(root), files[eps_file_index])}")
                    eps_path = path.join(pathlib.Path(root), files[eps_file_index])
                    render_options = self._get_render_options_print(str(eps_path))
                    im_processor = ImageMagickProcessor(input_file_path=eps_path, render_options=render_options)
                    i += 1
                    self.progress_bar.setValue(i)
                    try:
                        im_processor.render()
                        im_processor.render_preview()
                        i += 1
                        self.progress_bar.setValue(i)
                    except Exception as exc:
                        self._logger.debug(str(exc.args))
        self.progress_bar.hide()
