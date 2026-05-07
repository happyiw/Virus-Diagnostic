import json
import os
from tinydb import TinyDB, Query

class KnowledgeBase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'data', 'knowledge.db')
        self.db_path = db_path
        self.db = TinyDB(db_path)
        self.initialize_default_data()

    def initialize_default_data(self):
        # Проверяем, есть ли данные
        if not self.db.all():
            # Инициализируем базовые данные из курсовой
            self.db.insert({
                'type': 'classes',
                'data': [
                    'File injector virus', 'Network worm', 'Trojan downloader', 'Remote Access Trojan',
                    'Banking Trojan', 'Crypto-ransomware', 'Wiper', 'Cryptominer', 'Botnet agent', 'Rootkit', 'Чистая система'
                ]
            })
            self.db.insert({
                'type': 'features',
                'data': [
                    'средняя загрузка процессора', 'использование оперативной памяти',
                    'исходящий сетевой трафик', 'операции изменения файлов', 'наличие устойчивого удаленного управления'
                ]
            })
            # Типы признаков
            self.db.insert({
                'type': 'feature_types',
                'data': {
                    'средняя загрузка процессора': 'integer',
                    'использование оперативной памяти': 'integer',
                    'исходящий сетевой трафик': 'real',
                    'операции изменения файлов': 'real',
                    'наличие устойчивого удаленного управления': 'boolean'
                }
            })
            # Допустимые значения
            self.db.insert({
                'type': 'valid_ranges',
                'data': {
                    'средняя загрузка процессора': [0, 100],
                    'использование оперативной памяти': [0, 100],
                    'исходящий сетевой трафик': [0, 10000],
                    'операции изменения файлов': [0, 100000],
                    'наличие устойчивого удаленного управления': [0, 1]
                }
            })
            # Нормальные значения
            self.db.insert({
                'type': 'normal_ranges',
                'data': {
                    'средняя загрузка процессора': [0, 25],
                    'использование оперативной памяти': [0, 40],
                    'исходящий сетевой трафик': [0, 50],
                    'операции изменения файлов': [0, 100],
                    'наличие устойчивого удаленного управления': [0]
                }
            })
            # Признаки классов
            self.db.insert({
                'type': 'class_features',
                'data': {
                    'File injector virus': ['средняя загрузка процессора', 'использование оперативной памяти', 'операции изменения файлов'],
                    'Network worm': ['средняя загрузка процессора', 'использование оперативной памяти', 'исходящий сетевой трафик'],
                    'Trojan downloader': ['средняя загрузка процессора', 'использование оперативной памяти', 'исходящий сетевой трафик'],
                    'Remote Access Trojan': ['использование оперативной памяти', 'исходящий сетевой трафик', 'наличие устойчивого удалённого управления'],
                    'Banking Trojan': ['исходящий сетевой трафик', 'операции изменения файлов', 'наличие устойчивого удалённого управления'],
                    'Crypto-ransomware': ['средняя загрузка процессора', 'использование оперативной памяти', 'операции изменения файлов'],
                    'Wiper': ['средняя загрузка процессора', 'использование оперативной памяти', 'операции изменения файлов'],
                    'Cryptominer': ['средняя загрузка процессора', 'использование оперативной памяти', 'исходящий сетевой трафик'],
                    'Botnet agent': ['средняя загрузка процессора', 'исходящий сетевой трафик', 'наличие устойчивого удалённого управления'],
                    'Rootkit': ['средняя загрузка процессора', 'использование оперативной памяти', 'наличие устойчивого удалённого управления'],
                    'Чистая система': []
                }
            })
            # Значения для классов (упрощенные диапазоны)
            self.db.insert({
                'type': 'class_values',
                'data': {
                    'File injector virus': {
                        'средняя загрузка процессора': [25, 100],
                        'использование оперативной памяти': [20, 100],
                        'операции изменения файлов': [300, 100000]
                    },
                    'Network worm': {
                        'средняя загрузка процессора': [30, 100],
                        'использование оперативной памяти': [25, 100],
                        'исходящий сетевой трафик': [400, 10000]
                    },
                    # Добавить остальные аналогично
                    'Чистая система': {}
                }
            })

    def get_classes(self):
        result = self.db.search(Query().type == 'classes')
        return result[0]['data'] if result else []

    def get_features(self):
        result = self.db.search(Query().type == 'features')
        return result[0]['data'] if result else []

    def get_feature_types(self):
        result = self.db.search(Query().type == 'feature_types')
        return result[0]['data'] if result else {}

    def get_valid_ranges(self):
        result = self.db.search(Query().type == 'valid_ranges')
        return result[0]['data'] if result else {}

    def get_normal_ranges(self):
        result = self.db.search(Query().type == 'normal_ranges')
        return result[0]['data'] if result else {}

    def get_class_features(self):
        result = self.db.search(Query().type == 'class_features')
        return result[0]['data'] if result else {}

    def get_class_values(self):
        result = self.db.search(Query().type == 'class_values')
        return result[0]['data'] if result else {}

    # Методы для обновления
    def add_class(self, class_name):
        classes = self.get_classes()
        if class_name not in classes:
            classes.append(class_name)
            self.db.update({'data': classes}, Query().type == 'classes')

    def remove_class(self, class_name):
        classes = self.get_classes()
        if class_name in classes:
            classes.remove(class_name)
            self.db.update({'data': classes}, Query().type == 'classes')

    # Аналогично для других