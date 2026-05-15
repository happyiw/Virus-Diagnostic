import json
import random
import os
from datetime import datetime

class DatasetGenerator:
    """Генератор датасета для обучения модели диагностики вредоносного ПО"""
    
    # Определения классов и их характеристик
    MALWARE_CLASSES = {
        'File injector virus': {
            'cpu_load': (25, 100),
            'memory_usage': (20, 100),
            'network_traffic': (0, 50),
            'file_operations': (300, 100000),
            'remote_management': 0
        },
        'Network worm': {
            'cpu_load': (30, 100),
            'memory_usage': (25, 100),
            'network_traffic': (400, 10000),
            'file_operations': (50, 100000),
            'remote_management': 0
        },
        'Trojan downloader': {
            'cpu_load': (10, 100),
            'memory_usage': (15, 100),
            'network_traffic': (120, 10000),
            'file_operations': (0, 80),
            'remote_management': 0
        },
        'Remote Access Trojan': {
            'cpu_load': (15, 100),
            'memory_usage': (25, 100),
            'network_traffic': (60, 10000),
            'file_operations': (0, 100),
            'remote_management': 1
        },
        'Banking Trojan': {
            'cpu_load': (20, 100),
            'memory_usage': (30, 100),
            'network_traffic': (80, 10000),
            'file_operations': (50, 100000),
            'remote_management': 1
        },
        'Crypto-ransomware': {
            'cpu_load': (70, 100),
            'memory_usage': (40, 100),
            'network_traffic': (0, 200),
            'file_operations': (2000, 100000),
            'remote_management': 0
        },
        'Wiper': {
            'cpu_load': (50, 100),
            'memory_usage': (30, 100),
            'network_traffic': (0, 100),
            'file_operations': (3000, 100000),
            'remote_management': 0
        },
        'Cryptominer': {
            'cpu_load': (85, 100),
            'memory_usage': (50, 100),
            'network_traffic': (20, 10000),
            'file_operations': (0, 50),
            'remote_management': 0
        },
        'Botnet agent': {
            'cpu_load': (50, 100),
            'memory_usage': (30, 100),
            'network_traffic': (1000, 10000),
            'file_operations': (0, 100),
            'remote_management': 1
        },
        'Rootkit': {
            'cpu_load': (5, 100),
            'memory_usage': (10, 100),
            'network_traffic': (0, 50),
            'file_operations': (0, 50),
            'remote_management': 1
        },
        'Чистая система': {
            'cpu_load': (0, 25),
            'memory_usage': (0, 40),
            'network_traffic': (0, 50),
            'file_operations': (0, 100),
            'remote_management': 0
        }
    }
    
    def __init__(self, dataset_size=7500):
        self.dataset_size = dataset_size
        self.dataset = []
    
    def generate_sample(self, malware_class):
        """Генерирует один образец данных для класса вредоносного ПО"""
        characteristics = self.MALWARE_CLASSES[malware_class]
        
        # Генерируем значения для каждого признака
        cpu_load = random.randint(
            int(characteristics['cpu_load'][0]),
            int(characteristics['cpu_load'][1])
        )
        
        memory_usage = random.randint(
            int(characteristics['memory_usage'][0]),
            int(characteristics['memory_usage'][1])
        )
        
        network_traffic = random.uniform(
            characteristics['network_traffic'][0],
            characteristics['network_traffic'][1]
        )
        
        file_operations = random.uniform(
            characteristics['file_operations'][0],
            characteristics['file_operations'][1]
        )
        
        remote_management = characteristics['remote_management']
        
        # Добавляем небольшой шум к данным (±5% от значения)
        cpu_load = max(0, min(100, cpu_load + random.randint(-5, 5)))
        memory_usage = max(0, min(100, memory_usage + random.randint(-5, 5)))
        network_traffic = max(0, network_traffic + random.uniform(-50, 50))
        file_operations = max(0, file_operations + random.uniform(-100, 100))
        
        return {
            'cpu_load': int(cpu_load),
            'memory_usage': int(memory_usage),
            'network_traffic': round(network_traffic, 2),
            'file_operations': round(file_operations, 2),
            'remote_management': int(remote_management),
            'label': malware_class
        }
    
    def generate_dataset(self):
        """Генерирует полный датасет"""
        # Равномерно распределяем образцы по классам
        samples_per_class = self.dataset_size // len(self.MALWARE_CLASSES)
        
        for malware_class in self.MALWARE_CLASSES.keys():
            for _ in range(samples_per_class):
                self.dataset.append(self.generate_sample(malware_class))
        
        # Перемешиваем датасет
        random.shuffle(self.dataset)
        
        return self.dataset
    
    def save_to_json(self, filename='dataset.json'):
        """Сохраняет датасет в JSON файл"""
        if not self.dataset:
            self.generate_dataset()
        
        output_path = os.path.join(os.path.dirname(__file__), 'data', filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=2, ensure_ascii=False)
        
        print(f"Датасет сохранен в {output_path}")
        print(f"Размер датасета: {len(self.dataset)} образцов")
        
        # Вывести статистику
        class_counts = {}
        for sample in self.dataset:
            label = sample['label']
            class_counts[label] = class_counts.get(label, 0) + 1
        
        print("\nРаспределение по классам:")
        for cls, count in sorted(class_counts.items()):
            print(f"  {cls}: {count} образцов")
        
        return output_path


if __name__ == '__main__':
    # Генерируем датасет из 7500 образцов
    generator = DatasetGenerator(dataset_size=7500)
    generator.generate_dataset()
    generator.save_to_json('dataset.json')
