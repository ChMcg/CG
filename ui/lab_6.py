# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inelos/projects/KG/watchdog/../ui/lab_6.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(520, 551)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.moc_drawArea = QtWidgets.QOpenGLWidget(Form)
        self.moc_drawArea.setMinimumSize(QtCore.QSize(500, 500))
        self.moc_drawArea.setMaximumSize(QtCore.QSize(500, 500))
        self.moc_drawArea.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.moc_drawArea.setObjectName("moc_drawArea")
        self.horizontalLayout.addWidget(self.moc_drawArea)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.pause = QtWidgets.QPushButton(Form)
        self.pause.setObjectName("pause")
        self.verticalLayout.addWidget(self.pause)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pause.setText(_translate("Form", "Запуск"))