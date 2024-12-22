from PySide6.QtWidgets import QDialog, QMessageBox, QComboBox, QFormLayout, QLineEdit, QPushButton, QCheckBox
from datebase import Employee, Training, Employee_training
from PySide6.QtGui import QIcon

class AddTrainingDialog(QDialog):
    def __init__(self, session, employee_id=None, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon('icon.ico'))  # Устанавливаем иконку окна
        self.session = session
        self.employee_id = employee_id
        self.setWindowTitle("Добавление обучения сотрудника")
        self.layout = QFormLayout(self)

        # Список сотрудников
        self.employee_combo = QComboBox()
        self.load_employees()  # Заполнение комбобокса сотрудников
        self.layout.addRow("Сотрудник", self.employee_combo)

        # Список обучения
        self.training_combo = QComboBox()
        self.load_trainings()  # Заполнение комбобокса обучения
        self.layout.addRow("Обучение", self.training_combo)

        # Статус завершенности обучения
        self.training_completed = QCheckBox("Обучение завершено")
        self.layout.addRow(self.training_completed)

        # Номер документа
        self.document_number_input = QLineEdit()
        self.layout.addRow("Номер документа", self.document_number_input)

        # Кнопки
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.save_training)
        self.layout.addWidget(self.btn_save)

    def load_employees(self):
        """Загрузка сотрудников в комбобокс."""
        employees = self.session.query(Employee).filter(Employee.статус == False).all()
        for emp in employees:
            self.employee_combo.addItem(f"{emp.фамилия} {emp.имя} {emp.отчество}", emp.id)

    def load_trainings(self):
        """Загрузка обучения в комбобокс."""
        trainings = self.session.query(Training).all()
        for training in trainings:
            self.training_combo.addItem(training.название, training.id)

    def save_training(self):
        """Сохранение данных об обучении в базе данных."""
        employee_id = self.employee_combo.currentData()  # Получаем ID выбранного сотрудника
        training_id = self.training_combo.currentData()  # Получаем ID выбранного обучения
        training_completed = self.training_completed.isChecked()  # Получаем статус завершенности
        document_number = self.document_number_input.text()  # Получаем номер документа

        # Создание новой записи об обучении
        new_training = Employee_training(
            id_сотрудник=employee_id,
            id_обучение=training_id,
            обучение_пройдено=training_completed,
            номер_документа=document_number
        )

        # Добавление записи в сессию и коммит
        self.session.add(new_training)
        self.session.commit()
        
        # Показ сообщения об успешном добавлении
        QMessageBox.information(self, "Успех", "Данные об обучении успешно добавлены.")
        self.accept()  # Закрытие окна диалога
