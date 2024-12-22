from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QComboBox, QDateEdit
from PySide6.QtCore import QDate
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from datebase import Employee, Document, Post, DepartmentType, Employee_position, education_coworker, Education

class AddEmployeeWindow(QDialog):
    def __init__(self, session, reload_data, employee_id=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowIcon(QIcon('icon.ico'))
        self.reload_data = reload_data
        self.employee_id = employee_id  # ID сотрудника для редактирования, если задано
        self.setWindowTitle("Добавить/Редактировать сотрудника")

        self.layout = QFormLayout()

        # Поля для данных сотрудника
        self.surname_input = QLineEdit()  # Фамилия
        self.name_input = QLineEdit()     # Имя
        self.patronymic_input = QLineEdit()  # Отчество
        self.phone_input = QLineEdit()    # Номер телефона
        self.birthday_input = QDateEdit() # Дата рождения
        self.ssn_input = QLineEdit()      # СНИЛС
        self.tax_id_input = QLineEdit()   # ИНН
        self.work_experience_input = QLineEdit()  # Стаж работы
        self.family_status_input = QComboBox()  # Семейное положение
        self.family_status_input.addItems(["Да", "Нет"])

        # Добавляем комбобокс для выбора паспорта
        self.passport_input = QComboBox()
        self.load_passports()  # Загружаем паспорта из базы

        # Добавление всех элементов на форму
        self.layout.addRow("Фамилия", self.surname_input)
        self.layout.addRow("Имя", self.name_input)
        self.layout.addRow("Отчество", self.patronymic_input)
        self.layout.addRow("Номер телефона", self.phone_input)
        self.layout.addRow("Дата рождения", self.birthday_input)
        self.layout.addRow("СНИЛС", self.ssn_input)
        self.layout.addRow("ИНН", self.tax_id_input)
        self.layout.addRow("Стаж работы", self.work_experience_input)
        self.layout.addRow("Семейное положение", self.family_status_input)
        self.layout.addRow("Паспорт", self.passport_input)

        # Кнопки для добавления/редактирования сотрудника
        self.add_employee_button = QPushButton("Сохранить данные сотрудника")
        self.add_employee_button.clicked.connect(self.save_employee)
        self.layout.addRow(self.add_employee_button)

        self.cancel_button = QPushButton("Отменить")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addRow(self.cancel_button)
        
        # Кнопка для добавления должности
        self.add_position_button = QPushButton("Добавить должность и отдел")
        self.add_position_button.setEnabled(False)  # Изначально кнопка неактивна
        self.add_position_button.clicked.connect(self.open_position_window)
        self.layout.addRow(self.add_position_button)

        # Если это редактирование, то загружаем данные сотрудника
        if self.employee_id:
            self.load_employee_data(self.employee_id)

        self.setLayout(self.layout)

    def load_passports(self):
        """Загружает доступные паспорта в комбобокс"""
        passports = self.session.query(Document).all()
        self.passport_input.clear()
        for passport in passports:
            self.passport_input.addItem(f"{passport.серия}-{passport.номер}", passport.id)

    def load_employee_data(self, employee_id):
        """Загружает данные сотрудника для редактирования"""
        employee = self.session.query(Employee).get(employee_id)
        if employee:
            self.surname_input.setText(employee.фамилия)
            self.name_input.setText(employee.имя)
            self.patronymic_input.setText(employee.отчество)
            self.phone_input.setText(employee.номер_телефона)
            self.birthday_input.setDate(QDate.fromString(str(employee.дата_рождения), "yyyy-MM-dd"))
            self.ssn_input.setText(employee.снилс)
            self.tax_id_input.setText(employee.инн)
            self.work_experience_input.setText(str(employee.стаж_работы))
            self.family_status_input.setCurrentText("Да" if employee.семейное_положение else "Нет")
            self.passport_input.setCurrentIndex(
                self.passport_input.findData(employee.id_паспорт)
            )

    def save_employee(self):
        """Метод для сохранения/обновления данных сотрудника"""
        surname = self.surname_input.text()
        name = self.name_input.text()
        patronymic = self.patronymic_input.text()
        phone = self.phone_input.text()
        birthday = self.birthday_input.date().toPython()
        ssn = self.ssn_input.text()
        tax_id = self.tax_id_input.text()
        work_experience = int(self.work_experience_input.text())
        family_status = self.family_status_input.currentText() == "Да"
        passport_id = self.passport_input.currentData()  # ID паспорта

        if self.employee_id:
            # Если это редактирование, то обновляем данные сотрудника
            employee = self.session.query(Employee).get(self.employee_id)
            if employee:
                employee.фамилия = surname
                employee.имя = name
                employee.отчество = patronymic
                employee.номер_телефона = phone
                employee.дата_рождения = birthday
                employee.снилс = ssn
                employee.инн = tax_id
                employee.стаж_работы = work_experience
                employee.семейное_положение = family_status
                employee.id_паспорт = passport_id
                self.session.commit()
                self.close()
        else:
            # Если это добавление, то создаем нового сотрудника
            employee = Employee(
                фамилия=surname,
                имя=name,
                отчество=patronymic,
                номер_телефона=phone,
                дата_рождения=birthday,
                снилс=ssn,
                инн=tax_id,
                стаж_работы=work_experience,
                семейное_положение=family_status,
                дата_приема=birthday,  # Дата приема на работу
                id_паспорт=passport_id,  # Привязываем паспорт
                статус=False
            )
            self.session.add(employee)
            self.session.commit()

            # После добавления сотрудника активируем кнопки для добавления должности и образования
            self.add_position_button.setEnabled(True)
        
        # Перезагружаем данные в основном окне
        self.reload_data()

    def open_position_window(self):
        """Открытие окна для добавления должности и отдела"""
        # Окно PositionWindow теперь открывается поверх AddEmployeeWindow
        self.position_window = PositionWindow(self.session, self.reload_data, parent=self)
        self.position_window.setWindowModality(Qt.WindowModal)  # Блокируем взаимодействие с родительским окном
        self.position_window.show()
        
    def open_education_window(self):
        """Открытие окна для добавления образования сотруднику"""
        self.education_window = AddEducationWindow(self.session, self.reload_data, parent=self)
        self.education_window.setWindowModality(Qt.WindowModal)  # Блокируем взаимодействие с родительским окном
        self.education_window.show()

from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QPushButton

class AddEducationWindow(QDialog):
    def __init__(self, session, reload_data, parent=None):
        super().__init__(parent)
        self.session = session
        self.reload_data = reload_data
        self.setWindowTitle("Добавить образование сотруднику")

        self.layout = QFormLayout()

        # Выбор сотрудника
        self.employee_input = QComboBox()
        self.load_employees()

        # Выбор образования
        self.education_input = QComboBox()
        self.load_education()

        # Кнопка для добавления образования
        self.add_button = QPushButton("Добавить образование")
        self.add_button.clicked.connect(self.add_education)

        # Добавление элементов на форму
        self.layout.addRow("Сотрудник", self.employee_input)
        self.layout.addRow("Образование", self.education_input)
        self.layout.addRow(self.add_button)

        self.setLayout(self.layout)

    def load_employees(self):
        """Загружает список сотрудников в комбобокс"""
        employees = self.session.query(Employee).all()
        self.employee_input.clear()
        for employee in employees:
            self.employee_input.addItem(f"{employee.фамилия} {employee.имя}", employee.id)

    def load_education(self):
        """Загружает список уровней образования в комбобокс"""
        education = self.session.query(Education).all()
        self.education_input.clear()
        for education_item in education:
            education_display = f"{education_item.уровень_образования}"  # Можно добавить другие поля, если нужно
            self.education_input.addItem(education_display, education_item.id)

    def add_education(self):
        """Метод для добавления образования сотруднику"""
        employee_id = self.employee_input.currentData()  # ID выбранного сотрудника
        education_id = self.education_input.currentData()  # ID выбранного образования

        # Добавляем связь в таблицу связи образования и сотрудников
        new_relation = education_coworker.insert().values(id_сотрудник=employee_id, id_образование=education_id)

        # Выполнение запроса
        self.session.execute(new_relation)
        self.session.commit()

        # Перезагружаем данные
        self.reload_data()

        # Закрытие окна после добавления
        self.close()

    
class PositionWindow(QDialog):
    def __init__(self, session, reload_data, parent=None):
        super().__init__(parent)
        self.session = session
        self.reload_data = reload_data
        self.setWindowTitle("Добавить должность и отдел")

        self.layout = QFormLayout()

        # Выбор должности и отдела
        self.position_input = QComboBox()
        self.load_positions()

        self.department_input = QComboBox()
        self.department_input.addItems(DepartmentType)

        self.layout.addRow("Должность", self.position_input)
        self.layout.addRow("Отдел", self.department_input)

        # Кнопка для сохранения
        self.add_button = QPushButton("Добавить должность и отдел")
        self.add_button.clicked.connect(self.add_position)
        self.layout.addRow(self.add_button)

        self.setLayout(self.layout)

    def load_positions(self):
        """Загружает должности в комбобокс"""
        positions = self.session.query(Post).all()
        self.position_input.clear()
        for position in positions:
            self.position_input.addItem(position.название, position.id)

    def add_position(self):
        """Метод для добавления должности и отдела сотруднику"""
        position_id = self.position_input.currentData()  # ID выбранной должности
        department = self.department_input.currentText()  # Отдел

        # Получаем только что добавленного сотрудника
        employee_id = self.session.query(Employee).order_by(Employee.id.desc()).first().id

        # Создаем запись в таблице Employee_position
        new_position = Employee_position(
            id_должность=position_id,
            id_сотрудник=employee_id,
            отдел=department
        )

        # Добавляем запись в сессию и коммитим
        self.session.add(new_position)
        self.session.commit()

        # Перезагружаем данные в основном окне
        self.reload_data()

        self.close()