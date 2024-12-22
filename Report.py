from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QDateEdit
from datebase import Employee, Employee_training, Training
from PySide6.QtGui import QIcon

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

class ReportGenerator:
    def __init__(self, session):
        self.session = session
        # Регистрация шрифта DejaVuSans
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

    def generate_training_report(self, start_date, end_date):
        """Генерация отчета об обучении сотрудников."""
        file_path = "training_report.pdf"
        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("DejaVuSans", 12)  # Установка шрифта и размера
        c.drawString(100, 750, "Отчет об обучении сотрудников")
        c.drawString(100, 730, f"Период: {start_date} - {end_date}")

        # Запрос данных об обучении сотрудников
        trainings = self.session.query(Employee_training).join(Training).filter(
            Employee_training.обучение_пройдено == True,
            Training.дата_начала >= start_date,
            Training.дата_окончания <= end_date
        ).all()

        total_completed = len(trainings)  # Подсчет количества завершенных обучений

        c.drawString(100, 690, f"Всего завершено обучений: {total_completed}")

        # Дополнительная информация по каждому обучению
        y_position = 650
        for training in trainings:
            employee = training.сотрудник
            c.drawString(100, y_position, f"Сотрудник: {employee.фамилия} {employee.имя}")
            c.drawString(300, y_position, f"Курс: {training.обучение.название}")
            y_position -= 20  # Сдвиг для следующей строки

        c.save()
        print(f"Отчет об обучении успешно сгенерирован и сохранен в {file_path}")

    def generate_employee_card_report(self, employee_id):
        """Генерация карточки сотрудника с курсами обучения."""
        employee = self.session.query(Employee).get(employee_id)
        if not employee:
            raise ValueError("Сотрудник не найден")

        file_path = f"{employee.фамилия}_{employee.имя}_card.pdf"
        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("DejaVuSans", 12)  # Установка шрифта и размера
        c.drawString(100, 750, f"Карточка сотрудника: {employee.фамилия} {employee.имя}")
        c.drawString(100, 730, f"Дата рождения: {employee.дата_рождения}")
        c.drawString(100, 710, f"Телефон: {employee.номер_телефона}")
        c.drawString(100, 690, f"СНИЛС: {employee.снилс}")
        c.drawString(100, 670, f"ИНН: {employee.инн}")
        c.drawString(100, 650, f"Паспорт ID: {employee.id_паспорт}")

        # Получение курсов обучения сотрудника
        trainings = self.session.query(Employee_training).filter_by(id_сотрудник=employee_id).all()
        c.drawString(100, 620, "Курсы обучения:")
        y_position = 600
        for training in trainings:
            c.drawString(100, y_position, f"Курс: {training.обучение.название}, Завершено: {'Да' if training.обучение_пройдено else 'Нет'}")
            y_position -= 20  # Сдвиг для следующей строки

        c.save()
        print(f"Карточка сотрудника успешно сгенерирована и сохранена в {file_path}")


class ReportForm(QDialog):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setWindowTitle("Формирование отчетов")
        self.setWindowIcon(QIcon('icon.ico'))
        self.setFixedSize(400, 160)
        
        self.layout = QFormLayout(self)

        # Поля для ввода периода
        self.start_date_edit = QDateEdit()
        self.end_date_edit = QDateEdit()
        self.layout.addRow("Дата начала:", self.start_date_edit)
        self.layout.addRow("Дата окончания:", self.end_date_edit)

        # Кнопка для формирования отчета
        self.btn_generate_reports = QPushButton("Сформировать отчеты")
        self.btn_generate_reports.clicked.connect(self.generate_reports)
        self.layout.addRow(self.btn_generate_reports)

        # Поле для ввода ID сотрудника
        self.employee_id_input = QLineEdit()
        self.layout.addRow("ID сотрудника:", self.employee_id_input)
        
        # Кнопка для генерации карточки сотрудника
        self.btn_generate_employee_card = QPushButton("Сформировать карточку сотрудника")
        self.btn_generate_employee_card.clicked.connect(self.generate_employee_card)
        self.layout.addRow(self.btn_generate_employee_card)


    def generate_reports(self):
        try:
            """Генерация отчетов в PDF."""
            start_date = self.start_date_edit.date().toPython()
            end_date = self.end_date_edit.date().toPython()

            report_generator = ReportGenerator(self.session)
            report_generator.generate_training_report(start_date, end_date)

            QMessageBox.information(self, "Успех", "Отчет об обучении успешно сгенерирован.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def generate_employee_card(self):
        """Генерация карточки сотрудника по ID."""
        try:
            employee_id = int(self.employee_id_input.text())
            report_generator = ReportGenerator(self.session)
            report_generator.generate_employee_card_report(employee_id)

            QMessageBox.information(self, "Успех", "Карточка сотрудника успешно сгенерирована.")
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите корректный ID сотрудника.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


            
    def open_report_form(self):
        """Открытие формы для генерации отчетов."""
        report_form = ReportForm(self.session)
        report_form.exec_()