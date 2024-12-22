# Импортирование необходимых компонентов для работы с SQLAlchemy
from sqlalchemy import (
    Column,  # Для создания колонок в таблицах
    Integer,  # Для целочисленных значений
    String,  # Для строковых значений
    Date,  # Для работы с типом данных Date
    Boolean,
    ForeignKey,  # Для указания внешних ключей
    Table,  # Для создания промежуточных таблиц
)

from sqlalchemy.ext.declarative import declarative_base  # Для базового класса моделей
from sqlalchemy import create_engine  # Для создания подключения к базе данных
from sqlalchemy.orm import sessionmaker  # Для создания сессии для работы с базой данных
from sqlalchemy.orm import relationship  # Для задания связей между моделями
from sqlalchemy.dialects.postgresql import ENUM

# Создание базового класса для всех моделей
Base = declarative_base()

education_coworker = Table(
    "образование_сотрудника", Base.metadata,
    Column('id_сотрудник', Integer, ForeignKey('сотрудник.id'), primary_key=True),  # Внешний ключ на таблицу партнеров
    Column('id_образование', Integer, ForeignKey('образование.id'), primary_key=True),  # Внешний ключ на таблицу продукции
)

EducationLevelType = ('Основное общее', 'Среднее общее', 'Среднее профессиональное', 'Высшее')
TrainingType = ('очный', 'заочный')
DepartmentType = ('Бухгалтерия', 'IT', 'Маркетинг', 'Отдел продаж')

class Qualification(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "квалификация"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения
    название = Column(String)
    описание = Column(String)
    
    специальность = relationship("Speciality", back_populates="квалификация")

class Speciality(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "специальность"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения
    полнове_название = Column(String)
    сокращенное_названиие = Column(String)
    id_квалификация = Column(Integer, ForeignKey("квалификация.id"))

    квалификация = relationship("Qualification", back_populates="специальность")
    образование = relationship("Education", back_populates="специальность")
        
class Education(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "образование"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения  
    уровень_образования = Column(ENUM(EducationLevelType, name='EducationLevelType', create_type=False), nullable=False)
    серия = Column(Integer)
    номер = Column(Integer)
    регистрационный_номер = Column(Integer)
    дата_выдачи = Column(Date)
    id_специальность = Column(Integer, ForeignKey("специальность.id"))

    специальность = relationship("Speciality", back_populates="образование")
    сотрудник = relationship("Employee", secondary=education_coworker, back_populates="образование")
    
class Document(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "документ"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения
    серия = Column(Integer)
    номер = Column(Integer)
    дата_выдачи = Column(Date)
    кем_выдан = Column(String)

    сотрудник = relationship("Employee", back_populates="документ")
    
class Employee(Base):
    __tablename__ = "сотрудник"
    id = Column(Integer, primary_key=True)
    фамилия = Column(String)
    имя = Column(String)
    отчество = Column(String)
    номер_телефона = Column(String)
    дата_рождения = Column(Date)
    снилс = Column(String)
    инн = Column(String)
    id_паспорт = Column(Integer, ForeignKey("документ.id"))
    стаж_работы = Column(Integer)
    семейное_положение = Column(Boolean)
    дата_приема = Column(Date)
    дата_увольнения = Column(Date)
    статус = Column(Boolean, default=False)
    
    должность_сотрудников = relationship("Employee_position", back_populates="сотрудник")
    документ = relationship("Document", back_populates="сотрудник")
    образование = relationship("Education", secondary=education_coworker, back_populates="сотрудник")
    обучение_сотрудника = relationship("Employee_training", back_populates="сотрудник")
    
class Place_Study(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "место_обучения"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения
    полное_название = Column(String)
    сокращенное_названеие = Column(String)

    обучение = relationship("Training", back_populates="место_обучения")
    
class Training(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "обучение"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения
    название = Column(String)
    вид = Column(ENUM(*TrainingType, name='TrainingType', create_type=False), nullable=False)
    дата_начала = Column(Date)
    дата_окончания = Column(Date)
    формат_проведени = Column(String)
    id_место_проведения = Column(Integer, ForeignKey("место_обучения.id"))
    
    место_обучения = relationship("Place_Study", back_populates="обучение")
    обучение_сотрудника = relationship("Employee_training", back_populates="обучение")
    
    
class Employee_training(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "обучение_сотрудника"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения
    id_обучение = Column(Integer, ForeignKey("обучение.id"))
    id_сотрудник = Column(Integer, ForeignKey("сотрудник.id"))
    обучение_пройдено = Column(Boolean)
    путь_документа = Column(String)
    номер_документа = Column(String)

    обучение = relationship("Training", back_populates="обучение_сотрудника")
    сотрудник = relationship("Employee", back_populates="обучение_сотрудника")
    
class Post(Base):
    # Таблица для хранения информации о перемещении сотрудников между помещениями
    __tablename__ = "должность"
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор перемещения
    название = Column(String)
    описание_трудовых_обязательностей = Column(String)

    должность_сотрудников = relationship("Employee_position", back_populates="должность")

class Employee_position(Base):
    __tablename__ = "должность_сотрудника"
    id = Column(Integer, primary_key=True)
    id_должность = Column(Integer, ForeignKey("должность.id"))
    id_сотрудник = Column(Integer, ForeignKey("сотрудник.id"))
    отдел = Column(ENUM(DepartmentType, name='DepartmentType', create_type=False), nullable=False)

    должность = relationship("Post", back_populates="должность_сотрудников")  # Исправление
    сотрудник = relationship("Employee", back_populates="должность_сотрудников")  # Пример добавления обратной связи для сотрудника
    
class Connect:
    # Класс для создания подключения к базе данных
    @staticmethod
    def create_connection():
        # Создание подключения к базе данных PostgreSQL
        engine = create_engine("postgresql://postgres:1234@localhost:5432/viktor")
        Base.metadata.create_all(engine)  # Создание всех таблиц в базе данных
        Session = sessionmaker(bind=engine)  # Создание сессии для работы с базой данных
        session = Session()  # Открытие сессии
        return session  #
