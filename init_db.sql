-- Таблица для хранения классов вредоносного ПО
CREATE TABLE IF NOT EXISTS malware_classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения диагностических признаков
CREATE TABLE IF NOT EXISTS diagnostic_features (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    feature_type VARCHAR(20) NOT NULL CHECK (feature_type IN ('integer', 'real', 'boolean')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения диапазонов значений
CREATE TABLE IF NOT EXISTS value_ranges (
    id SERIAL PRIMARY KEY,
    feature_id INTEGER NOT NULL UNIQUE,
    min_value DECIMAL(10, 2) NOT NULL,
    max_value DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (feature_id) REFERENCES diagnostic_features(id) ON DELETE CASCADE
);

-- Таблица для хранения нормальных диапазонов
CREATE TABLE IF NOT EXISTS normal_ranges (
    id SERIAL PRIMARY KEY,
    feature_id INTEGER NOT NULL UNIQUE,
    min_value DECIMAL(10, 2) NOT NULL,
    max_value DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (feature_id) REFERENCES diagnostic_features(id) ON DELETE CASCADE
);

-- Таблица для связи классов и их признаков
CREATE TABLE IF NOT EXISTS class_features (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    feature_id INTEGER NOT NULL,
    FOREIGN KEY (class_id) REFERENCES malware_classes(id) ON DELETE CASCADE,
    FOREIGN KEY (feature_id) REFERENCES diagnostic_features(id) ON DELETE CASCADE,
    UNIQUE(class_id, feature_id)
);

-- Таблица для хранения значений признаков классов
CREATE TABLE IF NOT EXISTS class_feature_values (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    feature_id INTEGER NOT NULL,
    min_value DECIMAL(20, 2) NOT NULL,
    max_value DECIMAL(20, 2) NOT NULL,
    FOREIGN KEY (class_id) REFERENCES malware_classes(id) ON DELETE CASCADE,
    FOREIGN KEY (feature_id) REFERENCES diagnostic_features(id) ON DELETE CASCADE,
    UNIQUE(class_id, feature_id)
);

-- Таблица для логирования диагностики
CREATE TABLE IF NOT EXISTS diagnosis_logs (
    id SERIAL PRIMARY KEY,
    class_id INTEGER,
    cpu_load INTEGER,
    memory_usage INTEGER,
    network_traffic DECIMAL(10, 2),
    file_operations DECIMAL(20, 2),
    remote_management SMALLINT,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES malware_classes(id) ON DELETE SET NULL
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_malware_classes_name ON malware_classes(name);
CREATE INDEX idx_diagnostic_features_name ON diagnostic_features(name);
CREATE INDEX idx_diagnosis_logs_created_at ON diagnosis_logs(created_at);
CREATE INDEX idx_class_features_class_id ON class_features(class_id);
CREATE INDEX idx_class_features_feature_id ON class_features(feature_id);

-- Вставка базовых данных
INSERT INTO malware_classes (name) VALUES
  ('File injector virus'),
  ('Network worm'),
  ('Trojan downloader'),
  ('Remote Access Trojan'),
  ('Banking Trojan'),
  ('Crypto-ransomware'),
  ('Wiper'),
  ('Cryptominer'),
  ('Botnet agent'),
  ('Rootkit'),
  ('Чистая система')
ON CONFLICT (name) DO NOTHING;

INSERT INTO diagnostic_features (name, feature_type) VALUES
  ('средняя загрузка процессора', 'integer'),
  ('использование оперативной памяти', 'integer'),
  ('исходящий сетевой трафик', 'real'),
  ('операции изменения файлов', 'real'),
  ('наличие устойчивого удаленного управления', 'boolean')
ON CONFLICT (name) DO NOTHING;
