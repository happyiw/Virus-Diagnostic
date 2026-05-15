import json
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder


class DatasetPreparer:
    """Класс для подготовки датасета к обучению"""
    
    FEATURE_NAMES = [
        'cpu_load',
        'memory_usage',
        'network_traffic',
        'file_operations',
        'remote_management'
    ]
    
    def __init__(self, dataset_path=None):
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'dataset.json')
        self.dataset_path = dataset_path
        self.data = None
        self.X = None
        self.y = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.label_encoder = LabelEncoder()
    
    def load_dataset(self):
        """Загружает датасет из JSON файла"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"Датасет загружен: {len(self.data)} образцов")
        return self.data
    
    def prepare_features_and_labels(self):
        """Подготавливает признаки (X) и метки классов (y)"""
        if self.data is None:
            self.load_dataset()
        
        # Извлекаем признаки и метки
        features_list = []
        labels_list = []
        
        for sample in self.data:
            features = [
                sample['cpu_load'],
                sample['memory_usage'],
                sample['network_traffic'],
                sample['file_operations'],
                sample['remote_management']
            ]
            features_list.append(features)
            labels_list.append(sample['label'])
        
        self.X = np.array(features_list, dtype=np.float32)
        self.y = np.array(labels_list)
        
        # Кодируем строковые метки в числовые
        self.y_encoded = self.label_encoder.fit_transform(self.y)
        
        print(f"Признаки подготовлены: {self.X.shape}")
        print(f"Метки подготовлены: {len(self.y_encoded)} образцов")
        print(f"Классы: {list(self.label_encoder.classes_)}")
        
        return self.X, self.y_encoded
    
    def split_dataset(self, test_size=0.2, random_state=42):
        """Разделяет датасет на обучающую и тестовую выборки"""
        if self.X is None or self.y_encoded is None:
            self.prepare_features_and_labels()
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y_encoded, test_size=test_size, random_state=random_state
        )
        
        print(f"Обучающая выборка: {self.X_train.shape[0]} образцов")
        print(f"Тестовая выборка: {self.X_test.shape[0]} образцов")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def get_prepared_data(self):
        """Возвращает полностью подготовленные данные"""
        if self.X_train is None:
            self.split_dataset()
        
        return {
            'X_train': self.X_train,
            'X_test': self.X_test,
            'y_train': self.y_train,
            'y_test': self.y_test,
            'label_encoder': self.label_encoder,
            'feature_names': self.FEATURE_NAMES
        }


class MLModel:
    """Модель машинного обучения для диагностики вредоносного ПО"""
    
    def __init__(self, max_depth=15, min_samples_split=5, min_samples_leaf=2):
        self.model = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42
        )
        self.is_trained = False
        self.label_encoder = None
        self.feature_names = None
    
    def train(self, X_train, y_train):
        """Обучает модель на обучающей выборке"""
        print("Обучение модели...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        print("Модель обучена успешно!")
    
    def evaluate(self, X_test, y_test):
        """Оценивает качество модели на тестовой выборке"""
        if not self.is_trained:
            raise ValueError("Модель еще не обучена!")
        
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nТочность модели: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print("\nОтчет о классификации:")
        print(classification_report(y_test, y_pred, target_names=self.label_encoder.classes_))
        
        print("\nМатрица ошибок:")
        print(confusion_matrix(y_test, y_pred))
        
        return {
            'accuracy': accuracy,
            'predictions': y_pred,
            'y_test': y_test
        }
    
    def predict(self, features):
        """Делает предсказание на основе входных признаков"""
        if not self.is_trained:
            raise ValueError("Модель еще не обучена!")
        
        # features должен быть массивом [cpu_load, memory_usage, network_traffic, file_operations, remote_management]
        X = np.array([features], dtype=np.float32)
        y_pred_encoded = self.model.predict(X)[0]
        malware_class = self.label_encoder.inverse_transform([y_pred_encoded])[0]
        
        return malware_class
    
    def save_model(self, model_path=None):
        """Сохраняет обученную модель в файл"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'data', 'model.pkl')
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Модель сохранена в {model_path}")
        return model_path
    
    def load_model(self, model_path=None):
        """Загружает обученную модель из файла"""
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'data', 'model.pkl')
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.is_trained = True
        
        print(f"Модель загружена из {model_path}")
        return self
    
    def get_feature_importance(self):
        """Возвращает важность признаков"""
        if not self.is_trained:
            raise ValueError("Модель еще не обучена!")
        
        importances = self.model.feature_importances_
        feature_importance_dict = dict(zip(self.feature_names, importances))
        
        print("\nВажность признаков:")
        for feature, importance in sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True):
            print(f"  {feature}: {importance:.4f}")
        
        return feature_importance_dict


def train_and_save_model():
    """Основная функция для обучения и сохранения модели"""
    # Подготовка датасета
    preparer = DatasetPreparer()
    preparer.prepare_features_and_labels()
    preparer.split_dataset()
    
    # Получаем подготовленные данные
    data = preparer.get_prepared_data()
    
    # Создаем и обучаем модель
    model = MLModel(max_depth=15, min_samples_split=5, min_samples_leaf=2)
    model.label_encoder = data['label_encoder']
    model.feature_names = data['feature_names']
    
    model.train(data['X_train'], data['y_train'])
    
    # Оцениваем модель
    evaluation = model.evaluate(data['X_test'], data['y_test'])
    
    # Выводим важность признаков
    model.get_feature_importance()
    
    # Сохраняем модель
    model.save_model()
    
    return model, evaluation


if __name__ == '__main__':
    model, evaluation = train_and_save_model()
