import os


ML_FEATURE_NAMES = [
    'средняя загрузка процессора',
    'использование оперативной памяти',
    'исходящий сетевой трафик',
    'операции изменения файлов',
    'наличие устойчивого удаленного управления',
]

class DiagnosticEngine:
    def __init__(self, kb):
        self.kb = kb
        self.ml_model = None
        self.label_encoder = None
        self.load_ml_model()
    
    def load_ml_model(self):
        """Загружает обученную ML модель"""
        model_path = os.path.join(os.path.dirname(__file__), 'data', 'model.pkl')
        if not os.path.exists(model_path):
            print("Модель не найдена. Использую правила.")
            return

        try:
            import pickle
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            self.ml_model = model_data['model']
            self.label_encoder = model_data['label_encoder']
            print("ML модель загружена успешно")
        except Exception as e:
            print(f"Ошибка при загрузке модели: {e}")
    
    def diagnose_with_ml(self, input_values):
        """Диагностирует с помощью ML модели"""
        if self.ml_model is None:
            return None
        
        try:
            import numpy as np

            features = [input_values.get(feature_name, 0) for feature_name in ML_FEATURE_NAMES]
            
            X = np.array([features], dtype=np.float32)
            y_pred_encoded = self.ml_model.predict(X)[0]
            diagnosis = self.label_encoder.inverse_transform([y_pred_encoded])[0]
            return str(diagnosis)
        except Exception as e:
            print(f"Ошибка в ML диагностике: {e}")
            return None

    def diagnose(self, input_values):
        expert_result = self.diagnose_with_rules(input_values)
        ml_result = None
        if self.ml_model is not None:
            ml_result = self.diagnose_with_ml(input_values)

        return {
            'expert_diagnosis': expert_result['diagnosis'],
            'rejected': expert_result['rejected'],
            'ml_diagnosis': ml_result
        }

    def diagnose_with_rules(self, input_values):
        normal_ranges = self.kb.get_normal_ranges()
        abnormal_features = []
        for feature, value in input_values.items():
            normal = normal_ranges.get(feature)
            if isinstance(normal, list) and len(normal) == 2:
                if not (normal[0] <= value <= normal[1]):
                    abnormal_features.append(feature)
            elif isinstance(normal, list) and len(normal) == 1:
                if value != normal[0]:
                    abnormal_features.append(feature)

        if not abnormal_features:
            return {'diagnosis': 'Чистая система', 'rejected': []}

        classes = self.kb.get_classes()
        class_features = self.kb.get_class_features()
        class_values = self.kb.get_class_values()
        abnormal_feature_set = set(abnormal_features)

        candidates = []
        for cls in classes:
            if cls == 'Чистая система':
                continue

            features = class_features.get(cls, [])
            if not features:
                continue

            shared = set(features).intersection(abnormal_feature_set)
            if not shared:
                continue

            reasons = []
            for feature in features:
                if feature not in input_values:
                    continue

                value = input_values[feature]
                expected = class_values.get(cls, {}).get(feature)
                if expected is None:
                    continue

                if isinstance(expected, list) and len(expected) == 2:
                    if not (expected[0] <= value <= expected[1]):
                        reasons.append(f"для признака '{feature}' значение {value} не попадает в диапазон {expected}")
                elif isinstance(expected, list) and len(expected) == 1:
                    if value != expected[0]:
                        reasons.append(f"для признака '{feature}' ожидается значение {expected[0]}, но получено {value}")

            candidates.append({
                'class': cls,
                'reasons': reasons,
                'shared_count': len(shared)
            })

        if not candidates:
            return {'diagnosis': 'Неизвестный класс', 'rejected': []}

        candidates.sort(key=lambda item: (len(item['reasons']), -item['shared_count']))

        best = candidates[0]
        diagnosis = best['class'] if len(best['reasons']) == 0 else 'Неизвестный класс'

        # формируем список отклонённых гипотез: только N ближайших кандидатов
        N = 3
        if diagnosis != 'Неизвестный класс':
            other_candidates = [item for item in candidates if item['class'] != diagnosis]
            top_candidates = other_candidates[:N]
        else:
            # если диагноз неопределён — показываем N лучших кандидатов
            top_candidates = candidates[:N]

        rejected = []
        for item in top_candidates:
            reason_text = '; '.join(item['reasons']) if item.get('reasons') else 'пользовательские признаки не совпадают'
            rejected.append({'class': item['class'], 'reason': reason_text})

        return {'diagnosis': diagnosis, 'rejected': rejected}
