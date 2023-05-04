from classes import QMainWindow, uic, QtWidgets, QMessageBox, QFileDialog, walk, path, mkdir, Image, pathlib, \
    shutil, FfmpegProcessor, RenderOptions, ImageMagickProcessor
from render_options.print_render_options import PrintRenderOptions


class MainWindow(QMainWindow, PrintRenderOptions):
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
        self.working_directory = ""

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
            ["Размер макета (шxв)\nНАЗВАНИЕ ПАПКИ", "DPI / Длительность"])

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

    def _add_to_render_list(self, directory_name, full_dir_path: pathlib.Path, size_type, render_options):
        self.render_list[size_type].append(
            {
                "size_name": directory_name,
                "absolute_path": full_dir_path,
                "full_eps_file_path": full_dir_path.joinpath("Исходники").joinpath(directory_name + ".eps"),
                "render_options": render_options

            }
        )

    def _add_to_table(self, size_type, directory_name, full_dir_path: pathlib.Path, i):

        if size_type == self.DIGITAL:
            render_options = self._get_render_options_digital(directory_name)
            self._add_to_render_list(directory_name, full_dir_path, size_type, render_options)
            name_item = QtWidgets.QTableWidgetItem(directory_name)
            self.table_of_sizes.setItem(i, 0, name_item)
            duration_item = QtWidgets.QTableWidgetItem(str(render_options['duration']) + " sec")
            self.table_of_sizes.setItem(i, 1, duration_item)

        if size_type == self.PRINT:
            render_options = self._get_render_options_print(str(full_dir_path.joinpath("Исходники").joinpath(directory_name + ".eps")))
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

    def _complex_insert_sizes_in_table(self, files):
        self.table_of_sizes.setRowCount(len(files))
        size_type = self.DIGITAL
        for i, file_name in enumerate(files):
            full_dir_path = pathlib.Path(self.working_directory, file_name)
            self._add_to_table(size_type, file_name, full_dir_path, i)

    def _find_sizes_to_display(self):
        for root, dirs, files in walk(self.working_directory):
            if dirs and ("video" not in dirs) and ("Video" not in dirs):
                self._insert_sizes_in_table(dirs)
            elif files:
                files = [file_name for file_name in files if self._format_of_file_is_jpg(file_name)]
                self._complex_insert_sizes_in_table(files)
            break

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

    @staticmethod
    def _format_of_file_is_jpg(file_name):
        return '.jpg' in file_name

    def _render_jpg_images(self):
        self._init_progress_bar(len(self.render_list[self.DIGITAL]))
        for image in self.render_list[self.DIGITAL]:
            if self._format_of_file_is_jpg(image['size_name']):
                self._check_pixels(image['absolute_path'], image['size_name'])
                render_attributes = self._get_render_options_digital(str(image['absolute_path']))
                try:
                    ffmpeg_gen = FfmpegProcessor(input_file_path=str(image['absolute_path']),
                                                 video_extension=render_attributes['extension'],
                                                 video_duration=render_attributes['duration'],
                                                 additional_attributes=render_attributes['additional_attributes'])
                    ffmpeg_gen.render_video()
                    self._add_progress_to_progress_bar()
                except Exception as e:
                    print(e)
                    input()
                    pass
        self.progress_bar.hide()

    def _get_files_from_working_directory(self):
        for root, dirs, files in walk(self.working_directory):
            return files

    def _create_video_directory(self):
        try:
            mkdir(path.join(self.working_directory, "video"))
        except FileExistsError:
            pass

    def _complex_digital_render(self) -> None:
        self._create_video_directory()
        self._render_jpg_images()
        self._find_sizes_to_display()

    def _init_progress_bar(self, length):
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_bar.setRange(0, length)
        self.progress_bar_counter = 0

    def _add_progress_to_progress_bar(self, val=1):
        self.progress_bar_counter += val
        self.progress_bar.setValue(self.progress_bar_counter)

    def _render_digital(self) -> None:
        self._init_progress_bar(len(self.render_list[self.DIGITAL]))
        for root, dirs, files in walk(self.working_directory):
            if self._in_jpg_directory(root):
                jpg_path = path.join(pathlib.Path(root), files[0])
                self._check_pixels(jpg_path, files[0])
                render_attributes = self._get_render_options_digital(str(jpg_path))
                ffmpeg_gen = FfmpegProcessor(input_file_path=jpg_path,
                                             video_extension=render_attributes['extension'],
                                             video_duration=render_attributes['duration'],
                                             additional_attributes=render_attributes['additional_attributes'])
                self._add_progress_to_progress_bar()
                try:
                    ffmpeg_gen.create_preview()
                    ffmpeg_gen.render_video()
                except Exception as exc:
                    self._logger.debug(str(exc.args))
        self.progress_bar.hide()

    @staticmethod
    def _in_jpg_directory(root: str) -> bool:
        return "JPG" == root[-3::] or "jpg" == root[-3::]

    def _get_render_options_print(self, file_path: str) -> RenderOptions:
        directory = pathlib.Path(file_path).parent.parent
        size_name = str(directory).split("\\")[-1]
        render_dpi = self.dpi_table(size_name)
        return RenderOptions(input_file_options=f"-colorspace cmyk -density {render_dpi}",
                             output_file_options="-depth 8 -compress lzw -colorspace cmyk",
                             directory=directory,
                             full_size=file_path,
                             size_name=size_name)

    def _render_print(self) -> None:
        self._init_progress_bar(len(self.render_list[self.PRINT]) * 2)
        for size in self.render_list[self.PRINT]:
            self._logger.debug(f"Input file: {size['full_eps_file_path']}")
            im_processor = ImageMagickProcessor(input_file_path=size['full_eps_file_path'],
                                                render_options=size['render_options'])
            self._add_progress_to_progress_bar()
            try:
                im_processor.render()
                im_processor.render_preview()
                self._add_progress_to_progress_bar()
            except Exception as exc:
                self._logger.debug(str(exc.args))
        self.progress_bar.hide()
