import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Numeric, SmallInteger, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
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
    
    features = relationship("DiagnosticFeature", secondary="class_features")
    feature_values = relationship("ClassFeatureValue")


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


class NormalRange(Base):
    __tablename__ = "normal_ranges"
    
    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey("diagnostic_features.id"), unique=True, nullable=False)
    min_value = Column(Numeric(10, 2), nullable=False)
    max_value = Column(Numeric(10, 2), nullable=False)


class ClassFeature(Base):
    __tablename__ = "class_features"
    
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("malware_classes.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("diagnostic_features.id"), nullable=False)
    
    __table_args__ = (UniqueConstraint('class_id', 'feature_id', name='_class_feature_uc'),)


class ClassFeatureValue(Base):
    __tablename__ = "class_feature_values"
    
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("malware_classes.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("diagnostic_features.id"), nullable=False)
    min_value = Column(Numeric(20, 2), nullable=False)
    max_value = Column(Numeric(20, 2), nullable=False)
    
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
        # Загружаем данные из JSON файлов
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        # Классы
        with open(os.path.join(data_dir, 'classes.json'), 'r', encoding='utf-8') as f:
            classes_data = json.load(f)
            for class_name in classes_data.get('classes', []):
                if not session.query(MalwareClass).filter_by(name=class_name).first():
                    session.add(MalwareClass(name=class_name))
        
        # Признаки
        with open(os.path.join(data_dir, 'features.json'), 'r', encoding='utf-8') as f:
            features_data = json.load(f)
        
        with open(os.path.join(data_dir, 'feature_types.json'), 'r', encoding='utf-8') as f:
            types_data = json.load(f)
        
        for feature_name in features_data.get('features', []):
            if not session.query(DiagnosticFeature).filter_by(name=feature_name).first():
                feature_type = types_data['feature_types'].get(feature_name, 'integer')
                session.add(DiagnosticFeature(name=feature_name, feature_type=feature_type))
        
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
