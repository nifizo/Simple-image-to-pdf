import sys, os
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QMainWindow, QWidget, QListWidget, QListWidgetItem,
                             QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QHBoxLayout, QVBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PIL import Image

class ImageSorter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image to PDF")
        self.setGeometry(100, 100, 800, 600)
        # Встановлюємо сучасний шрифт більшого розміру для інтерфейсу
        font = QFont("Arial", 10)
        QApplication.instance().setFont(font)
        # Ініціалізуємо UI
        self.setupUI()
    def setupUI(self):
        # Центральний віджет і основний layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        # Верхня панель керування (горизонтальний layout)
        control_layout = QHBoxLayout()
        # Створюємо та налаштовуємо кнопки
        self.openButton = QPushButton("Завантажити зображення")
        self.saveButton = QPushButton("Зберегти у PDF")
        self.openButton.setMinimumHeight(30)
        self.saveButton.setMinimumHeight(30)
        # Напис і випадаючий список для вибору сортування
        sort_label = QLabel("Сортувати за:")
        self.sortCombo = QComboBox()
        self.sortCombo.addItems([
            "Ім'ям файлу",
            "Датою створення",
            "Розміром файлу",
            "Розширенням файлу",
            "Вручну (перетягування)"
        ])
        self.sortCombo.setCurrentIndex(4)  # Встановлюємо режим "Вручну" за замовчуванням
        # Додаємо елементи управління на верхню панель
        control_layout.addWidget(self.openButton)
        control_layout.addWidget(self.saveButton)
        control_layout.addStretch(1)
        control_layout.addWidget(sort_label)
        control_layout.addWidget(self.sortCombo)
        # Додаємо верхню панель до основного layout
        main_layout.addLayout(control_layout)
        # Створюємо та налаштовуємо список зображень
        self.listWidget = QListWidget()
        self.listWidget.setIconSize(QSize(64, 64))  # розмір мініатюр (іконок)
        # Увімкнення перетягування для ручного сортування
        self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
        # Додаємо список зображень до основного layout (з розтягуванням на весь екран)
        main_layout.addWidget(self.listWidget, 1)
        # Підключаємо сигнали до слотів
        self.openButton.clicked.connect(self.open_images)
        self.saveButton.clicked.connect(self.save_pdf)
        self.sortCombo.currentIndexChanged.connect(self.sort_images)
    def open_images(self):
        # Відкриваємо діалог вибору файлів зображень
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Виберіть зображення", "",
            "Зображення (*.png *.jpg *.jpeg *.bmp *.gif);;Усі файли (*)"
        )
        if not file_paths:
            return  # якщо нічого не вибрано, виходимо
        # Додаємо кожне вибране зображення до списку
        for path in file_paths:
            # Отримуємо ім'я файлу з шляху
            file_name = os.path.basename(path)
            item = QListWidgetItem(file_name)
            # Створюємо QPixmap для мініатюри зображення
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                # Масштабуємо зображення до 64x64 збережуючи пропорції
                pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(pixmap))
            # Зберігаємо інформацію про файл у елементі списку для сортування
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            try:
                ctime = os.path.getctime(path)
            except Exception:
                ctime = 0
            ext = os.path.splitext(path)[1].lower()  # розширення файлу (з крапкою)
            item.setData(Qt.UserRole, {"path": path, "size": size, "ctime": ctime, "ext": ext})
            # Додаємо елемент до списку
            self.listWidget.addItem(item)
        # Якщо обрано автоматичне сортування (не "вручну"), відсортувати список одразу
        if self.sortCombo.currentIndex() != 4:
            self.sort_images()  # повторно застосувати поточне сортування
    def save_pdf(self):
        # Якщо список порожній, попереджаємо користувача
        if self.listWidget.count() == 0:
            QMessageBox.warning(self, "Немає зображень", "Спочатку завантажте зображення для збереження у PDF.")
            return
        # Діалог збереження PDF-файлу
        pdf_path, _ = QFileDialog.getSaveFileName(self, "Зберегти PDF", "", "PDF Files (*.pdf)")
        if not pdf_path:
            return  # відмінено користувачем
        # Додаємо розширення .pdf, якщо не вказано
        if not pdf_path.lower().endswith(".pdf"):
            pdf_path += ".pdf"
        # Збираємо усі шляхи зображень у поточному порядку
        image_paths = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            data = item.data(Qt.UserRole)
            if data:
                image_paths.append(data["path"])
            else:
                image_paths.append(item.text())
        # Відкриваємо всі зображення за допомогою Pillow
        try:
            pil_images = []
            for idx, img_path in enumerate(image_paths):
                img = Image.open(img_path)
                # Конвертуємо зображення в RGB для сумісності з PDF
                pil_img = img.convert("RGB")
                pil_images.append(pil_img)
            # Зберігаємо перше зображення як PDF з наступними через append_images
            if pil_images:
                first_image = pil_images[0]
                other_images = pil_images[1:]
                first_image.save(pdf_path, save_all=True, append_images=other_images)
            QMessageBox.information(self, "Готово", f"PDF файл успішно збережено: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти PDF: {e}")
    def sort_images(self):
        # Визначаємо режим сортування за індексом вибору
        mode_index = self.sortCombo.currentIndex()
        # mode_index: 0=Name, 1=Date, 2=Size, 3=Extension, 4=Manual
        if mode_index == 4:
            # Ручне сортування: увімкнути перетягування та не виконувати авто-сортування
            self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
            return
        # Для автоматичного сортування вимикаємо можливість перетягування
        self.listWidget.setDragDropMode(QAbstractItemView.NoDragDrop)
        # Отримуємо всі елементи списку
        items = []
        for i in range(self.listWidget.count()):
            items.append(self.listWidget.item(i))
        # Виконуємо сортування списку згідно обраного критерію
        if mode_index == 0:  # Ім'я файлу
            items.sort(key=lambda x: x.text().lower())
        elif mode_index == 1:  # Дата створення
            items.sort(key=lambda x: x.data(Qt.UserRole)["ctime"])
        elif mode_index == 2:  # Розмір файлу
            items.sort(key=lambda x: x.data(Qt.UserRole)["size"])
        elif mode_index == 3:  # Розширення файлу
            items.sort(key=lambda x: x.data(Qt.UserRole)["ext"])
        # Очищаємо список і додаємо елементи заново у новому порядку
        self.listWidget.clear()
        for item in items:
            self.listWidget.addItem(item)
        # Drag&drop залишається вимкненим в режимі авто-сортування
        # (Якщо потрібно вручну змінити порядок, слід обрати режим "Вручну")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSorter()
    window.show()
    sys.exit(app.exec_())
