import subprocess
import os
import pathlib
from loguru import logger

"""
Python API for ImageMagick
"""

output = subprocess.check_output(["magick", "-version"])
print(output)

