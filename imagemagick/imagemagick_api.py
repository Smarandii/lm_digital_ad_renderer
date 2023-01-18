from __init__ import os, subprocess


class RenderOptions:
    def __init__(self, input_file_options, output_file_options, directory):
        self.input_file_options = input_file_options
        self.output_file_options = output_file_options
        self.directory = directory


class ImageMagickProcessor:
    def __init__(self, input_file, output_file, render_options: RenderOptions):
        self.input_file = input_file
        self.output_file = output_file
        self.render_options = render_options

    def delete_first_page_of_tiff(self):
        try:
            os.remove(os.path.join(self.render_options.directory, "0_" + self.output_file))
        except FileNotFoundError:
            pass

    def render(self):
        """
        calls ImageMagick query, for example:
        magick -colorspace cmyk -units pixelsperinch -density 1100 '.\Illustrator 2020.eps' -compress lzw -colorspace cmyk 'tes.tif'
        magick convert tes.tif -compress lzw %d_110ppi.tif

        result of ImageMagick query saved in output_file
        """
        subprocess.call(f"magick {self.render_options.input_file_options} '{self.input_file}' "
                        f"{self.render_options.output_file_options} '{self.output_file}'")
        subprocess.call(f"magick convert {self.output_file} -compress lzw %d_{self.output_file}")