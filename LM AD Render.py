from classes.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from sys import exit
from loguru import logger as log


def start_program(app: QApplication):
    log.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='10 MB', compression='zip')
    win = MainWindow(log)
    win.setGeometry(1000, 400, 930, 550)
    win.setWindowTitle("LM Ad Render")
    win.show()
    exit(app.exec_())


def dependencies_installed(app: QApplication):
    import subprocess
    try:
        output_ffmpeg = subprocess.check_output(["ffmpeg", "-version"])
        output_imagemagick = subprocess.check_output(["magick", "-version"])
        return True
    except WindowsError:
        return False


def show_missing_dependencies_window(app):
    from classes.missing_dependencies_window import MissingDependenciesWindow
    window = MissingDependenciesWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    try:
        app = QApplication([])
        if dependencies_installed(app):
            start_program(app)
        else:
            show_missing_dependencies_window(app)
    except Exception as e:
        log.debug(e)
        input()
