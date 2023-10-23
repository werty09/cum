import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
import csv
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging

# Задайте константу для пути к базе данных
DB_PATH = 'db.db'

# Другие константы
CSV_DEFAULT_EXTENSION = '.csv'
CSV_FILE_TYPES = [('CSV Files', f'*{CSV_DEFAULT_EXTENSION}')]

# Вместо хардкода пути в коде, используйте константы
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)

# Настройка логирования
logging.basicConfig(filename='my_app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Создание объекта SQLAlchemy Engine и сессии
db_path = 'db.db'
engine = create_engine(f'sqlite:///{db_path}', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Определение класса для отображения таблицы
class Employee(Base):
    __tablename__ = 'db'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tel = Column(String)
    email = Column(String)
    salary = Column(Float)

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        self.db = DB()
        self.view_records()

    def init_main(self):
        # Создаем панель инструментов
        toolbar = tk.Frame(bg='#d7d8eD', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_open_dialog = tk.Button(toolbar, text="Добавить сотрудника", command=self.open_child, bg='#d7d8e0')
        btn_open_dialog.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self, columns=('ID', 'name', 'tel', 'email', 'salary'), height=20, show='headings')
        self.tree.column("ID", width=30, anchor=tk.CENTER)
        self.tree.column("name", width=200, anchor=tk.CENTER)
        self.tree.column("tel", width=100, anchor=tk.CENTER)
        self.tree.column("email", width=150, anchor=tk.CENTER)
        self.tree.column("salary", width=100, anchor=tk.CENTER)

        self.tree.heading("ID", text='ID', command=lambda: self.sort_records('id'))
        self.tree.heading("name", text='ФИО', command=lambda: self.sort_records('name'))
        self.tree.heading("tel", text='Телефон', command=lambda: self.sort_records('tel'))
        self.tree.heading("email", text='E-mail', command=lambda: self.sort_records('email'))
        self.tree.heading("salary", text='Заработная плата', command=lambda: self.sort_records('salary'))

        self.tree.pack(side=tk.LEFT)

        btn_edit_dialog = tk.Button(toolbar, text="Редактировать сотрудника", command=self.open_update_dialog, bg='#d7d8e0')
        btn_edit_dialog.pack(side=tk.LEFT)

        btn_delete = tk.Button(toolbar, text="Удалить", command=self.delete_records, bg='#d7d8e0')
        btn_delete.pack(side=tk.LEFT)

        btn_search = tk.Button(toolbar, text="Поиск", command=self.open_search_dialog, bg='#d7d8e0')
        btn_search.pack(side=tk.LEFT)

    def open_search_dialog(self):
        Search(self)

    def search_records(self, name, tel, email):
        name = ('%' + name + '%',)
        tel = ('%' + tel + '%',)
        email = ('%' + email + '%')
        data = self.db.filter_data(name, tel, email)
        self.view_records(data)

    def delete_records(self):
        for selection_item in self.tree.selection():
            id = self.tree.set(selection_item, '#1')
            self.db.delete_data(id)
        self.view_records()

    def update_record(self, name, tel, email, salary):
        id = self.tree.set(self.tree.selection()[0], '#1')
        self.db.update_data(id, name, tel, email, salary)
        self.view_records()

    def open_update_dialog(self):
        selected_item = self.tree.selection()
        if selected_item:
            Update(self, selected_item[0])

    def open_child(self):
        Child(self)

    def records(self, name, tel, email, salary):
        self.db.insert_data(name, tel, email, salary)
        self.view_records()

    def view_records(self):
        data = self.db.get_all_data()
        self.populate_treeview(data)

    def sort_records(self, column):
        data = self.db.get_all_data_sorted(column)
        self.populate_treeview(data)

    def populate_treeview(self, data):
        [self.tree.delete(i) for i in self.tree.get_children()]
        for row in data:
            self.tree.insert('', 'end', values=row)

class Child(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.init_child()

    def init_child(self):
        self.title('Добавить сотрудника')
        self.geometry('400x220')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        label_name = tk.Label(self, text='ФИО:')
        label_name.place(x=50, y=50)
        label_select = tk.Label(self, text='Телефон:')
        label_select.place(x=50, y=80)
        label_email = tk.Label(self, text='E-mail:')
        label_email.place(x=50, y=110)
        label_salary = tk.Label(self, text='Заработная плата:')
        label_salary.place(x=50, y=140)

        self.entry_name = ttk.Entry(self)
        self.entry_name.place(x=200, y=50)

        self.entry_email = ttk.Entry(self)
        self.entry_email.place(x=200, y=80)

        self.entry_tel = ttk.Entry(self)
        self.entry_tel.place(x=200, y=110)

        self.entry_salary = ttk.Entry(self)
        self.entry_salary.place(x=200, y=140)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=300, y=170)

        btn_ok = ttk.Button(self, text='Добавить', command=self.add_record)
        btn_ok.place(x=220, y=170)

    def add_record(self):
        name = self.entry_name.get()
        email = self.entry_email.get()
        tel = self.entry_tel.get()
        salary = self.entry_salary.get()

        if name and email and tel and salary:
            self.app.records(name, tel, email, salary)
            self.destroy()
        else:
            messagebox.showerror('Ошибка', 'Заполните все поля')

class Update(Child):
    def __init__(self, app, selected_item):
        super().__init__(app)
        self.selected_item = selected_item
        self.init_edit()
        self.default_data()

    def init_edit(self):
        self.title('Редактировать сотрудника')
        btn_edit = ttk.Button(self, text='Редактировать', command=self.edit_record)
        btn_edit.place(x=205, y=170)

    def default_data(self):
        id = self.selected_item
        data = self.app.db.get_data(id)
        self.entry_name.insert(0, data[1])
        self.entry_email.insert(0, data[2])
        self.entry_tel.insert(0, data[3])
        self.entry_salary.insert(0, data[4])

    def edit_record(self):
        id = self.selected_item
        name = self.entry_name.get()
        email = self.entry_email.get()
        tel = self.entry_tel.get()
        salary = self.entry_salary.get()

        if name and email and tel and salary:
            self.app.update_record(name, tel, email, salary)
            self.destroy()
        else:
            messagebox.showerror('Ошибка', 'Заполните все поля')

class Search(tk.Toplevel):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.init_search()

    def init_search(self):
        self.title('Поиск')
        self.geometry('380x100')
        self.resizable(False, False)

        label_search = tk.Label(self, text='Поиск')
        label_search.place(x=50, y=20)

        self.entry_search = ttk.Entry(self)
        self.entry_search.place(x=105, y=20, width=150)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=105, y=50)

        btn_search = ttk.Button(self, text='Поиск', command=self.search)
        btn_search.place(x=105, y=50)

    def search(self):
        name = self.entry_search.get()
        self.app.search_records(name)
        self.destroy()

class DB():
    def __init__(self):
        self.conn = sqlite3.connect('db.db')
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS DB (
        id INTEGER PRIMARY KEY,
        name TEXT,
        tel TEXT,
        email TEXT,
        salary REAL
        );
        """)
        self.conn.commit()

    def insert_data(self, name, tel, email, salary):
        self.c.execute("""INSERT INTO db (name, tel, email, salary)
        VALUES (?,?,?,?)
        """, (name, tel, email, salary))
        self.conn.commit()

    def update_data(self, id, name, tel, email, salary):
        self.c.execute("""UPDATE db SET name=?, tel=?, email=?, salary=?
        WHERE ID=?""", (name, tel, email, salary, id))
        self.conn.commit()

    def delete_data(self, id):
        self.c.execute('DELETE FROM db WHERE id = ?', (id,))
        self.conn.commit()

    def get_all_data(self):
        self.c.execute('''SELECT * FROM db''')
        return self.c.fetchall()

    def get_data(self, id):
        self.c.execute('''SELECT * FROM db WHERE id=?''', (id,))
        return self.c.fetchone()

    def filter_data(self, name, tel, email):
        query = 'SELECT * FROM db WHERE name LIKE ? AND tel LIKE ? AND email LIKE ?'
        self.c.execute(query, ('%' + name + '%', '%' + tel + '%', '%' + email + '%'))
        return self.c.fetchall()

    def get_all_data_sorted(self, column):
        query = f'SELECT * FROM db ORDER BY {column}'
        self.c.execute(query)
        return self.c.fetchall()

if __name__ == '__main__':
    Base.metadata.create_all(engine)  # Создаем таблицу в базе данных
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title('Список сотрудников компании')
    root.geometry('800x450')
    root.resizable(False, False)
    root.mainloop()
