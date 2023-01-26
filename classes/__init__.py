from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import QUrl
from PIL import Image
from PyQt5 import QtWidgets
from PyQt5.QtCore import QPoint

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from ffmpeg.ffmpeg_api import FfmpegProcessor
from imagemagick.imagemagick_api import RenderOptions, ImageMagickProcessor
import pathlib
import shutil

from os import path, mkdir, walk