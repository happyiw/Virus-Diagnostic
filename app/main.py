import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.knowledge_base import KnowledgeBase
from app.diagnostic_engine import DiagnosticEngine
import json

class KnowledgeEditor:
    def __init__(self, root, kb):
        self.feature_combo_valid = None
        self.class_combo_cf = None
        self.class_combo_cv = None
        self.current_class_values = None
        self.current_class_features_listbox = None
        self.current_feature_listbox = None
        self.value_entries = {}
        self.root = root
        self.kb = kb
        self.root.title("Редактор базы знаний")
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=8, pady=8)

        # Вкладка классов
        frame_classes = ttk.Frame(notebook)
        notebook.add(frame_classes, text='Классы ПО')
        self.create_classes_tab(frame_classes)

        # Вкладка признаков
        frame_features = ttk.Frame(notebook)
        notebook.add(frame_features, text='Диагностические признаки')
        self.create_features_tab(frame_features)

        # Вкладка допустимых значений
        frame_valid = ttk.Frame(notebook)
        notebook.add(frame_valid, text='Допустимые значения')
        self.create_valid_tab(frame_valid)

        # Вкладка признаков класса
        frame_class_features = ttk.Frame(notebook)
        notebook.add(frame_class_features, text='Признаки класса')
        self.create_class_features_tab(frame_class_features)

        # Вкладка значений для класса
        frame_class_values = ttk.Frame(notebook)
        notebook.add(frame_class_values, text='Значения для класса')
        self.create_class_values_tab(frame_class_values)

    def refresh_feature_comboboxes(self):
        feature_values = self.kb.get_features()
        if self.feature_combo_valid is not None:
            self.feature_combo_valid.config(values=feature_values)
        if self.current_feature_listbox is not None:
            self.current_feature_listbox.delete(0, tk.END)
            for feat in feature_values:
                self.current_feature_listbox.insert(tk.END, feat)

    def refresh_class_comboboxes(self):
        class_values = self.kb.get_classes()
        if self.class_combo_cf is not None:
            self.class_combo_cf.config(values=class_values)
        if self.class_combo_cv is not None:
            self.class_combo_cv.config(values=class_values)

    def refresh_all(self):
        self.refresh_feature_comboboxes()
        self.refresh_class_comboboxes()

    def create_classes_tab(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(left_frame, text='Список классов:').pack(anchor=tk.W)

        listbox = tk.Listbox(left_frame, height=12)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        for cls in self.kb.get_classes():
            listbox.insert(tk.END, cls)

        right_frame = ttk.Frame(container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        ttk.Label(right_frame, text='Новый класс:').pack(anchor=tk.W)
        entry = ttk.Entry(right_frame, width=30)
        entry.pack(pady=(0, 8))

        btn_add = ttk.Button(right_frame, text='Добавить', command=lambda: self.add_class(entry, listbox))
        btn_add.pack(fill=tk.X, pady=2)

        btn_remove = ttk.Button(right_frame, text='Удалить', command=lambda: self.remove_class(listbox))
        btn_remove.pack(fill=tk.X, pady=2)

        btn_refresh = ttk.Button(right_frame, text='Обновить списки', command=self.refresh_all)
        btn_refresh.pack(fill=tk.X, pady=(20, 2))

        btn_import = ttk.Button(right_frame, text='Импорт из JSON', command=lambda: self.import_json('classes'))
        btn_import.pack(fill=tk.X, pady=2)

    def add_class(self, entry, listbox):
        name = entry.get().strip()
        if name:
            self.kb.add_class(name)
            listbox.insert(tk.END, name)
            entry.delete(0, tk.END)
            self.refresh_class_comboboxes()
        else:
            messagebox.showerror("Ошибка", "Введите название класса")

    def remove_class(self, listbox):
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection)
            self.kb.remove_class(name)
            listbox.delete(selection)
            self.refresh_class_comboboxes()

    def create_features_tab(self, parent):
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(left_frame, text='Список признаков:').pack(anchor=tk.W)

        listbox = tk.Listbox(left_frame, height=12)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        self.current_feature_listbox = listbox

        for feat in self.kb.get_features():
            listbox.insert(tk.END, feat)

        right_frame = ttk.Frame(container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        ttk.Label(right_frame, text='Новый признак:').pack(anchor=tk.W)
        entry = ttk.Entry(right_frame, width=30)
        entry.pack(pady=(0, 8))

        btn_add = ttk.Button(right_frame, text='Добавить', command=lambda: self.add_feature(entry, listbox))
        btn_add.pack(fill=tk.X, pady=2)

        btn_remove = ttk.Button(right_frame, text='Удалить', command=lambda: self.remove_feature(listbox))
        btn_remove.pack(fill=tk.X, pady=2)

        btn_refresh = ttk.Button(right_frame, text='Обновить списки', command=self.refresh_feature_comboboxes)
        btn_refresh.pack(fill=tk.X, pady=(20, 2))

        btn_import = ttk.Button(right_frame, text='Импорт из JSON', command=lambda: self.import_json('features'))
        btn_import.pack(fill=tk.X, pady=2)

    def add_feature(self, entry, listbox):
        name = entry.get().strip()
        if name:
            features = self.kb.get_features()
            if name not in features:
                self.kb.add_feature(name)
                listbox.insert(tk.END, name)
                self.refresh_feature_comboboxes()
            entry.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Введите название признака")

    def remove_feature(self, listbox):
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection)
            self.kb.remove_feature(name)
            listbox.delete(selection)
            self.refresh_feature_comboboxes()

    def create_valid_tab(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text='Выберите признак:').grid(row=0, column=0, sticky=tk.W, pady=4)
        feature_var = tk.StringVar()
        feature_combo = ttk.Combobox(frame, textvariable=feature_var, values=self.kb.get_features(), state='readonly')
        feature_combo.grid(row=0, column=1, sticky=tk.EW, pady=4)
        self.feature_combo_valid = feature_combo

        ttk.Label(frame, text='Тип:').grid(row=1, column=0, sticky=tk.W, pady=4)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(frame, textvariable=type_var, values=['integer', 'real', 'boolean'], state='readonly')
        type_combo.grid(row=1, column=1, sticky=tk.EW, pady=4)

        ttk.Label(frame, text='Минимальное значение:').grid(row=2, column=0, sticky=tk.W, pady=4)
        min_entry = ttk.Entry(frame)
        min_entry.grid(row=2, column=1, sticky=tk.EW, pady=4)

        ttk.Label(frame, text='Максимальное значение:').grid(row=3, column=0, sticky=tk.W, pady=4)
        max_entry = ttk.Entry(frame)
        max_entry.grid(row=3, column=1, sticky=tk.EW, pady=4)

        btn_set = ttk.Button(frame, text='Установить', command=lambda: self.set_valid(feature_var.get(), type_var.get(), min_entry.get(), max_entry.get()))
        btn_set.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=10)

        btn_load = ttk.Button(frame, text='Загрузить текущие значения', command=lambda: self.load_valid_range(feature_var.get(), type_var, min_entry, max_entry))
        btn_load.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=2)

        btn_import = ttk.Button(frame, text='Импорт из JSON', command=lambda: self.import_json('valid_ranges'))
        btn_import.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=10)

    def set_valid(self, feature, ftype, min_str, max_str):
        if not feature or not ftype:
            messagebox.showerror("Ошибка", "Выберите признак и тип")
            return
        self.kb.set_feature_type(feature, ftype)

        if ftype == 'boolean':
            min_val = 0
            max_val = 1
        else:
            try:
                min_val = float(min_str)
                max_val = float(max_str)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный диапазон")
                return

        self.kb.set_valid_range(feature, min_val, max_val)
        messagebox.showinfo("Успех", "Допустимые значения установлены")

    def load_valid_range(self, feature, type_var, min_entry, max_entry):
        if not feature:
            messagebox.showerror("Ошибка", "Выберите признак для загрузки")
            return
        valid_ranges = self.kb.get_valid_ranges().get(feature)
        if valid_ranges is None:
            messagebox.showerror("Ошибка", "Диапазон для выбранного признака не задан")
            return
        if self.kb.get_feature_types().get(feature) == 'boolean':
            type_var.set('boolean')
            min_entry.delete(0, tk.END)
            max_entry.delete(0, tk.END)
            min_entry.insert(0, '0')
            max_entry.insert(0, '1')
        else:
            type_var.set(self.kb.get_feature_types().get(feature, 'integer'))
            min_entry.delete(0, tk.END)
            max_entry.delete(0, tk.END)
            min_entry.insert(0, str(valid_ranges[0]))
            max_entry.insert(0, str(valid_ranges[1]))

    def create_class_features_tab(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text='Выберите класс:').pack(anchor=tk.W)
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(frame, textvariable=class_var, values=self.kb.get_classes(), state='readonly')
        class_combo.pack(fill=tk.X, pady=4)
        self.class_combo_cf = class_combo

        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, height=12)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)
        class_combo.bind('<<ComboboxSelected>>', lambda event: self.load_class_features(class_var.get(), listbox))

        btn_load = ttk.Button(frame, text='Загрузить признаки', command=lambda: self.load_class_features(class_var.get(), listbox))
        btn_load.pack(fill=tk.X, pady=4)

        btn_save = ttk.Button(frame, text='Сохранить', command=lambda: self.save_class_features(class_var.get(), listbox))
        btn_save.pack(fill=tk.X, pady=4)

        btn_import = ttk.Button(frame, text='Импорт из JSON', command=lambda: self.import_json('class_features'))
        btn_import.pack(fill=tk.X, pady=4)

    def load_class_features(self, cls, listbox):
        if not cls:
            return
        class_features = self.kb.get_class_features()
        features = class_features.get(cls, [])
        listbox.delete(0, tk.END)
        for feat in self.kb.get_features():
            listbox.insert(tk.END, feat)
            if feat in features:
                listbox.select_set(listbox.size() - 1)

    def save_class_features(self, cls, listbox):
        if not cls:
            messagebox.showerror("Ошибка", "Выберите класс")
            return
        selected = [listbox.get(i) for i in listbox.curselection()]
        self.kb.set_class_features(cls, selected)
        messagebox.showinfo("Успех", "Признаки сохранены")

    def create_class_values_tab(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text='Выберите класс:').pack(anchor=tk.W)
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(frame, textvariable=class_var, values=self.kb.get_classes(), state='readonly')
        class_combo.pack(fill=tk.X, pady=4)
        self.class_combo_cv = class_combo
        class_combo.bind('<<ComboboxSelected>>', lambda event: self.load_class_values(class_var.get()))

        self.values_frame = ttk.Frame(frame)
        self.values_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        btn_load = ttk.Button(frame, text='Загрузить значения', command=lambda: self.load_class_values(class_var.get()))
        btn_load.pack(fill=tk.X, pady=4)

        btn_save = ttk.Button(frame, text='Сохранить', command=lambda: self.save_class_values(class_var.get()))
        btn_save.pack(fill=tk.X, pady=4)

        btn_import = ttk.Button(frame, text='Импорт из JSON', command=lambda: self.import_json('class_values'))
        btn_import.pack(fill=tk.X, pady=4)

    def load_class_values(self, cls):
        if not cls:
            return
        for widget in self.values_frame.winfo_children():
            widget.destroy()

        class_values = self.kb.get_class_values().get(cls, {})
        features = self.kb.get_class_features().get(cls, [])
        types = self.kb.get_feature_types()

        self.value_entries = {}
        for feat in features:
            ftype = types.get(feat, 'integer')
            if ftype == 'boolean':
                frame = ttk.Frame(self.values_frame)
                frame.pack(fill=tk.X)
                ttk.Label(frame, text=feat).pack(side=tk.LEFT)
                var = tk.IntVar(value=class_values.get(feat, [0])[0])
                ttk.Checkbutton(frame, variable=var).pack(side=tk.RIGHT)
                self.value_entries[feat] = var
            else:
                # Минимум
                frame_min = ttk.Frame(self.values_frame)
                frame_min.pack(fill=tk.X)
                ttk.Label(frame_min, text=f"{feat} (мин):").pack(side=tk.LEFT)
                entry_min = ttk.Entry(frame_min, width=10)
                entry_min.insert(0, str(class_values.get(feat, [0, 0])[0]))
                entry_min.pack(side=tk.RIGHT)
                
                # Максимум
                frame_max = ttk.Frame(self.values_frame)
                frame_max.pack(fill=tk.X)
                ttk.Label(frame_max, text=f"{feat} (макс):").pack(side=tk.LEFT)
                entry_max = ttk.Entry(frame_max, width=10)
                entry_max.insert(0, str(class_values.get(feat, [0, 0])[1]))
                entry_max.pack(side=tk.RIGHT)
                
                self.value_entries[f"{feat}_min"] = entry_min
                self.value_entries[f"{feat}_max"] = entry_max

    def save_class_values(self, cls):
        if not cls:
            messagebox.showerror("Ошибка", "Выберите класс")
            return
        values = {}
        features = self.kb.get_class_features().get(cls, [])
        types = self.kb.get_feature_types()
        
        for feat in features:
            ftype = types.get(feat, 'integer')
            if ftype == 'boolean':
                widget = self.value_entries.get(feat)
                if isinstance(widget, tk.IntVar):
                    values[feat] = [widget.get()]
            else:
                try:
                    min_widget = self.value_entries.get(f"{feat}_min")
                    max_widget = self.value_entries.get(f"{feat}_max")
                    if min_widget is None or max_widget is None:
                        raise ValueError
                    min_val = float(min_widget.get())
                    max_val = float(max_widget.get())
                    values[feat] = [min_val, max_val]
                except Exception:
                    messagebox.showerror("Ошибка", f"Неверный диапазон для {feat}")
                    return
        
        self.kb.set_class_values(cls, values)
        messagebox.showinfo("Успех", "Значения сохранены")

    def import_json(self, data_type):
        """Импорт данных из JSON файла"""
        file_path = filedialog.askopenfilename(
            title=f"Выберите JSON файл для {data_type}",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'data' not in data:
                messagebox.showerror("Ошибка", "JSON файл должен содержать ключ 'data'")
                return
            
            # Обновляем базу данных
            self.kb.import_data(data_type, data['data'])
            
            # Обновляем интерфейс
            self.refresh_all()
            
            messagebox.showinfo("Успех", f"Данные {data_type} импортированы успешно")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при импорте: {str(e)}")

class InputSystem:
    def __init__(self, root, kb, engine):
        self.root = root
        self.kb = kb
        self.engine = engine
        self.root.title("Ввод исходных данных")
        self.create_widgets()

    def create_widgets(self):
        features = self.kb.get_features()
        feature_types = self.kb.get_feature_types()
        self.feature_types = feature_types
        self.valid_ranges = self.kb.get_valid_ranges()

        self.entries = {}
        content = ttk.Frame(self.root, padding=12)
        content.pack(fill=tk.BOTH, expand=True)

        for index, feature in enumerate(features):
            ttk.Label(content, text=feature).grid(row=index, column=0, sticky=tk.W, padx=(0, 6), pady=6)

            ftype = feature_types.get(feature, 'integer')
            if ftype == 'boolean':
                var = tk.IntVar()
                ttk.Checkbutton(content, variable=var).grid(row=index, column=1, sticky=tk.W, pady=6)
                self.entries[feature] = var
            else:
                entry = ttk.Entry(content, width=18)
                entry.grid(row=index, column=1, sticky=tk.W, pady=6)
                # bind focus out and key release to validate and auto-clamp the value
                entry.bind('<FocusOut>', lambda e, f=feature, w=entry: self._on_focus_out(f, w))
                entry.bind('<KeyRelease>', lambda e, f=feature, w=entry: self._on_key_release(f, w))
                self.entries[feature] = entry

        button_frame = ttk.Frame(content)
        button_frame.grid(row=len(features), column=0, columnspan=2, pady=(12, 0), sticky=tk.EW)

        btn_diagnose = ttk.Button(button_frame, text='Начать диагностику', command=self.diagnose)
        btn_diagnose.pack(side=tk.LEFT, padx=(0, 8))

        btn_view_kb = ttk.Button(button_frame, text='Просмотреть базу знаний', command=self.view_kb)
        btn_view_kb.pack(side=tk.LEFT)

        self.diagnosis_label = ttk.Label(content, text='', font=('Arial', 11, 'bold'), wraplength=520)
        self.diagnosis_label.grid(row=len(features) + 1, column=0, columnspan=2, pady=(16, 6), sticky=tk.W)

        ttk.Label(content, text='Отклонённые гипотезы:', font=('Arial', 10, 'underline')).grid(row=len(features) + 2, column=0, columnspan=2, sticky=tk.W)
        self.rejected_text = tk.Text(content, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.rejected_text.grid(row=len(features) + 3, column=0, columnspan=2, sticky=tk.EW, pady=(4, 0))

    def view_kb(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Просмотр базы знаний")

        text = tk.Text(view_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)

        classes = self.kb.get_classes()
        features = self.kb.get_features()
        class_features = self.kb.get_class_features()
        class_values = self.kb.get_class_values()

        kb_info = f"Классы: {classes}\n\n"
        kb_info += f"Признаки: {features}\n\n"
        kb_info += "Признаки классов:\n"
        for cls, feats in class_features.items():
            kb_info += f"  {cls}: {feats}\n"
        kb_info += "\nЗначения классов:\n"
        for cls in classes:
            values = class_values.get(cls, {})
            if not values:
                kb_info += f"  {cls}: {{}}\n"
                continue
            kb_info += f"  {cls}:\n"
            for feat, val in values.items():
                kb_info += f"    {feat}: {val}\n"
        kb_info += "\n"

        text.insert(tk.END, kb_info)
        text.config(state=tk.DISABLED)

    def diagnose(self):
        input_values = {}
        feature_types = self.kb.get_feature_types()
        valid_ranges = self.kb.get_valid_ranges()

        # read and ensure all values are parsed and clamped (auto-clamping already applied on focus out)
        # allow missing inputs: skip empty fields instead of forcing user to fill all
        for feature, widget in self.entries.items():
            val = self._parse_and_clamp(feature, widget, show_error=False)
            if val is None:
                continue
            input_values[feature] = val

        # Проверка достаточности данных: нужно хотя бы одно совпадение введённых признаков с признаками какого-либо класса
        class_features = self.kb.get_class_features()
        provided = set(input_values.keys())
        max_overlap = 0
        for cls, feats in class_features.items():
            if cls == 'Чистая система':
                continue
            overlap = len(set(feats) & provided)
            if overlap > max_overlap:
                max_overlap = overlap

        if max_overlap == 0:
            messagebox.showerror("Недостаточно данных", "Недостаточно признаков для постановки диагноза. Введите значения хотя бы для одного признака, относящегося к классам.")
            return

        result = self.engine.diagnose(input_values)
        diagnosis = result.get('expert_diagnosis', 'Неизвестный класс')
        rejected = result.get('rejected', [])

        self.diagnosis_label.config(text=f'Диагноз экспертной системы: {diagnosis}')

        self.rejected_text.config(state=tk.NORMAL)
        self.rejected_text.delete('1.0', tk.END)
        if rejected:
            for item in rejected:
                self.rejected_text.insert(tk.END, f"- {item['class']}: {item['reason']}\n")
        else:
            self.rejected_text.insert(tk.END, 'Нет отклонённых гипотез для данной ситуации.')
        self.rejected_text.config(state=tk.DISABLED)

    def _on_focus_out(self, feature, widget):
        # called when an entry loses focus: silently parse and clamp
        try:
            self._parse_and_clamp(feature, widget, show_error=False)
        except Exception:
            pass

    def _on_key_release(self, feature, widget):
        # called on key release: attempt to parse and clamp only if the current input is a valid number
        try:
            # _parse_and_clamp is safe: it returns None on invalid partial input and does not modify widget
            self._parse_and_clamp(feature, widget, show_error=False)
        except Exception:
            pass

    def _parse_and_clamp(self, feature, widget, show_error=False):
        ftype = self.feature_types.get(feature, 'integer')
        valid_ranges = self.valid_ranges

        if isinstance(widget, tk.IntVar):
            value = widget.get()
        else:
            raw = widget.get().strip()
            if raw == '':
                if show_error:
                    messagebox.showerror("Ошибка", f"Введите значение для {feature}")
                return None
            try:
                value = float(raw)
            except ValueError:
                if show_error:
                    messagebox.showerror("Ошибка", f"Неверное значение для {feature}")
                return None

        if ftype == 'boolean':
            value = 1 if value else 0
        elif ftype == 'integer':
            value = int(round(value))

        if feature in valid_ranges:
            range_value = valid_ranges[feature]
            if isinstance(range_value, list) and len(range_value) >= 2:
                low, high = range_value[0], range_value[1]
                if value < low or value > high:
                    value = min(max(value, low), high)
                    # update widget with corrected value
                    if not isinstance(widget, tk.IntVar):
                        widget.delete(0, tk.END)
                        widget.insert(0, str(value))
                    else:
                        widget.set(value)

        return value

class MainApp:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.engine = DiagnosticEngine(self.kb)

        self.root = tk.Tk()
        self.root.title("Экспертная система диагностики ПО")

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        menu.add_command(label='Редактор знаний', command=self.open_editor)
        menu.add_command(label='Ввод данных', command=self.open_input)

    def open_editor(self):
        editor_window = tk.Toplevel(self.root)
        KnowledgeEditor(editor_window, self.kb)

    def open_input(self):
        input_window = tk.Toplevel(self.root)
        InputSystem(input_window, self.kb, self.engine)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = MainApp()
    app.run()