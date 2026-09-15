import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, SmallInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Конфигурация БД
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_USER = os.getenv('DB_USER', 'virusdb')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'viruspass')
DB_NAME = os.getenv('DB_NAME', 'virus_diagnostic')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Модели ORM
class MalwareClass(Base):
    __tablename__ = "malware_classes"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    features = relationship("DiagnosticFeature", secondary="class_features", overlaps="class_features,feature")
    class_features = relationship("ClassFeature", back_populates="malware_class", overlaps="features,class_features")
    feature_values = relationship("ClassFeatureValue", back_populates="malware_class", overlaps="feature_values,malware_class")


class DiagnosticFeature(Base):
    __tablename__ = "diagnostic_features"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    feature_type = Column(String(20), nullable=False)  # integer, real, boolean
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ValueRange(Base):
    __tablename__ = "value_ranges"
    
    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey("diagnostic_features.id"), unique=True, nullable=False)
    min_value = Column(Numeric(10, 2), nullable=False)
    max_value = Column(Numeric(10, 2), nullable=False)
    feature = relationship("DiagnosticFeature")


class NormalRange(Base):
    __tablename__ = "normal_ranges"
    
    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey("diagnostic_features.id"), unique=True, nullable=False)
    min_value = Column(Numeric(10, 2), nullable=False)
    max_value = Column(Numeric(10, 2), nullable=False)
    feature = relationship("DiagnosticFeature")


class ClassFeature(Base):
    __tablename__ = "class_features"
    
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("malware_classes.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("diagnostic_features.id"), nullable=False)
    
    malware_class = relationship("MalwareClass", back_populates="class_features", overlaps="features,class_features")
    feature = relationship("DiagnosticFeature", overlaps="features")
    
    __table_args__ = (UniqueConstraint('class_id', 'feature_id', name='_class_feature_uc'),)


class ClassFeatureValue(Base):
    __tablename__ = "class_feature_values"
    
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("malware_classes.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("diagnostic_features.id"), nullable=False)
    min_value = Column(Numeric(20, 2), nullable=False)
    max_value = Column(Numeric(20, 2), nullable=False)
    
    malware_class = relationship("MalwareClass", back_populates="feature_values", overlaps="feature_values,malware_class")
    feature = relationship("DiagnosticFeature", overlaps="features")
    
    __table_args__ = (UniqueConstraint('class_id', 'feature_id', name='_class_feature_value_uc'),)


class DiagnosisLog(Base):
    __tablename__ = "diagnosis_logs"
    
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("malware_classes.id"))
    cpu_load = Column(Integer)
    memory_usage = Column(Integer)
    network_traffic = Column(Numeric(10, 2))
    file_operations = Column(Numeric(20, 2))
    remote_management = Column(SmallInteger)
    model_used = Column(String(50))  # 'rules', 'ml'
    created_at = Column(DateTime, default=datetime.utcnow)


def create_tables():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)


def init_database_from_json():
    """Инициализирует БД данными из JSON файлов"""
    session = SessionLocal()
    
    try:
        data_dir = os.path.join(os.path.dirname(__file__), 'data')

        # Классы
        with open(os.path.join(data_dir, 'classes.json'), 'r', encoding='utf-8') as f:
            classes_data = json.load(f).get('data', [])
            for class_name in classes_data:
                if not session.query(MalwareClass).filter_by(name=class_name).first():
                    session.add(MalwareClass(name=class_name))

        # Признаки
        with open(os.path.join(data_dir, 'features.json'), 'r', encoding='utf-8') as f:
            features_data = json.load(f).get('data', [])
        with open(os.path.join(data_dir, 'feature_types.json'), 'r', encoding='utf-8') as f:
            types_data = json.load(f).get('data', {})

        for feature_name in features_data:
            if not session.query(DiagnosticFeature).filter_by(name=feature_name).first():
                feature_type = types_data.get(feature_name, 'integer')
                session.add(DiagnosticFeature(name=feature_name, feature_type=feature_type))

        # Диапазоны
        with open(os.path.join(data_dir, 'ranges.json'), 'r', encoding='utf-8') as f:
            ranges_data = json.load(f).get('data', {})

        for feature_name, value in ranges_data.get('valid_ranges', {}).items():
            feature = session.query(DiagnosticFeature).filter_by(name=feature_name).first()
            if feature and not session.query(ValueRange).filter_by(feature_id=feature.id).first():
                if isinstance(value, list) and len(value) == 2:
                    session.add(ValueRange(feature_id=feature.id, min_value=value[0], max_value=value[1]))
                elif isinstance(value, list) and len(value) == 1:
                    session.add(ValueRange(feature_id=feature.id, min_value=value[0], max_value=value[0]))
                else:
                    print(f"Пропускаю некорректный valid range для {feature_name}: {value}")

        for feature_name, value in ranges_data.get('normal_ranges', {}).items():
            feature = session.query(DiagnosticFeature).filter_by(name=feature_name).first()
            if feature and not session.query(NormalRange).filter_by(feature_id=feature.id).first():
                if isinstance(value, list) and len(value) == 2:
                    session.add(NormalRange(feature_id=feature.id, min_value=value[0], max_value=value[1]))
                elif isinstance(value, list) and len(value) == 1:
                    session.add(NormalRange(feature_id=feature.id, min_value=value[0], max_value=value[0]))
                else:
                    print(f"Пропускаю некорректный normal range для {feature_name}: {value}")

        # Признаки классов
        with open(os.path.join(data_dir, 'class_features.json'), 'r', encoding='utf-8') as f:
            class_features_data = json.load(f).get('data', {})

        for class_name, feature_list in class_features_data.items():
            malware_class = session.query(MalwareClass).filter_by(name=class_name).first()
            if not malware_class:
                continue
            for feature_name in feature_list:
                feature = session.query(DiagnosticFeature).filter_by(name=feature_name).first()
                if feature and not session.query(ClassFeature).filter_by(class_id=malware_class.id, feature_id=feature.id).first():
                    session.add(ClassFeature(class_id=malware_class.id, feature_id=feature.id))

        # Значения классов
        with open(os.path.join(data_dir, 'class_values.json'), 'r', encoding='utf-8') as f:
            class_values_data = json.load(f).get('data', {})

        for class_name, values in class_values_data.items():
            malware_class = session.query(MalwareClass).filter_by(name=class_name).first()
            if not malware_class:
                continue
            for feature_name, value in values.items():
                feature = session.query(DiagnosticFeature).filter_by(name=feature_name).first()
                if feature and not session.query(ClassFeatureValue).filter_by(class_id=malware_class.id, feature_id=feature.id).first():
                    if isinstance(value, list):
                        if len(value) == 2:
                            session.add(ClassFeatureValue(class_id=malware_class.id, feature_id=feature.id, min_value=value[0], max_value=value[1]))
                        elif len(value) == 1:
                            session.add(ClassFeatureValue(class_id=malware_class.id, feature_id=feature.id, min_value=value[0], max_value=value[0]))
                        else:
                            print(f"Пропускаю некорректное значение для {class_name}/{feature_name}: {value}")
                    else:
                        print(f"Пропускаю некорректный тип значения для {class_name}/{feature_name}: {value}")

        session.commit()
        print("БД инициализирована успешно из JSON файлов")
        
    except Exception as e:
        session.rollback()
        print(f"Ошибка при инициализации БД: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    create_tables()
    init_database_from_json()
