from classes import QMainWindow, uic, QUrl, QtGui, QtWidgets, pathlib


class MissingDependenciesWindow(QMainWindow):
    def __init__(self, ffmpeg_installation_link="https://github.com/BtbN/FFmpeg-Builds/releases",
                 imagemagick_installation_link="https://imagemagick.org/script/download.php#windows"):
        super(MissingDependenciesWindow, self).__init__()

        uic.loadUi(f"{pathlib.Path('').parent.absolute()}\\ui\\MissingDependenciesWindow.ui", self)
        self._ffmpeg_installation_link = ffmpeg_installation_link
        self._imagemagick_installation_link = imagemagick_installation_link
        self.pushButton_install_ffmpeg.clicked.connect(self.ffmpeg_install_link_open)
        self.pushButton_install_imagemagick.clicked.connect(self.imagemagick_install_link_open)

    def ffmpeg_install_link_open(self):
        url = QUrl(self._ffmpeg_installation_link)
        QtGui.QDesktopServices.openUrl(url)

    def imagemagick_install_link_open(self):
        url = QUrl(self._imagemagick_installation_link)
        QtGui.QDesktopServices.openUrl(url)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MissingDependenciesWindow()
    window.show()
    app.exec_()
