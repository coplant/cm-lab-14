import math
from enum import Enum

from PySide6 import QtCharts, QtCore
from PySide6.QtGui import QPainter, QBrush, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem
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
        self.is_decrypted = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.data = None
        self.frequency = {}
        self.text_frequency = {}
        self.ru = "абвгдеёжзийклмнопрстуфхцчщшъыьэюя"
        self.en = "abcdefghijklmnopqrstuvwxyz"
        self.ru_freq = {
            "а": 0.062, "б": 0.014, "в": 0.038, "г": 0.013, "д": 0.025,
            "е": 0.072, "ё": 0.00013, "ж": 0.007, "з": 0.016, "и": 0.062,
            "й": 0.010, "к": 0.028, "л": 0.035, "м": 0.026, "н": 0.053,
            "о": 0.090, "п": 0.023, "р": 0.040, "с": 0.045, "т": 0.053,
            "у": 0.021, "ф": 0.002, "х": 0.009, "ц": 0.004, "ч": 0.012,
            "ш": 0.006, "щ": 0.003, "ъ": 0.014, "ы": 0.016, "ь": 0.014,
            "э": 0.003, "ю": 0.006, "я": 0.018, " ": 0.175
        }
        self.en_freq = {
            "a": 0.0796, "b": 0.0160, "c": 0.0284, "d": 0.0401, "e": 0.1286,
            "f": 0.0262, "g": 0.0199, "h": 0.0539, "i": 0.0777, "j": 0.0016,
            "k": 0.0041, "l": 0.0351, "m": 0.0243, "n": 0.0751, "o": 0.0662,
            "p": 0.0181, "q": 0.0017, "r": 0.0683, "s": 0.0662, "t": 0.0972,
            "u": 0.0248, "v": 0.0115, "w": 0.0180, "x": 0.0017, "y": 0.0152,
            "z": 0.0005
        }
        self.freq_abc = [self.ru_freq, self.en_freq]
        self.num = "0123456789"
        self.abc = [self.ru, self.en]
        self.ru_ic = 0.0553
        self.en_ic = 0.0644
        self.ic = [self.ru_ic, self.en_ic]
        self.BORDER = 0.95
        self.MAX_POSSIBLE_LENGTH = 50

        self.ui.combo_language.view().pressed.connect(lambda x: self.handle_language(x.row()))
        self.ui.btn_analyse.clicked.connect(self.analyse_text)
        self.ui.btn_decrypt.clicked.connect(self.decrypt_text)
        self.ui.action_open.triggered.connect(self.open_text)
        self.ui.action_save.triggered.connect(self.save_text)

    def handle_language(self, x):
        ru_abc = {k: v for k, v in sorted(self.ru_freq.items(), key=lambda item: item[1], reverse=True)}
        en_abc = {k: v for k, v in sorted(self.en_freq.items(), key=lambda item: item[1], reverse=True)}
        if x == self.Language.RUSSIAN.value:
            if not self.frequency or self.frequency == en_abc:
                self.frequency = ru_abc
        elif x == self.Language.ENGLISH.value:
            if not self.frequency or self.frequency == ru_abc:
                self.frequency = en_abc
        self.ui.line_abc.setText(self.abc[x])

    def index_coincidence(self, message):
        current_abc = self.ui.line_abc.text()
        letters_count, length = {char: message.count(char) for char in current_abc}, len(message)
        if length == 1:
            return 0
        return sum([dict.get(letters_count, num, 0) * (dict.get(letters_count, num, 0) - 1) /
                    (length * (length - 1)) for num in current_abc])

    def set_text_frequency(self, choice):
        self.ui.table_stats.setRowCount(len(self.freq_abc[choice]))
        index = 0
        for i in range(len(self.text_frequency.items())):
            text_frequency = list(self.text_frequency.items())
            if text_frequency[i][0].lower() in self.freq_abc[choice].keys():
                letter = text_frequency[i][0]
                count, frequency = text_frequency[i][1]
                self.ui.table_stats.setItem(index, 0, QTableWidgetItem(letter.upper()))
                self.ui.table_stats.setItem(index, 1, QTableWidgetItem(f"{count}"))
                self.ui.table_stats.setItem(index, 2, QTableWidgetItem(f"{frequency * 100:g}"))
                self.ui.table_stats.setItem(index, 3,
                                            QTableWidgetItem(f"{self.freq_abc[choice].get(letter.lower()) * 100:g}"))
                index += 1
        self.ui.table_stats.resizeColumnsToContents()

    def draw_chart(self, choice):
        # построение гистограммы
        if not self.frequency:
            return QMessageBox.information(self, "Ошибка", "Некорректные значения частот")
        layout = self.ui.horizontalLayout.takeAt(0)
        if layout:
            layout.widget().deleteLater()
        self.setFixedHeight(650)
        axis_x = QtCharts.QBarCategoryAxis()
        axis_y = QtCharts.QValueAxis()
        series = QtCharts.QBarSeries()
        practical = QtCharts.QBarSet("Текущее")
        practical.setColor(QColor(163, 74, 236, 255))
        practical.setBorderColor(QColor(255, 255, 255, 255))
        theory = QtCharts.QBarSet("Ожидаемое")
        theory.setColor(QColor(98, 235, 56, 255))
        for i in self.abc[choice]:
            axis_x.append(i.upper())
            practical.append(self.text_frequency.get(i)[1])
            theory.append(self.frequency.get(i))
        series.append(practical)
        series.append(theory)
        chart = QtCharts.QChart()
        chart.addAxis(axis_x, QtCore.Qt.AlignmentFlag.AlignBottom)
        chart.addSeries(series)
        max_value_freq = max(self.frequency.items(), key=lambda x: x[1])[1]
        max_value_text = max(self.text_frequency.items(), key=lambda x: x[1][1])[1][1]
        axis_y.setRange(0, max(max_value_freq, max_value_text))
        chart.addAxis(axis_y, QtCore.Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        chart_view = QtCharts.QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.chart().setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))
        self.ui.horizontalLayout.addWidget(chart_view)

    def get_key(self):
        length = self.ui.spin_key_len.value()
        current_abc = self.ui.line_abc.text()
        ciphertext = self.ui.plain_text.toPlainText().lower()
        for char in ciphertext:
            if char not in current_abc:
                ciphertext = ciphertext.replace(char, "")
        current_abc = self.ui.line_abc.text()
        keys = []
        for k in range(length):
            temp = ""
            j = k
            while j < len(ciphertext):
                temp += ciphertext[j]
                j += length
            keys.append(temp)
        result = ""
        for i in range(length):
            times = {current_abc.index(keys[i][j]): keys[i].count(keys[i][j]) for j in range(len(keys[i]))}
            max_index = max(times.items(), key=lambda x: x[1])[0]
            # для русского и английского языка
            default = max(current_abc.lower().find("о"), current_abc.lower().find("e"))
            if current_abc.find(" ") >= 0:
                default = current_abc.find(" ")
            result += current_abc[((max_index - default) + len(current_abc)) % len(current_abc)]
        self.ui.line_key.setText(result)

    def get_key_length(self):
        current_abc = self.ui.line_abc.text()
        ciphertext = self.ui.plain_text.toPlainText().lower()
        current_ic = self.ui.combo_language.currentIndex()
        for char in ciphertext:
            if char not in current_abc:
                ciphertext = ciphertext.replace(char, "")
        if self.ui.combo_method.currentIndex() == self.Method.IC.value:
            result = {}
            for i in range(1, len(current_abc)):
                message = ''.join([ciphertext[k] for k in range(0, len(ciphertext), i)])
                result[i] = self.index_coincidence(message)
            key_lengths = [(a, b) for a, b in result.items() if b > (self.ic[current_ic] * self.BORDER)]
            prob_length = min(key_lengths, key=lambda x: x[0])
            self.ui.spin_key_len.setValue(prob_length[0])
            return
        elif self.ui.combo_method.currentIndex() == self.Method.AUTO_CORRELATION.value:
            for i in range(1, self.MAX_POSSIBLE_LENGTH):
                text = ciphertext[i:] + ciphertext[:i]
                coincidences = 0
                for j in range(len(ciphertext)):
                    if ciphertext[j] == text[j]:
                        coincidences += 1
                index = coincidences / len(ciphertext)
                if index > (self.ic[current_ic] * self.BORDER):
                    self.ui.spin_key_len.setValue(i)
                    return
        elif self.ui.combo_method.currentIndex() == self.Method.KASIKI.value:
            if len(ciphertext) < 10:
                return QMessageBox.information(self, "Ошибка", "Текст слишком короткий")
            checked = ""
            possible_lengths = []
            for i in range(int(len(ciphertext) / 3 - 1)):
                substring = ciphertext[i:i + 3]
                if substring not in checked:
                    times = 0
                    j = 0
                    while ciphertext.find(substring, j) != -1:
                        j = ciphertext.find(substring, j) + 1
                        times += 1
                    if times >= 3:
                        checked += substring + " "
                        positions_difference = []
                        previous = ciphertext.find(substring)
                        j = previous + 1
                        while ciphertext.find(substring, j) != -1:
                            current_index = ciphertext.find(substring, j)
                            positions_difference.append(current_index - 1)
                            previous = current_index
                            j = current_index + 1
                        current_GCD = positions_difference[0]
                        for k in range(1, len(positions_difference)):
                            current_GCD = math.gcd(current_GCD, positions_difference[k])
                        if current_GCD > 1:
                            possible_lengths.append(current_GCD)
            if len(possible_lengths):
                possible_lengths.sort()
                i = 0
                possibility = {}
                while i < len(possible_lengths) and possible_lengths[i] < self.MAX_POSSIBLE_LENGTH:
                    possibility[possible_lengths[i]] = possibility.get(possible_lengths[i], 0) + 1
                    i += 1
                for i in possibility.keys():
                    possibility[i] *= i
                max_index = max(possibility.items(), key=lambda x: x[1])[0]
                self.ui.spin_key_len.setValue(max_index)
                return

    def analyse_text(self):
        if not self.ui.plain_text.toPlainText():
            return QMessageBox.information(self, "Ошибка", "Неверная длина зашифрованного текста")
        if not self.ui.line_abc.text():
            return QMessageBox.information(self, "Ошибка", "Неверная длина алфавита")
        self.get_key_length()
        self.get_key()

    def get_extended_key(self, data):
        extended_key = []
        key = self.ui.line_key.text()
        index = 0
        for char in data:
            is_found = False
            for abc in self.abc:
                if char.lower() in abc:
                    extended_key.append(int(abc.index(key[index % len(key)].lower())))
                    index += 1
                    is_found = True
            if not is_found:
                extended_key.append(0)
        return extended_key

    def decrypt_text(self):
        data = self.ui.plain_text.toPlainText().lower()
        extended_key = self.get_extended_key(data)
        text = ''
        for i, char in enumerate(data):
            is_found = False
            for abc in self.abc:
                if char.lower() in abc:
                    to_add = abc[
                        (len(abc) + abc.index(char.lower()) - self.Action.DECRYPT.value * extended_key[i]) % len(abc)]
                    text += to_add.upper() if char.isupper() else to_add.lower()
                    is_found = True
            if not is_found:
                text += char
        for abc in self.abc:
            for char in abc:
                self.text_frequency[char] = (text.count(char), text.count(char) / len(text))
        self.text_frequency = {k: v for k, v in
                               sorted(self.text_frequency.items(), key=lambda item: item[1][1], reverse=True)}
        self.ui.cipher_text.setText(text)
        self.set_text_frequency(self.ui.combo_language.currentIndex())
        self.draw_chart(self.ui.combo_language.currentIndex())

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
