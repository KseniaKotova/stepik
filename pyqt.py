import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QVBoxLayout, QWidget, QComboBox, QFileDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
import os
import pandas as pd
from datetime import datetime
from pathlib import Path


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер файлов")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon("image.png"))

        self.generate_test_files()

        layout = QVBoxLayout()

        self.button_download_file = QPushButton("Загрузить файл", self)
        self.button_to_convert = QPushButton("Конвертировать", self)
        self.button_to_convert.setEnabled(False)
        self.button_save_file = QPushButton("Сохранить как...", self)
        self.button_save_file.setEnabled(False)
        
        self.choose_convert = QComboBox()
        self.choose_convert.addItem("")
        self.choose_convert.addItem("CSV -> JSON")
        self.choose_convert.addItem("JSON -> CSV")
        self.choose_convert.setEnabled(False)

        self.file_path_label = QLabel("Путь к файлу: ", self)
        self.is_empty_file = QLabel("", self)
        self.success_convert = QLabel("", self)
        self.type_convert = QLabel("", self)

        self.button_download_file.clicked.connect(self.clicked_to_download)
        self.choose_convert.currentTextChanged.connect(self.choose_combobox)
        self.button_to_convert.clicked.connect(self.convert_file)
        self.button_save_file.clicked.connect(self.save_file)
        
        layout.addWidget(self.button_download_file)
        layout.addWidget(self.choose_convert)
        layout.addWidget(self.button_to_convert)
        layout.addWidget(self.button_save_file)
        layout.addWidget(self.file_path_label)
        layout.addWidget(self.is_empty_file)
        layout.addWidget(self.type_convert)
        layout.addWidget(self.success_convert)
        
        self.setLayout(layout)

    def generate_test_files(self):
        if not os.path.exists("test.csv"):
            with open("test.csv", "w") as f:
                f.write("name,age\nAlice,30\nBob,25")
            print("Создан тестовый файл: test.csv")

        if not os.path.exists("test.json"):
            with open("test.json", "w") as f:
                f.write('[{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]')
            print("Создан тестовый файл: test.json")
    
    def clicked_to_download(self):
        options = QFileDialog.Options()
        try: 
            self.file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "*.json;;*.csv", options=options)
            self.file_path_label.setText(f"Выбран файл: {self.file_path}")
            if self.file_path:
                if os.path.getsize(self.file_path) != 0: 
                    self.is_empty_file.setText(f"")
                    self.choose_convert.setEnabled(True)
                else: 
                    self.is_empty_file.setText(f"Ошибка! Файл пустой.")
                    self.choose_convert.setEnabled(False)
            else:
                self.file_path_label.setText("Отмена выбора файла.")
        except Exception as e:
            self.file_path_label.setText(f"Возникла ошибка при выборе файла: {str(e)}")
    
    def choose_combobox(self):
        current_text = self.choose_convert.currentText()
        if current_text == "":
            return
        
        if (current_text == 'CSV -> JSON' and self.file_path.endswith('.csv')) or (current_text == 'JSON -> CSV' 
            and self.file_path.endswith('.json')):
                self.success_convert.setText('Нажмите кнопку "Конвертировать".')
                self.button_to_convert.setEnabled(True)
        else:
            self.success_convert.setText("Выбрана неверная операция конвертирования!")
            self.button_to_convert.setEnabled(False)

    def convert_file(self):
        try:
            if self.file_path:
                if self.file_path.endswith('.csv'):
                    self.file_conv = self.convert_to_json()
                    self.conv_format = 'json'
                elif self.file_path.endswith('.json'):
                    self.file_conv = self.convert_to_csv()
                    self.conv_format = 'csv'
                self.success_convert.setText('Нажмите кнопку "Сохранить как...".')
                self.button_save_file.setEnabled(True)
            else:
                self.success_convert.setText('Возникла ошибка при конвертации.')
                self.button_save_file.setEnabled(False)
        except Exception as e:
            self.success_convert.setText(f"Возникла ошибка при конвертации: {str(e)}")
    
    def save_file(self):
        if not hasattr(self, 'file_conv') or self.file_conv is None:
            self.success_convert.setText("Ошибка: данные для сохранения отсутствуют!")

        options = QFileDialog.Options()
        try:
            self.save_file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", f"{self.create_file_name(Path(self.file_path).stem, self.conv_format)}", f"(*.{self.conv_format})", options=options)
            if self.save_file_path:
                if self.conv_format == 'json':
                    self.file_conv.to_json(self.create_file_name(Path(self.file_path).stem, self.conv_format), orient='records')
                else:
                    self.file_conv.to_csv(self.create_file_name(Path(self.file_path).stem, self.conv_format), index=False)
                self.success_convert.setText("Файл успешно сохранен!")
                QTimer.singleShot(2000, self.reset_state)
            else:
                self.success_convert.setText("Отмена сохранения.")
        except Exception:
            self.success_convert.setText("Ошибка сохранения.")

    def convert_to_json(self):
        ext = 'json'
        output_file = self.create_file_name(Path(self.file_path).stem, ext)
        csv_file = pd.read_csv(self.file_path)
        self.type_convert.setText(f"Файл успешно конвертирован в JSON: {output_file}")
        return csv_file
    
    def convert_to_csv(self):
        ext = 'csv'
        output_file = self.create_file_name(Path(self.file_path).stem, ext)
        json_file = pd.read_json(self.file_path)
        self.type_convert.setText(f"Файл успешно конвертирован в CSV: {output_file}")
        return json_file
        
    def create_file_name(self, base_name, extension):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{base_name}_{timestamp}.{extension}"

    def reset_state(self):
        self.file_path = None
        self.file_conv = None
        self.conv_format = None
        self.file_path_label.setText("Путь к файлу: ")
        self.is_empty_file.setText("")
        self.success_convert.setText("Выберите новый файл для конвертации.")
        self.type_convert.setText("")
        self.choose_convert.setCurrentText("")
        self.choose_convert.setEnabled(False)
        self.button_to_convert.setEnabled(False)
        self.button_save_file.setEnabled(False)   


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())