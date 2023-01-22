from classes.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from sys import exit
from loguru import logger as log


def start_program(app: QApplication):
    log.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')
    win = MainWindow(log)
    win.setGeometry(1000, 400, 800, 200)
    win.setWindowTitle("LM Ad Render")
    win.show()
    exit(app.exec_())


def dependencies_installed(app: QApplication):
    import subprocess
    from classes.missing_dependencies_window import MissingDependenciesWindow
    try:
        output_ffmpeg = subprocess.check_output(["ffmpeg", "-version"])
        output_imagemagick = subprocess.check_output(["magick", "-version"])
        return True
    except WindowsError:
        window = MissingDependenciesWindow()
        window.show()
        app.exec_()
        return False


if __name__ == "__main__":
    try:
        app = QApplication([])
        if dependencies_installed(app):
            start_program(app)
    except Exception as e:
        log.debug(e)
        input()
