import pathlib
import shutil
import argparse
import os
import subprocess
from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 KB', compression='zip')


class FfmpegGenerator:
    def __init__(self, video_extension, video_duration, input_file_path):

        self.jpg_path = pathlib.Path(input_file_path)
        self.video_extension = video_extension
        self.video_duration = video_duration
        self.DIR_PATH = pathlib.Path(self.jpg_path.parent)
        self.name = self.jpg_path.__str__().split("\\")[-1]
        self.name_without_extension = self.jpg_path.__str__().split("\\")[-1].replace(".jpg", "")
        self.video_name = self.name_without_extension + "." + self.video_extension
        if "Gallery" in input_file_path:
            self.gallery = True
            self.name_with_preview = self.name_without_extension + " — Gallery — preview.jpg"
        else:
            self.name_with_preview = self.name_without_extension + " — preview.jpg"
        self.video_path = os.path.join(self.DIR_PATH.parent, "Видео", self.video_name)
        if "fade" in input_file_path:
            self.fade_in_fade_out = True

    def __str__(self):
        return self.name, self.jpg_path

    def delete_old_preview(self, directory):
        try:
            os.remove(os.path.join(directory, self.name_with_preview))
        except FileNotFoundError:
            pass

    def create_preview(self):
        logger.debug(f"COPY: {self.jpg_path} to the {self.DIR_PATH.parent.__str__()}")
        self.delete_old_preview(self.DIR_PATH.parent)
        shutil.copy(self.jpg_path, self.DIR_PATH.parent)

        logger.debug(f"RENAME: {os.path.join(self.DIR_PATH.parent, self.name).__str__()} to the "
                     f"{os.path.join(self.DIR_PATH.parent, self.name_with_preview)}")
        os.rename(os.path.join(self.DIR_PATH.parent, self.name),
                  os.path.join(self.DIR_PATH.parent, self.name_with_preview))

        logger.debug(f"COPY: {self.jpg_path} to the {self.DIR_PATH.parent.parent.__str__()}")
        self.delete_old_preview(self.DIR_PATH.parent.parent)
        shutil.copy(self.jpg_path, self.DIR_PATH.parent.parent)

        logger.debug(f"RENAME: {os.path.join(self.DIR_PATH.parent.parent, self.name).__str__()} to the "
                     f"{os.path.join(self.DIR_PATH.parent.parent, self.name_with_preview)}")
        os.rename(os.path.join(self.DIR_PATH.parent.parent, self.name),
                  os.path.join(self.DIR_PATH.parent.parent, self.name_with_preview))

    def render_video(self):
        # Old way to use ffmpeg:
        # os.system(f'start /wait cmd /c "ffmpeg -y -loop 1 -i "{self.jpg_path}" -t {self.video_duration}
        # -pix_fmt yuv420p "{self.video_path}""')

        logger.debug(f"Executing...\n"
                     f"ffmpeg \n"
                     f"-y -loop 1 \n"
                     f"-i {self.jpg_path} \n"
                     f"-t {self.video_duration} \n"
                     f"-pix_fmt yuv420p {self.video_path} \n")
        subprocess.call(
            f"ffmpeg -y -loop 1 -i \"{self.jpg_path}\" -t {self.video_duration} -pix_fmt yuv420p \"{self.video_path}\"")
        if self.fade_in_fade_out:
            f_in_fname = self.video_path.replace('.mp4', '_fade_in.mp4')
            f_in_f_out_fname = f_in_fname.replace('_fade_in.mp4', '_fade_in_fade_out.mp4')
            subprocess.call(f"ffmpeg -y -i \"{self.video_path}\" -vf \"fade=t=in:st=0:d=1\" \"{f_in_fname}\"")
            subprocess.call(f"ffmpeg -y -i \"{f_in_fname}\" -vf \"fade=t=out:st=4:d=1\" \"{f_in_f_out_fname}\"")
            os.remove(f_in_fname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Grinding images helper"
    )

    parser.add_argument(
        "-i", type=str,
        help="Input file path"
    )

    parser.add_argument(
        "-e", type=str,
        help="The extension of the video to create without dot, example — (avi, mp4, etc.)"
    )
    parser.add_argument(
        "-t", type=str,
        help="The duration of the video to create in secs, example — (5, 10, etc.)"
    )
    args = parser.parse_args()

    if args.e is None:
        args.e = "mp4"
    if args.t is None:
        args.t = "5"
    size = FfmpegGenerator(video_extension=args.e, video_duration=args.t, input_file_path=args.i)

    try:
        size.create_preview()
        size.render_video()
    except FileExistsError as e:
        logger.debug("Операция создания превью прервана, так как файл preview уже существует!")
        os.remove(os.path.join(size.DIR_PATH.parent, size.name))
        size.render_video()
    except Exception as e:
        print(e)
