import pathlib

from imagemagick import os, subprocess, logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')


class RenderOptions:
    def __init__(self, input_file_options, output_file_options, directory: pathlib.Path, full_size, size_name):
        self.input_file_options = input_file_options
        self.output_file_options = output_file_options
        self.directory = directory
        self.full_size = full_size
        self.output_directory = self.directory.joinpath("Принт")
        self.output_file_name = f"{self.get_density() // 10}ppi lzw.tif"
        self.preview_file_name = size_name + ' — preview.png'
        self.preview_input_options = f"-colorspace rgb -density " \
                                     f"{self.get_density() // 2}"

    def get_density(self):
        return int(self.input_file_options.split(' ')[-1])


class ImageMagickProcessor:
    def __init__(self, input_file_path, render_options: RenderOptions):
        self.input_file_path = input_file_path
        self.render_options = render_options
        self.output_file_path = os.path.join(self.render_options.directory,
                                             "Принт",
                                             self.render_options.output_file_name)
        self.output_preview_path_1 = os.path.join(self.render_options.directory,
                                                  self.render_options.preview_file_name)
        self.output_preview_path_2 = os.path.join(self.render_options.directory.parent,
                                                  self.render_options.preview_file_name)

    def render(self):
        """
        calls ImageMagick query, for example:
        magick -colorspace cmyk -units pixelsperinch -density 1100 '.\Illustrator 2020.eps' -compress lzw -colorspace cmyk 'tes.tif'
        magick convert tes.tif -compress lzw %d_110ppi.tif

        result of ImageMagick query saved in output_file
        """
        logger.debug(f"EXECUTE: magick {self.render_options.input_file_options} \"{self.input_file_path}[0]\" "
                        f"{self.render_options.output_file_options} \"{self.output_file_path}\"")
        subprocess.call(f"magick {self.render_options.input_file_options} \"{self.input_file_path}[0]\" "
                        f"{self.render_options.output_file_options} \"{self.output_file_path}\"")

    def render_preview(self):
        """
        calls ImageMagick query, for example:
        magick -colorspace cmyk -units pixelsperinch -density 900 '.\Illustrator 2020.eps' 'preview.jpg'

        result of ImageMagick query saved in size directory as preview
        :return:
        """
        logger.debug(f"EXECUTE: magick {self.render_options.preview_input_options} \"{self.input_file_path}[0]\" "
                        f"\"{self.output_preview_path_1}\"")
        subprocess.call(f"magick {self.render_options.preview_input_options} \"{self.input_file_path}[0]\" "
                        f"\"{self.output_preview_path_1}\"")
        logger.debug(f"EXECUTE: magick {self.render_options.preview_input_options} \"{self.input_file_path}[0]\" "
                     f"\"{self.output_preview_path_2}\"")
        subprocess.call(f"magick {self.render_options.preview_input_options} \"{self.input_file_path}[0]\" "
                        f"\"{self.output_preview_path_2}\"")