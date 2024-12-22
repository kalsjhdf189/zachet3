from PySide6.QtWidgets import  QApplication
from main_window import MainWindow

app = QApplication([]) # Создаем объект приложения QApplication
window = MainWindow() # Создаем объект MainWindow
window.show() # Отображаем окно приложения
app.exec() # Запускаем цикл событий приложения