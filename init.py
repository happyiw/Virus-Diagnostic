#!/usr/bin/env python
"""Скрипт для инициализации: генерация датасета и обучение модели"""

import sys
import os

# Добавляем папку app в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from dataset_generator import DatasetGenerator
from ml_model import train_and_save_model

def main():
    print("=" * 50)
    print("Инициализация: Генерация датасета и обучение модели")
    print("=" * 50)
    
    # Генерируем датасет
    print("\n[1/2] Генерируем датасет...")
    generator = DatasetGenerator(dataset_size=7500)
    generator.generate_dataset()
    generator.save_to_json()
    
    # Обучаем модель
    print("\n[2/2] Обучаем модель машинного обучения...")
    model, evaluation = train_and_save_model()
    
    print("\n" + "=" * 50)
    print("Инициализация завершена успешно!")
    print("=" * 50)

if __name__ == '__main__':
    main()
