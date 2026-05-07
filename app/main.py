import tkinter as tk
from tkinter import ttk, messagebox
from knowledge_base import KnowledgeBase
from diagnostic_engine import DiagnosticEngine
from llm_helper import LLMHelper
from tinydb import Query

class KnowledgeEditor:
    def __init__(self, root, kb):
        self.root = root
        self.kb = kb
        self.root.title("Редактор базы знаний")
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

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

    def create_classes_tab(self, parent):
        listbox = tk.Listbox(parent)
        listbox.pack(side=tk.LEFT, fill=tk.Y)
        for cls in self.kb.get_classes():
            listbox.insert(tk.END, cls)

        frame_right = ttk.Frame(parent)
        frame_right.pack(side=tk.RIGHT, fill=tk.Y)

        entry = ttk.Entry(frame_right)
        entry.pack()

        btn_add = ttk.Button(frame_right, text='Добавить', command=lambda: self.add_class(entry, listbox))
        btn_add.pack()

        btn_remove = ttk.Button(frame_right, text='Удалить', command=lambda: self.remove_class(listbox))
        btn_remove.pack()

    def add_class(self, entry, listbox):
        name = entry.get().strip()
        if name:
            self.kb.add_class(name)
            listbox.insert(tk.END, name)
            entry.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Введите название класса")

    def remove_class(self, listbox):
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection)
            self.kb.remove_class(name)
            listbox.delete(selection)

    def create_features_tab(self, parent):
        listbox = tk.Listbox(parent)
        listbox.pack(side=tk.LEFT, fill=tk.Y)
        for feat in self.kb.get_features():
            listbox.insert(tk.END, feat)

        frame_right = ttk.Frame(parent)
        frame_right.pack(side=tk.RIGHT, fill=tk.Y)

        entry = ttk.Entry(frame_right)
        entry.pack()

        btn_add = ttk.Button(frame_right, text='Добавить', command=lambda: self.add_feature(entry, listbox))
        btn_add.pack()

        btn_remove = ttk.Button(frame_right, text='Удалить', command=lambda: self.remove_feature(listbox))
        btn_remove.pack()

    def add_feature(self, entry, listbox):
        name = entry.get().strip()
        if name:
            features = self.kb.get_features()
            if name not in features:
                features.append(name)
                self.kb.db.update({'data': features}, Query().type == 'features')
                listbox.insert(tk.END, name)
            entry.delete(0, tk.END)
        else:
            messagebox.showerror("Ошибка", "Введите название признака")

    def remove_feature(self, listbox):
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection)
            features = self.kb.get_features()
            if name in features:
                features.remove(name)
                self.kb.db.update({'data': features}, Query().type == 'features')
                listbox.delete(selection)

    def create_valid_tab(self, parent):
        # Выбор признака и типа
        ttk.Label(parent, text='Выберите признак:').pack()
        feature_var = tk.StringVar()
        feature_combo = ttk.Combobox(parent, textvariable=feature_var, values=self.kb.get_features())
        feature_combo.pack()

        ttk.Label(parent, text='Тип:').pack()
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(parent, textvariable=type_var, values=['integer', 'real', 'boolean'])
        type_combo.pack()

        ttk.Label(parent, text='Диапазон (мин макс):').pack()
        range_entry = ttk.Entry(parent)
        range_entry.pack()

        btn_set = ttk.Button(parent, text='Установить', command=lambda: self.set_valid(feature_var.get(), type_var.get(), range_entry.get()))
        btn_set.pack()

    def set_valid(self, feature, ftype, range_str):
        if not feature or not ftype:
            messagebox.showerror("Ошибка", "Выберите признак и тип")
            return
        types = self.kb.get_feature_types()
        types[feature] = ftype
        self.kb.db.update({'data': types}, Query().type == 'feature_types')

        ranges = self.kb.get_valid_ranges()
        if ftype == 'boolean':
            ranges[feature] = [0, 1]
        else:
            try:
                min_val, max_val = map(float, range_str.split())
                ranges[feature] = [min_val, max_val]
            except:
                messagebox.showerror("Ошибка", "Неверный диапазон")
                return
        self.kb.db.update({'data': ranges}, Query().type == 'valid_ranges')
        messagebox.showinfo("Успех", "Допустимые значения установлены")

    def create_class_features_tab(self, parent):
        ttk.Label(parent, text='Выберите класс:').pack()
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(parent, textvariable=class_var, values=self.kb.get_classes())
        class_combo.pack()

        listbox = tk.Listbox(parent, selectmode=tk.MULTIPLE)
        listbox.pack(fill=tk.Y)

        btn_load = ttk.Button(parent, text='Загрузить признаки', command=lambda: self.load_class_features(class_var.get(), listbox))
        btn_load.pack()

        btn_save = ttk.Button(parent, text='Сохранить', command=lambda: self.save_class_features(class_var.get(), listbox))
        btn_save.pack()

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
        class_features = self.kb.get_class_features()
        class_features[cls] = selected
        self.kb.db.update({'data': class_features}, Query().type == 'class_features')
        messagebox.showinfo("Успех", "Признаки сохранены")

    def create_class_values_tab(self, parent):
        ttk.Label(parent, text='Выберите класс:').pack()
        class_var = tk.StringVar()
        class_combo = ttk.Combobox(parent, textvariable=class_var, values=self.kb.get_classes())
        class_combo.pack()

        self.values_frame = ttk.Frame(parent)
        self.values_frame.pack(fill=tk.BOTH)

        btn_load = ttk.Button(parent, text='Загрузить значения', command=lambda: self.load_class_values(class_var.get()))
        btn_load.pack()

        btn_save = ttk.Button(parent, text='Сохранить', command=lambda: self.save_class_values(class_var.get()))
        btn_save.pack()

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
            frame = ttk.Frame(self.values_frame)
            frame.pack(fill=tk.X)
            ttk.Label(frame, text=feat).pack(side=tk.LEFT)
            ftype = types.get(feat, 'integer')
            if ftype == 'boolean':
                var = tk.IntVar(value=class_values.get(feat, [0])[0])
                ttk.Checkbutton(frame, variable=var).pack(side=tk.RIGHT)
                self.value_entries[feat] = var
            else:
                entry = ttk.Entry(frame)
                entry.insert(0, f"{class_values.get(feat, [0, 0])[0]} {class_values.get(feat, [0, 0])[1]}")
                entry.pack(side=tk.RIGHT)
                self.value_entries[feat] = entry

    def save_class_values(self, cls):
        if not cls:
            messagebox.showerror("Ошибка", "Выберите класс")
            return
        values = {}
        for feat, widget in self.value_entries.items():
            if isinstance(widget, tk.IntVar):
                values[feat] = [widget.get()]
            else:
                try:
                    min_val, max_val = map(float, widget.get().split())
                    values[feat] = [min_val, max_val]
                except:
                    messagebox.showerror("Ошибка", f"Неверный диапазон для {feat}")
                    return
        class_values = self.kb.get_class_values()
        class_values[cls] = values
        self.kb.db.update({'data': class_values}, Query().type == 'class_values')
        messagebox.showinfo("Успех", "Значения сохранены")

class InputSystem:
    def __init__(self, root, kb, engine, llm):
        self.root = root
        self.kb = kb
        self.engine = engine
        self.llm = llm
        self.root.title("Ввод исходных данных")
        self.create_widgets()

    def create_widgets(self):
        features = self.kb.get_features()
        feature_types = self.kb.get_feature_types()

        self.entries = {}
        for feature in features:
            frame = ttk.Frame(self.root)
            frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(frame, text=feature).pack(side=tk.LEFT)

            ftype = feature_types.get(feature, 'integer')
            if ftype == 'boolean':
                var = tk.IntVar()
                ttk.Checkbutton(frame, variable=var).pack(side=tk.RIGHT)
                self.entries[feature] = var
            else:
                entry = ttk.Entry(frame)
                entry.pack(side=tk.RIGHT)
                self.entries[feature] = entry

        btn_diagnose = ttk.Button(self.root, text='Начать диагностику', command=self.diagnose)
        btn_diagnose.pack(pady=10)

        btn_view_kb = ttk.Button(self.root, text='Просмотреть базу знаний', command=self.view_kb)
        btn_view_kb.pack(pady=5)

        self.result_label = ttk.Label(self.root, text='', wraplength=400)
        self.result_label.pack()

    def view_kb(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Просмотр базы знаний")

        text = tk.Text(view_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)

        kb_info = f"Классы: {self.kb.get_classes()}\n\n"
        kb_info += f"Признаки: {self.kb.get_features()}\n\n"
        kb_info += f"Признаки классов: {self.kb.get_class_features()}\n\n"
        kb_info += f"Значения классов: {self.kb.get_class_values()}\n"

        text.insert(tk.END, kb_info)
        text.config(state=tk.DISABLED)

    def diagnose(self):
        input_values = {}
        for feature, widget in self.entries.items():
            if isinstance(widget, tk.IntVar):
                value = widget.get()
            else:
                try:
                    value = float(widget.get())
                except ValueError:
                    messagebox.showerror("Ошибка", f"Неверное значение для {feature}")
                    return
            input_values[feature] = value

        diagnosis = self.engine.diagnose(input_values)
        explanation = self.llm.generate_explanation(diagnosis, input_values)
        self.result_label.config(text=f'Диагноз: {diagnosis}\nОбъяснение: {explanation}')

class MainApp:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.engine = DiagnosticEngine(self.kb)
        self.llm = LLMHelper()

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
        InputSystem(input_window, self.kb, self.engine, self.llm)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = MainApp()
    app.run()