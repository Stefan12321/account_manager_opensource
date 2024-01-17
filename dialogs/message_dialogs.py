from PyQt5.QtWidgets import QMessageBox


def open_error_dialog(message: str):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText(message)
    error_dialog.setWindowTitle("Error")
    error_dialog.show()
    error_dialog.exec()


def open_information_dialog(message: str):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Information)
    error_dialog.setText(message)
    error_dialog.setWindowTitle("Info")
    error_dialog.show()
    error_dialog.exec()
