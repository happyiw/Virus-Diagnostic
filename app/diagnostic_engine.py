from knowledge_base import KnowledgeBase

class DiagnosticEngine:
    def __init__(self, kb):
        self.kb = kb

    def diagnose(self, input_values):
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