# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\UI\settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(768, 451)
        Dialog.setStyleSheet("QPushButton{\n"
"height: 36px;\n"
"border: 1px solid;\n"
"border-radius: 4px;\n"
"border-color:  rgba(0, 0, 0, 0.12);\n"
"color: #6200ee;\n"
"font: \"Roboto\";\n"
"font-size: 20px;\n"
"padding: 5px\n"
"}\n"
"QPushButton::hover{\n"
"    background-color: rgb(230, 230, 230);\n"
"}\n"
"QPushButton::pressed{\n"
"    background-color: rgb(179, 179, 179);\n"
"}\n"
"\n"
"QListWidget{\n"
"border: none;\n"
"}\n"
"QLineEdit{\n"
"border: none;\n"
"}\n"
"")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.user_agent_label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.user_agent_label.sizePolicy().hasHeightForWidth())
        self.user_agent_label.setSizePolicy(sizePolicy)
        self.user_agent_label.setObjectName("user_agent_label")
        self.verticalLayout_4.addWidget(self.user_agent_label)
        self.user_agent_line = QtWidgets.QLineEdit(Dialog)
        self.user_agent_line.setObjectName("user_agent_line")
        self.verticalLayout_4.addWidget(self.user_agent_line)
        self.extensions_label = QtWidgets.QLabel(Dialog)
        self.extensions_label.setObjectName("extensions_label")
        self.verticalLayout_4.addWidget(self.extensions_label)
        self.listWidgetExtensions = QtWidgets.QListWidget(Dialog)
        self.listWidgetExtensions.setObjectName("listWidgetExtensions")
        self.verticalLayout_4.addWidget(self.listWidgetExtensions)
        self.passwords_label = QtWidgets.QLabel(Dialog)
        self.passwords_label.setObjectName("passwords_label")
        self.verticalLayout_4.addWidget(self.passwords_label)
        self.passwords_textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.passwords_textBrowser.setObjectName("passwords_textBrowser")
        self.verticalLayout_4.addWidget(self.passwords_textBrowser)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_line_number = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_line_number.sizePolicy().hasHeightForWidth())
        self.label_line_number.setSizePolicy(sizePolicy)
        self.label_line_number.setObjectName("label_line_number")
        self.verticalLayout_2.addWidget(self.label_line_number)
        self.lineEdit_line_number = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_line_number.setObjectName("lineEdit_line_number")
        self.verticalLayout_2.addWidget(self.lineEdit_line_number)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.latitude_label = QtWidgets.QLabel(Dialog)
        self.latitude_label.setObjectName("latitude_label")
        self.verticalLayout_9.addWidget(self.latitude_label)
        self.latitude_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.latitude_lineEdit.setObjectName("latitude_lineEdit")
        self.verticalLayout_9.addWidget(self.latitude_lineEdit)
        self.horizontalLayout_5.addLayout(self.verticalLayout_9)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.longitude_label = QtWidgets.QLabel(Dialog)
        self.longitude_label.setObjectName("longitude_label")
        self.verticalLayout_8.addWidget(self.longitude_label)
        self.longitude_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.longitude_lineEdit.setObjectName("longitude_lineEdit")
        self.verticalLayout_8.addWidget(self.longitude_lineEdit)
        self.horizontalLayout_5.addLayout(self.verticalLayout_8)
        self.verticalLayout_7.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addLayout(self.verticalLayout_7)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.proxy_id_label = QtWidgets.QLabel(Dialog)
        self.proxy_id_label.setObjectName("proxy_id_label")
        self.verticalLayout_5.addWidget(self.proxy_id_label)
        self.proxy_id_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.proxy_id_lineEdit.setObjectName("proxy_id_lineEdit")
        self.verticalLayout_5.addWidget(self.proxy_id_lineEdit)
        self.horizontalLayout_3.addLayout(self.verticalLayout_5)
        self.search_clean_ip_pushButton = QtWidgets.QPushButton(Dialog)
        self.search_clean_ip_pushButton.setEnabled(True)
        self.search_clean_ip_pushButton.setObjectName("search_clean_ip_pushButton")
        self.horizontalLayout_3.addWidget(self.search_clean_ip_pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.new_tab_label = QtWidgets.QLabel(Dialog)
        self.new_tab_label.setObjectName("new_tab_label")
        self.verticalLayout_6.addWidget(self.new_tab_label)
        self.new_tab_lineEdit = QtWidgets.QLineEdit(Dialog)
        self.new_tab_lineEdit.setObjectName("new_tab_lineEdit")
        self.verticalLayout_6.addWidget(self.new_tab_lineEdit)
        self.horizontalLayout_4.addLayout(self.verticalLayout_6)
        self.new_tab_pushButton = QtWidgets.QPushButton(Dialog)
        self.new_tab_pushButton.setMinimumSize(QtCore.QSize(141, 0))
        self.new_tab_pushButton.setObjectName("new_tab_pushButton")
        self.horizontalLayout_4.addWidget(self.new_tab_pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Settings"))
        self.user_agent_label.setText(_translate("Dialog", "User agent"))
        self.extensions_label.setText(_translate("Dialog", "Extensions"))
        self.passwords_label.setText(_translate("Dialog", "Passwords"))
        self.label_line_number.setText(_translate("Dialog", "Line number (only for autoreg)"))
        self.latitude_label.setText(_translate("Dialog", "Latitude"))
        self.longitude_label.setText(_translate("Dialog", "Longitude"))
        self.proxy_id_label.setText(_translate("Dialog", "Proxy id"))
        self.search_clean_ip_pushButton.setText(_translate("Dialog", "Search clean IP"))
        self.new_tab_label.setText(_translate("Dialog", "Open new tab with url"))
        self.new_tab_pushButton.setText(_translate("Dialog", "OPEN"))
