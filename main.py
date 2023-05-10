from enum import Enum
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from ui_mainwindow import Ui_MainWindow


class Application(QMainWindow):
    class Method(Enum):
        IC = 0
        AUTO_CORRELATION = 1
        KASIKI = 2

    class Action(Enum):
        ANALYSE = 0
        DECRYPT = 1

    def __init__(self):
        super(Application, self).__init__()
        self.before = ()
        self.replace = {}
        self.is_decrypted = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.data = None
        self.frequency = {}
        self.text_frequency = {}
        self.ru = "абвгдеёжзийклмнопрстуфхцчщшъыьэюя"
        self.en = "abcdefghijklmnopqrstuvwxyz"
        self.num = "0123456789"
        self.abc = [self.ru, self.en]

        self.ui.action_open_cipher.triggered.connect(self.open_text)
        self.ui.action_save_cipher.triggered.connect(self.save_text)

    def open_text(self):
        file_name = QFileDialog.getOpenFileName(self, "Открыть файл", ".", "All Files (*)")
        if file_name[0]:
            self.is_decrypted = False
            with open(file_name[0], "r", encoding="utf-8") as file:
                self.data = file.read()
                self.ui.plain_text.setText(self.data)
        else:
            QMessageBox.information(self, "Ошибка", "Файл не выбран")

    def save_text(self):
        file_name = QFileDialog.getSaveFileName(self, "Сохранить файл", ".", "All Files (*)")
        if file_name[0]:
            with open(file_name[0], "w") as file:
                file.write(self.ui.cipher_text.toPlainText())
        else:
            QMessageBox.information(self, "Ошибка", "Файл не выбран")


if __name__ == "__main__":
    app = QApplication()
    window = Application()
    app.exec()
