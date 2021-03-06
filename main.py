from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from ui.mainwindow import Ui_MainWindow as MainWindow
from lab_1 import Lab_1
from lab_2 import Lab_2
from lab_3 import Lab_3
from lab_4 import Lab_4
from lab_5 import Lab_5
from lab_6 import Lab_6


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui: MainWindow = MainWindow()
        self.ui.setupUi(self)
        # self.ui.verticalLayout.addWidget(Lab_1(self.ui.centralwidget))
        self.ui.tabWidget.addTab(Lab_1(self.ui.tabWidget), 'Лабораторная 1')
        self.ui.tabWidget.addTab(Lab_2(self.ui.tabWidget), 'Лабораторная 2')
        self.ui.tabWidget.addTab(Lab_3(self.ui.tabWidget), 'Лабораторная 3')
        self.ui.tabWidget.addTab(Lab_4(self.ui.tabWidget), 'Лабораторная 4')
        self.ui.tabWidget.addTab(Lab_5(self.ui.tabWidget), 'Лабораторная 5')
        self.ui.tabWidget.addTab(Lab_6(self.ui.tabWidget), 'Лабораторная 6')
        self.ui.tabWidget.setCurrentIndex(6-1)
        self.ui.tabWidget.setCurrentIndex(1-1)
        self.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.ui.tabWidget.currentChanged.connect(
                lambda: self.resize(self.minimumSize())
            )

    def keyPressEvent(self, e: Qt.QKeyEvent):
        if e.key() == Qt.Qt.Key_Escape:
            self.close()


class App():
    def exec(self) -> int:
        app = Qt.QApplication([])
        app.setStyle('Fusion')
        window = Window()
        window.show()
        return app.exec()


def main():
    App().exec()


if __name__ == "__main__":
    main()
