import os
import numpy as np
from .knowledge_base import KnowledgeBase

class DiagnosticEngine:
    def __init__(self, kb):
        self.kb = kb
        self.ml_model = None
        self.load_ml_model()
    
    def load_ml_model(self):
        """Загружает обученную ML модель"""
        try:
            import pickle
            model_path = os.path.join(os.path.dirname(__file__), 'data', 'model.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                self.ml_model = model_data['model']
                self.label_encoder = model_data['label_encoder']
                print("ML модель загружена успешно")
            else:
                print("Модель не найдена. Использую правила.")
        except Exception as e:
            print(f"Ошибка при загрузке модели: {e}")
    
    def diagnose_with_ml(self, input_values):
        """Диагностирует с помощью ML модели"""
        if self.ml_model is None:
            return None
        
        try:
            # Извлекаем признаки в правильном порядке
            features = [
                input_values.get('средняя загрузка процессора', 0),
                input_values.get('использование оперативной памяти', 0),
                input_values.get('исходящий сетевой трафик', 0),
                input_values.get('операции изменения файлов', 0),
                input_values.get('наличие устойчивого удаленного управления', 0)
            ]
            
            X = np.array([features], dtype=np.float32)
            y_pred_encoded = self.ml_model.predict(X)[0]
            diagnosis = self.label_encoder.inverse_transform([y_pred_encoded])[0]
            return str(diagnosis)
        except Exception as e:
            print(f"Ошибка в ML диагностике: {e}")
            return None

    def diagnose(self, input_values):
        # Сначала пробуем ML модель
        if self.ml_model is not None:
            ml_diagnosis = self.diagnose_with_ml(input_values)
            if ml_diagnosis:
                return ml_diagnosis
        
        # Fallback на правила
        return self.diagnose_with_rules(input_values)
    
    def diagnose_with_rules(self, input_values):
        # Сначала проверить на "Чистая система"
        normal_ranges = self.kb.get_normal_ranges()
        is_clean = True
        for feature, value in input_values.items():
            normal = normal_ranges.get(feature, [])
            if isinstance(normal, list) and len(normal) == 2:
                if not (normal[0] <= value <= normal[1]):
                    is_clean = False
                    break
            elif isinstance(normal, list) and len(normal) == 1:
                if value != normal[0]:
                    is_clean = False
                    break

        if is_clean:
            return 'Чистая система'

        # Проверить классы
        classes = self.kb.get_classes()
        class_features = self.kb.get_class_features()
        class_values = self.kb.get_class_values()

        for cls in classes:
            if cls == 'Чистая система':
                continue
            features = class_features.get(cls, [])
            match = True
            for feature in features:
                if feature not in input_values:
                    match = False
                    break
                value = input_values[feature]
                expected = class_values.get(cls, {}).get(feature, [])
                if isinstance(expected, list) and len(expected) == 2:
                    if not (expected[0] <= value <= expected[1]):
                        match = False
                        break
                elif isinstance(expected, list) and len(expected) == 1:
                    if value != expected[0]:
                        match = False
                        break
            if match:
                return cls

        return 'Неизвестный класс'  # Или наиболее близкий