import pathlib
import shutil
import os
import subprocess
from loguru import logger


output = subprocess.check_output(["ffmpeg", "-version"])
print(output)