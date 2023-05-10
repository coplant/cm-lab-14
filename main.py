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
        self.ru_ic = 0.0553
        self.en_ic = 0.0644
        self.ic = [self.ru_ic, self.en_ic]
        self.BORDER = 0.95

        self.ui.combo_language.view().pressed.connect(lambda x: self.handle_language(x.row()))
        self.ui.btn_analyse.clicked.connect(self.analyse_text)
        self.ui.btn_decrypt.clicked.connect(self.decrypt_text)
        self.ui.action_open.triggered.connect(self.open_text)
        self.ui.action_save.triggered.connect(self.save_text)

    def handle_language(self, x):
        self.ui.line_abc.setText(self.abc[x])

    def index_coincidence(self, message):
        current_abc = self.ui.line_abc.text()
        letters_count, length = {char: message.count(char) for char in current_abc}, len(message)
        if length == 1:
            return 0
        return sum([dict.get(letters_count, num, 0) * (dict.get(letters_count, num, 0) - 1) /
                    (length * (length - 1)) for num in current_abc])

    def get_key(self):
        ...

    def get_key_length(self):
        if self.ui.combo_method.currentIndex() == self.Method.IC.value:
            current_ic = self.ui.combo_language.currentIndex()
            current_abc = self.ui.line_abc.text()
            ciphertext = self.ui.plain_text.toPlainText().lower()
            result = {}
            for i in range(1, len(current_abc)):
                message = ''.join([ciphertext[k] for k in range(0, len(ciphertext), i)])
                result[i] = self.index_coincidence(message)
            key_lengths = [(a, b) for a, b in result.items() if b > (self.ic[current_ic] * self.BORDER)]
            prob_length = min(key_lengths, key=lambda x: x[0])
            self.ui.spin_key_len.setValue(prob_length[0])
        elif self.ui.combo_method.currentIndex() == self.Method.AUTO_CORRELATION.value:
            print("AUTO_CORRELATION method")
        elif self.ui.combo_method.currentIndex() == self.Method.KASIKI.value:
            print("KASIKI method")

    def analyse_text(self):
        if not self.ui.plain_text.toPlainText():
            return QMessageBox.information(self, "Ошибка", "Неверная длина зашифрованного текста")
        if not self.ui.line_abc.text():
            return QMessageBox.information(self, "Ошибка", "Неверная длина алфавита")
        self.get_key_length()
        self.get_key()

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
