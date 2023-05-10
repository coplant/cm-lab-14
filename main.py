from enum import Enum
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from ui_mainwindow import Ui_MainWindow


class Application(QMainWindow):
    class Language(Enum):
        RUSSIAN = 0
        ENGLISH = 1

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

        self.ui.combo_language.view().pressed.connect(lambda x: self.handle_language(x.row()))
        self.ui.btn_analyse.clicked.connect(self.analyse_text)
        self.ui.btn_decrypt.clicked.connect(self.decrypt_text)
        self.ui.action_open.triggered.connect(self.open_text)
        self.ui.action_save.triggered.connect(self.save_text)

    def handle_language(self, x):
        self.ui.line_abc.setText(self.abc[x])

    def analyse_text(self):
        if self.ui.combo_method.currentIndex() == self.Method.IC.value:
            print("IC method")
        elif self.ui.combo_method.currentIndex() == self.Method.AUTO_CORRELATION.value:
            print("AUTO_CORRELATION method")
        elif self.ui.combo_method.currentIndex() == self.Method.KASIKI.value:
            print("KASIKI method")

    def decrypt_text(self):
        print("Not implemented")

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
