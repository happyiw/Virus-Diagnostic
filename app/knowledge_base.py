import json
import os
from sqlalchemy.exc import SQLAlchemyError
from .database import (
    SessionLocal,
    create_tables,
    init_database_from_json,
    MalwareClass,
    DiagnosticFeature,
    ValueRange,
    NormalRange,
    ClassFeature,
    ClassFeatureValue
)

class KnowledgeBase:
    def __init__(self):
        try:
            create_tables()
            self.initialize_default_data()
        except Exception as e:
            print(f"Ошибка инициализации базы знаний: {e}. Используется JSON-фоллбек.")

    def initialize_default_data(self):
        session = SessionLocal()
        try:
            if (
                session.query(MalwareClass).count() == 0
                or session.query(DiagnosticFeature).count() == 0
                or session.query(ClassFeature).count() == 0
                or session.query(ClassFeatureValue).count() == 0
            ):
                init_database_from_json()
        finally:
            session.close()

    def _get_class(self, class_name, session):
        return session.query(MalwareClass).filter_by(name=class_name).first()

    def _get_feature(self, feature_name, session):
        return session.query(DiagnosticFeature).filter_by(name=feature_name).first()

    def get_classes(self):
        session = SessionLocal()
        try:
            classes = [cls.name for cls in session.query(MalwareClass).order_by(MalwareClass.name).all()]
            if not classes:
                classes = self._load_json_data('classes.json')
            return classes
        except SQLAlchemyError:
            return self._load_json_data('classes.json')
        finally:
            session.close()

    def get_features(self):
        session = SessionLocal()
        try:
            features = [feature.name for feature in session.query(DiagnosticFeature).order_by(DiagnosticFeature.name).all()]
            if not features:
                features = self._load_json_data('features.json')
            return features
        except SQLAlchemyError:
            return self._load_json_data('features.json')
        finally:
            session.close()

    def get_feature_types(self):
        session = SessionLocal()
        try:
            result = {feature.name: feature.feature_type for feature in session.query(DiagnosticFeature).all()}
            default_types = self._load_json_data('feature_types.json')
            if not result:
                result = default_types
            else:
                for feature_name, feature_type in default_types.items():
                    result.setdefault(feature_name, feature_type)
            return result
        except SQLAlchemyError:
            return self._load_json_data('feature_types.json')
        finally:
            session.close()

    def get_valid_ranges(self):
        session = SessionLocal()
        try:
            ranges = {}
            for item in session.query(ValueRange).all():
                ranges[item.feature.name] = [float(item.min_value), float(item.max_value)]
            default_valid_ranges = self._load_json_data('ranges.json').get('valid_ranges', {})
            for feature_name, value in default_valid_ranges.items():
                if feature_name not in ranges:
                    ranges[feature_name] = list(value)
            return ranges
        except SQLAlchemyError:
            return self._load_json_data('ranges.json').get('valid_ranges', {})
        finally:
            session.close()

    def get_normal_ranges(self):
        session = SessionLocal()
        try:
            ranges = {}
            for item in session.query(NormalRange).all():
                ranges[item.feature.name] = [float(item.min_value), float(item.max_value)]
            default_normal_ranges = self._load_json_data('ranges.json').get('normal_ranges', {})
            for feature_name, value in default_normal_ranges.items():
                if feature_name not in ranges:
                    ranges[feature_name] = list(value)
            return ranges
        except SQLAlchemyError:
            return self._load_json_data('ranges.json').get('normal_ranges', {})
        finally:
            session.close()

    def _load_json_data(self, filename):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
            return json.load(f).get('data', {})

    def get_class_features(self):
        session = SessionLocal()
        try:
            result = {}
            for cls in session.query(MalwareClass).all():
                result[cls.name] = [feature.name for feature in cls.features]
            default_features = self._load_json_data('class_features.json')
            for class_name, features in default_features.items():
                if class_name not in result:
                    result[class_name] = list(features)
                else:
                    for feature in features:
                        if feature not in result[class_name]:
                            result[class_name].append(feature)
            return result
        except SQLAlchemyError:
            return self._load_json_data('class_features.json')
        finally:
            session.close()

    def get_class_values(self):
        session = SessionLocal()
        try:
            result = {}
            for item in session.query(ClassFeatureValue).all():
                class_name = item.malware_class.name
                feature_name = item.feature.name
                result.setdefault(class_name, {})
                result[class_name][feature_name] = [float(item.min_value), float(item.max_value)]
            default_values = self._load_json_data('class_values.json')
            for class_name, values in default_values.items():
                if class_name not in result:
                    result[class_name] = {k: list(v) for k, v in values.items()}
                else:
                    for feature_name, value in values.items():
                        result[class_name].setdefault(feature_name, list(value))
            return result
        except SQLAlchemyError:
            return self._load_json_data('class_values.json')
        finally:
            session.close()

    def add_class(self, class_name):
        session = SessionLocal()
        try:
            if not self._get_class(class_name, session):
                session.add(MalwareClass(name=class_name))
                session.commit()
        finally:
            session.close()

    def remove_class(self, class_name):
        session = SessionLocal()
        try:
            cls = self._get_class(class_name, session)
            if cls:
                session.query(ClassFeature).filter_by(class_id=cls.id).delete()
                session.query(ClassFeatureValue).filter_by(class_id=cls.id).delete()
                session.delete(cls)
                session.commit()
        finally:
            session.close()

    def add_feature(self, feature_name, feature_type='integer'):
        session = SessionLocal()
        try:
            if not self._get_feature(feature_name, session):
                session.add(DiagnosticFeature(name=feature_name, feature_type=feature_type))
                session.commit()
        finally:
            session.close()

    def remove_feature(self, feature_name):
        session = SessionLocal()
        try:
            feature = self._get_feature(feature_name, session)
            if feature:
                session.query(ClassFeature).filter_by(feature_id=feature.id).delete()
                session.query(ClassFeatureValue).filter_by(feature_id=feature.id).delete()
                session.query(ValueRange).filter_by(feature_id=feature.id).delete()
                session.query(NormalRange).filter_by(feature_id=feature.id).delete()
                session.delete(feature)
                session.commit()
        finally:
            session.close()

    def set_feature_type(self, feature_name, feature_type):
        session = SessionLocal()
        try:
            feature = self._get_feature(feature_name, session)
            if feature:
                feature.feature_type = feature_type
            else:
                session.add(DiagnosticFeature(name=feature_name, feature_type=feature_type))
            session.commit()
        finally:
            session.close()

    def set_valid_range(self, feature_name, min_value, max_value):
        session = SessionLocal()
        try:
            feature = self._get_feature(feature_name, session)
            if feature:
                range_item = session.query(ValueRange).filter_by(feature_id=feature.id).first()
                if range_item:
                    range_item.min_value = min_value
                    range_item.max_value = max_value
                else:
                    session.add(ValueRange(feature_id=feature.id, min_value=min_value, max_value=max_value))
                session.commit()
        finally:
            session.close()

    def set_normal_range(self, feature_name, min_value, max_value):
        session = SessionLocal()
        try:
            feature = self._get_feature(feature_name, session)
            if feature:
                range_item = session.query(NormalRange).filter_by(feature_id=feature.id).first()
                if range_item:
                    range_item.min_value = min_value
                    range_item.max_value = max_value
                else:
                    session.add(NormalRange(feature_id=feature.id, min_value=min_value, max_value=max_value))
                session.commit()
        finally:
            session.close()

    def set_class_features(self, class_name, feature_names):
        session = SessionLocal()
        try:
            cls = self._get_class(class_name, session)
            if not cls:
                return
            session.query(ClassFeature).filter_by(class_id=cls.id).delete()
            for feature_name in feature_names:
                feature = self._get_feature(feature_name, session)
                if feature:
                    session.add(ClassFeature(class_id=cls.id, feature_id=feature.id))
            session.commit()
        finally:
            session.close()

    def set_class_values(self, class_name, values):
        session = SessionLocal()
        try:
            cls = self._get_class(class_name, session)
            if not cls:
                return
            session.query(ClassFeatureValue).filter_by(class_id=cls.id).delete()
            for feature_name, value in values.items():
                feature = self._get_feature(feature_name, session)
                if feature and isinstance(value, list):
                    min_val = float(value[0])
                    max_val = float(value[1]) if len(value) > 1 else float(value[0])
                    session.add(ClassFeatureValue(class_id=cls.id, feature_id=feature.id, min_value=min_val, max_value=max_val))
            session.commit()
        finally:
            session.close()

    def set_classes(self, class_names):
        session = SessionLocal()
        try:
            existing = {cls.name: cls for cls in session.query(MalwareClass).all()}
            for class_name in class_names:
                if class_name not in existing:
                    session.add(MalwareClass(name=class_name))
            for class_name, cls in existing.items():
                if class_name not in class_names:
                    session.query(ClassFeature).filter_by(class_id=cls.id).delete()
                    session.query(ClassFeatureValue).filter_by(class_id=cls.id).delete()
                    session.delete(cls)
            session.commit()
        finally:
            session.close()

    def set_features(self, feature_names):
        session = SessionLocal()
        try:
            existing = {feature.name: feature for feature in session.query(DiagnosticFeature).all()}
            for feature_name in feature_names:
                if feature_name not in existing:
                    session.add(DiagnosticFeature(name=feature_name, feature_type='integer'))
            for feature_name, feature in existing.items():
                if feature_name not in feature_names:
                    session.query(ClassFeature).filter_by(feature_id=feature.id).delete()
                    session.query(ClassFeatureValue).filter_by(feature_id=feature.id).delete()
                    session.query(ValueRange).filter_by(feature_id=feature.id).delete()
                    session.query(NormalRange).filter_by(feature_id=feature.id).delete()
                    session.delete(feature)
            session.commit()
        finally:
            session.close()

    def set_feature_types(self, types_data):
        session = SessionLocal()
        try:
            for feature_name, ftype in types_data.items():
                feature = self._get_feature(feature_name, session)
                if feature:
                    feature.feature_type = ftype
                else:
                    session.add(DiagnosticFeature(name=feature_name, feature_type=ftype))
            session.commit()
        finally:
            session.close()

    def set_valid_ranges(self, ranges_data):
        for feature, bounds in ranges_data.items():
            self.set_valid_range(feature, bounds[0], bounds[1])

    def set_normal_ranges(self, ranges_data):
        for feature, bounds in ranges_data.items():
            self.set_normal_range(feature, bounds[0], bounds[1])

    def set_all_class_features(self, class_features_data):
        for class_name, feature_list in class_features_data.items():
            self.set_class_features(class_name, feature_list)

    def set_all_class_values(self, class_values_data):
        for class_name, values in class_values_data.items():
            self.set_class_values(class_name, values)

    def import_data(self, data_type, data):
        if data_type == 'classes':
            self.set_classes(data)
        elif data_type == 'features':
            self.set_features(data)
        elif data_type == 'feature_types':
            self.set_feature_types(data)
        elif data_type == 'valid_ranges':
            self.set_valid_ranges(data)
        elif data_type == 'normal_ranges':
            self.set_normal_ranges(data)
        elif data_type == 'class_features':
            self.set_all_class_features(data)
        elif data_type == 'class_values':
            self.set_all_class_values(data)
