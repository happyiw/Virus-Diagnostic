import json
import os
import tempfile
import unittest

import numpy as np
from sklearn.preprocessing import LabelEncoder

from app.diagnostic_engine import DiagnosticEngine
from app.ml_model import DatasetPreparer, MLModel


class DummyKnowledgeBase:
    def __init__(self):
        self._classes = ['Чистая система', 'Network worm']
        self._feature_types = {
            'средняя загрузка процессора': 'integer',
            'использование оперативной памяти': 'integer',
            'исходящий сетевой трафик': 'integer',
            'операции изменения файлов': 'integer',
            'наличие устойчивого удаленного управления': 'boolean'
        }
        self._normal_ranges = {
            'средняя загрузка процессора': [0, 25],
            'использование оперативной памяти': [0, 40],
            'исходящий сетевой трафик': [0, 50],
            'операции изменения файлов': [0, 100],
            'наличие устойчивого удаленного управления': [0]
        }
        self._class_features = {
            'Чистая система': [],
            'Network worm': ['средняя загрузка процессора']
        }
        self._class_values = {
            'Чистая система': {
                'средняя загрузка процессора': [0, 25]
            },
            'Network worm': {
                'средняя загрузка процессора': [30, 100]
            }
        }

    def get_classes(self):
        return list(self._classes)

    def get_feature_types(self):
        return dict(self._feature_types)

    def get_normal_ranges(self):
        return dict(self._normal_ranges)

    def get_class_features(self):
        return dict(self._class_features)

    def get_class_values(self):
        return dict(self._class_values)


class TestDatasetPreparer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dataset_path = os.path.join(self.temp_dir.name, 'dataset.json')
        self.samples = [
            {
                'cpu_load': 10,
                'memory_usage': 20,
                'network_traffic': 5,
                'file_operations': 10,
                'remote_management': 0,
                'label': 'Clean'
            },
            {
                'cpu_load': 60,
                'memory_usage': 50,
                'network_traffic': 300,
                'file_operations': 200,
                'remote_management': 0,
                'label': 'Malware'
            }
        ]
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.samples, f, ensure_ascii=False)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_dataset_and_validate(self):
        preparer = DatasetPreparer(dataset_path=self.dataset_path)
        data = preparer.load_dataset()
        self.assertEqual(len(data), 2)

    def test_prepare_features_and_labels(self):
        preparer = DatasetPreparer(dataset_path=self.dataset_path)
        preparer.load_dataset()
        X, y = preparer.prepare_features_and_labels()
        self.assertEqual(X.shape, (2, 5))
        self.assertEqual(y.shape, (2,))
        self.assertTrue(np.allclose(X[0], [10, 20, 5, 10, 0]))
        self.assertEqual(set(y.tolist()), {'Clean', 'Malware'})


class TestMLModel(unittest.TestCase):
    def setUp(self):
        self.X_train = np.array([
            [10, 20, 5, 10, 0],
            [60, 50, 300, 200, 0],
            [55, 45, 280, 180, 0]
        ], dtype=np.float32)
        labels = ['Clean', 'Malware', 'Malware']
        self.label_encoder = LabelEncoder().fit(labels)
        self.y_train = self.label_encoder.transform(labels)

    def test_train_and_predict(self):
        model = MLModel(max_depth=3, min_samples_split=2, min_samples_leaf=1)
        model.label_encoder = self.label_encoder
        model.feature_names = ['cpu_load', 'memory_usage', 'network_traffic', 'file_operations', 'remote_management']
        model.train(self.X_train, self.y_train)
        prediction = model.predict([60, 50, 300, 200, 0])
        self.assertIn(prediction, ['Clean', 'Malware'])

    def test_evaluate_requires_trained_model(self):
        model = MLModel()
        with self.assertRaises(ValueError):
            model.evaluate(self.X_train, self.y_train)


class TestDiagnosticEngine(unittest.TestCase):
    def test_clean_system_diagnosis(self):
        kb = DummyKnowledgeBase()
        engine = DiagnosticEngine(kb)
        result = engine.diagnose({
            'средняя загрузка процессора': 10,
            'использование оперативной памяти': 20,
            'исходящий сетевой трафик': 10,
            'операции изменения файлов': 10,
            'наличие устойчивого удаленного управления': 0
        })
        self.assertEqual(result['expert_diagnosis'], 'Чистая система')
        self.assertEqual(result['rejected'], [])

    def test_network_worm_diagnosis(self):
        kb = DummyKnowledgeBase()
        engine = DiagnosticEngine(kb)
        result = engine.diagnose({
            'средняя загрузка процессора': 50,
            'использование оперативной памяти': 20,
            'исходящий сетевой трафик': 10,
            'операции изменения файлов': 10,
            'наличие устойчивого удаленного управления': 0
        })
        self.assertEqual(result['expert_diagnosis'], 'Network worm')
        self.assertIsInstance(result['rejected'], list)


if __name__ == '__main__':
    unittest.main()
