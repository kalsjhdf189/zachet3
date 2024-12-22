from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableView, QPushButton, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtGui import QStandardItemModel, QStandardItem
from datebase import Connect, Employee

from AddEmployeeDialog import AddEmployeeWindow
from AddTrainingDialog import AddTrainingDialog
from Report import ReportForm

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сотрудники")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('icon.ico'))  # Устанавливаем иконку окна
        
        self.session = Connect.create_connection()

        # Создаем QTableView
        self.table_view = QTableView()

        # Создаем модель для таблицы
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Фамилия", "Имя", "Отчество", "Телефон", "Дата рождения", "СНИЛС", "ИНН", "Паспорт", "Стаж работы", "Семейное положение", "Дата приема", "Дата увольнения"])

        # Устанавливаем модель в QTableView
        self.table_view.setModel(self.model)

        # Создаем layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)

        self.add_button = QPushButton("Добавить сотрудника")
        self.add_button.clicked.connect(self.open_add_employee_window)
        
        self.add_tr = QPushButton("Добавить Обучение")
        self.add_tr.clicked.connect(self.open_add_training_window)

        self.delete_button = QPushButton("Удалить сотрудника")
        self.delete_button.clicked.connect(self.mark_employee_as_deleted)
        
        # Кнопки для отчетов
        self.report_button = QPushButton("Сформировать отчеты")
        self.report_button.clicked.connect(self.open_report_form)

        # Добавляем кнопку в layout
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.add_tr)
        layout.addWidget(self.report_button)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Загрузка данных
        self.load_data()
        
        # Подключаем обработчик для двойного клика по строке
        self.table_view.doubleClicked.connect(self.open_edit_employee_window)

    def load_data(self):
        self.model.clear()
        
        employees = self.session.query(Employee).filter(Employee.статус == False).all()
        for row, employee in enumerate(employees):
            self.model.insertRow(row)

            # Строки для связанных данных
            document = employee.документ if employee.документ else None

            # Заполнение таблицы
            self.model.setItem(row, 0, QStandardItem(str(employee.id)))
            self.model.setItem(row, 1, QStandardItem(employee.фамилия))
            self.model.setItem(row, 2, QStandardItem(employee.имя))
            self.model.setItem(row, 3, QStandardItem(employee.отчество))
            self.model.setItem(row, 4, QStandardItem(employee.номер_телефона))
            self.model.setItem(row, 5, QStandardItem(employee.дата_рождения.strftime("%Y-%m-%d")))
            self.model.setItem(row, 6, QStandardItem(employee.снилс))
            self.model.setItem(row, 7, QStandardItem(employee.инн))

            # Извлекаем паспортные данные
            passport_info = f"{document.серия} {document.номер}" if document else "Нет данных"
            self.model.setItem(row, 8, QStandardItem(passport_info))

            self.model.setItem(row, 9, QStandardItem(str(employee.стаж_работы)))
            self.model.setItem(row, 10, QStandardItem("Да" if employee.семейное_положение else "Нет"))

            # Даты
            self.model.setItem(row, 11, QStandardItem(employee.дата_приема.strftime("%Y-%m-%d") if employee.дата_приема else ""))
            self.model.setItem(row, 12, QStandardItem(employee.дата_увольнения.strftime("%Y-%m-%d") if employee.дата_увольнения else "Нет"))
            
    def open_add_employee_window(self):
        # Открытие окна для добавления нового сотрудника (ID = None)
        add_window = AddEmployeeWindow(self.session, self.load_data)
        add_window.exec_()
        
    def open_edit_employee_window(self, index):
        # Получаем ID сотрудника из таблицы
        employee_id = int(self.model.item(index.row(), 0).text())
        
        # Открытие окна для редактирования выбранного сотрудника
        add_window = AddEmployeeWindow(self.session, self.load_data, employee_id)
        add_window.exec_()
        
    def open_add_training_window(self, employee_id):
        dialog = AddTrainingDialog(self.session, employee_id, self)
        dialog.exec_()

    def mark_employee_as_deleted(self):
        current_row = self.table_view.currentIndex().row()
        
        if current_row == -1:
            return

        employee_id = int(self.model.item(current_row, 0).text())

        employee = self.session.query(Employee).get(employee_id)
        
        if employee:
            employee.статус = True
            self.session.commit()

            self.load_data()

            QMessageBox.information(self, "Успех", "Сотрудник успешно помечен как удалённый.")
            
    def open_report_form(self):
        """Открытие формы для формирования отчетов."""
        report_form = ReportForm(self.session)
        report_form.exec_()