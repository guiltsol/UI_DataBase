import re
import tkinter as tk
from tkinter import messagebox
import mysql.connector

class TheaterDatabase:

    def __init__(self, connection_string: dict):
        """
        Инициализация подключения к БД
        :param connection_string: Словарь с параметрами подключения
        """
        self.connection_string = connection_string

    def execute_query(self, query: str, params: tuple = ()):
        """
        Выполнение SELECT-запроса с возвращением результатов
        :param query: SQL-запрос
        :param params: Параметры запроса
        :return: Результат запроса
        """
        try:
            with mysql.connector.connect(**self.connection_string) as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except mysql.connector.Error as e:
            messagebox.showerror(
                "Ошибка БД", f"Ошибка выполнения запроса: {e}")
            raise

    def execute_update(self, query: str, params: tuple = ()):
        """
        Выполнение INSERT/UPDATE/DELETE-запроса
        :param query: SQL-запрос
        :param params: Параметры запроса
        """
        try:
            with mysql.connector.connect(**self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
        except mysql.connector.Error as e:
            messagebox.showerror("Ошибка БД", f"Ошибка обновления данных: {e}")
            raise


class DataController:

    def __init__(self, db):
    
        self.db = db

    def add_record_to_db(self, table, *args):
        """
        Добавление записи в указанную таблицу
        :param table: Название таблицы
        :param args: Значения полей записи
        """
        if table == "Performances":
            query = "INSERT INTO Performances (Title, Budget, Year) VALUES (%s, %s, %s)"
        elif table == "Actors":
            query = "INSERT INTO Actors (Name, Experience, Awards) VALUES (%s, %s, %s)"
        elif table == "Roles":
            query = "INSERT INTO Roles (PerformanceID, RoleName) VALUES (%s, %s)"
        elif table == "Contracts":
            query = """
                INSERT INTO Contracts 
                (ActorID, RoleID, Year, BaseSalary, PerformanceCount, Bonus) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
        self.db.execute_update(query, args)

    def update_actor_salary_db(self, actor_id, new_salary):
        query = "UPDATE Contracts SET BaseSalary = %s WHERE ActorID = %s"
        self.db.execute_update(query, (new_salary, actor_id))

    def delete_record_from_db(self, table, record_id):
        column = {
            "Performances": "PerformanceID",
            "Actors": "ActorID",
            "Roles": "RoleID",
            "Contracts": "ContractID"
        }[table]
        query = f"DELETE FROM {table} WHERE {column} = %s"
        self.db.execute_update(query, (record_id,))

    def get_performances_by_year_db(self, year):
        return self.db.execute_query("SELECT * FROM Performances WHERE Year = %s", (year,))

    def get_all_data(self, table):
        return self.db.execute_query(f"SELECT * FROM {table}")

    def update_add_fields(self, theater_ui, *args):
        """Обновление полей ввода при смене таблицы"""
        table = theater_ui.table_add_variable.get()
        fields = [theater_ui.add_field_1_label, theater_ui.add_field_2_label,
                  theater_ui.add_field_3_label, theater_ui.add_field_4_label,
                  theater_ui.add_field_5_label, theater_ui.add_field_6_label]
        entries = [theater_ui.add_field_1_entry, theater_ui.add_field_2_entry,
                   theater_ui.add_field_3_entry, theater_ui.add_field_4_entry,
                   theater_ui.add_field_5_entry, theater_ui.add_field_6_entry]

        for field in fields + entries:
            field.grid_forget()

        if table == "Performances":
            labels = ["Название", "Бюджет", "Год"]
        elif table == "Actors":
            labels = ["Имя", "Опыт", "Награды"]
        elif table == "Roles":
            labels = ["ID Спектакля", "Роль"]
        elif table == "Contracts":
            labels = ["ID актёра", "ID роли", "Год",
                      "Базовая зарплата", "Кол-во спектаклей", "Бонус"]

        for i, label in enumerate(labels):
            fields[i].config(text=label)
            fields[i].grid(row=i+1, column=0)
            entries[i].grid(row=i+1, column=1)

    def add_record(self, theater_ui):
        """Обработчик добавления новой записи"""
        table = theater_ui.table_add_variable.get()
        entries = [theater_ui.add_field_1_entry, theater_ui.add_field_2_entry,
                   theater_ui.add_field_3_entry, theater_ui.add_field_4_entry,
                   theater_ui.add_field_5_entry, theater_ui.add_field_6_entry]
        args = [entry.get() for entry in entries if entry.winfo_ismapped()]
        try:
            self.add_record_to_db(table, *args)
            messagebox.showinfo(
                "Успех", f"Запись добавлена в таблицу {table}!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def get_performances_by_year(self, theater_ui):
        """Поиск спектаклей по году"""
        try:
            year = int(theater_ui.entry_get_year.get())
            data = self.get_performances_by_year_db(year)
            self.show_data(theater_ui, data, f"Спектакли за {year} год")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Год должен быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_actor_salary(self, theater_ui):
        """Обновление зарплаты актера"""
        try:
            actor_id = int(theater_ui.entry_actor_id.get())
            new_salary = float(theater_ui.entry_new_salary.get())
            self.update_actor_salary_db(actor_id, new_salary)
            messagebox.showinfo(
                "Успех", f"Зарплата актёра {actor_id} обновлена!")
        except ValueError:
            messagebox.showerror(
                "Ошибка ввода", "ID и зарплата должны быть числами")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_record(self, theater_ui):
        """Удаление записи из таблицы"""
        try:
            table = theater_ui.table_delete_variable.get()
            record_id = int(theater_ui.entry_delete_id.get())
            self.delete_record_from_db(table, record_id)
            messagebox.showinfo(
                "Успех", f"Запись {record_id} из {table} удалена!")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID должен быть числом")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def output_performances(self, theater_ui):
        """Вывод всех спектаклей"""
        data = self.get_all_data("Performances")
        self.show_data(theater_ui, data, "Спектакли")

    def output_actors(self, theater_ui):
        """Вывод всех актеров"""
        data = self.get_all_data("Actors")
        self.show_data(theater_ui, data, "Актёры")

    def output_roles(self, theater_ui):
        """Вывод всех ролей"""
        data = self.get_all_data("Roles")
        self.show_data(theater_ui, data, "Роли")

    def output_contracts(self, theater_ui):
        """Вывод всех контрактов"""
        data = self.get_all_data("Contracts")
        self.show_data(theater_ui, data, "Контракты")

    def show_data(self, theater_ui, data, title):
        theater_ui.text_output.delete("1.0", tk.END)
        if data:
            for row in data:
                line = ", ".join([f"{k}: {v}" for k, v in row.items()]) + "\n"
                theater_ui.text_output.insert(tk.END, line)
        else:
            theater_ui.text_output.insert(tk.END, f"{title} не найдены\n")

    def close_app(self, theater_ui):
        theater_ui.root.destroy()


class TheaterUI:

    def __init__(self, root, data_controller):
        """
        Инициализация интерфейса
        :param root: Корневое окно Tkinter
        :param data_controller: Экземпляр DataController
        """
        self.root = root
        self.data_controller = data_controller
        self.root.title("Театральная база данных")
        self.create_frames()
        self.create_widgets()

    def create_frames(self):
        self.frame_main = tk.Frame(self.root)
        self.frame_main.pack(fill=tk.BOTH, expand=True)

        self.frame_main.grid_rowconfigure(0, weight=1)
        self.frame_main.grid_rowconfigure(1, weight=1)
        self.frame_main.grid_rowconfigure(2, weight=1)
        self.frame_main.grid_rowconfigure(3, weight=1)
        self.frame_main.grid_columnconfigure(0, weight=1)
        self.frame_main.grid_columnconfigure(1, weight=2)

        self.frame_add = tk.LabelFrame(self.frame_main, text="Добавить запись")
        self.frame_add.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_get = tk.LabelFrame(
            self.frame_main, text="Спектакли по году")
        self.frame_get.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_update = tk.LabelFrame(
            self.frame_main, text="Изменить зарплату актёра")
        self.frame_update.grid(row=2, column=0, padx=10,
                               pady=10, sticky="nsew")
        self.frame_delete = tk.LabelFrame(
            self.frame_main, text="Удалить запись")
        self.frame_delete.grid(row=3, column=0, padx=10,
                               pady=10, sticky="nsew")
        self.frame_output = tk.LabelFrame(self.frame_main, text="Вывод данных")
        self.frame_output.grid(row=0, column=1, rowspan=4,
                               padx=10, pady=10, sticky="nsew")

        for frame in [self.frame_add, self.frame_get, self.frame_update, self.frame_delete]:
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)
        self.frame_output.grid_rowconfigure(0, weight=1)
        self.frame_output.grid_columnconfigure(0, weight=1)

    def create_widgets(self):
        tk.Label(self.frame_add, text="Таблица").grid(
            row=0, column=0, sticky="w")
        self.table_add_options = [
            "Performances", "Actors", "Roles", "Contracts"]
        self.table_add_variable = tk.StringVar(value=self.table_add_options[0])
        self.table_add_variable.trace(
            "w", lambda *args: self.data_controller.update_add_fields(self, *args))
        tk.OptionMenu(self.frame_add, self.table_add_variable, *
                      self.table_add_options).grid(row=0, column=1, sticky="ew")

        self.add_field_1_label = tk.Label(self.frame_add)
        self.add_field_1_entry = tk.Entry(self.frame_add)
        self.add_field_2_label = tk.Label(self.frame_add)
        self.add_field_2_entry = tk.Entry(self.frame_add)
        self.add_field_3_label = tk.Label(self.frame_add)
        self.add_field_3_entry = tk.Entry(self.frame_add)
        self.add_field_4_label = tk.Label(self.frame_add)
        self.add_field_4_entry = tk.Entry(self.frame_add)
        self.add_field_5_label = tk.Label(self.frame_add)
        self.add_field_5_entry = tk.Entry(self.frame_add)
        self.add_field_6_label = tk.Label(self.frame_add)
        self.add_field_6_entry = tk.Entry(self.frame_add)

        self.add_button = tk.Button(
            self.frame_add, text="Добавить", command=lambda: self.data_controller.add_record(self))
        self.add_button.grid(row=7, column=0, columnspan=2,
                             padx=5, pady=5, sticky="ew")
        self.data_controller.update_add_fields(self)

        tk.Label(self.frame_get, text="Год").grid(row=0, column=0, sticky="w")
        self.entry_get_year = tk.Entry(self.frame_get)
        self.entry_get_year.grid(row=0, column=1, sticky="ew")
        tk.Button(self.frame_get, text="Найти", command=lambda: self.data_controller.get_performances_by_year(
            self)).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_update, text="ID актёра").grid(
            row=0, column=0, sticky="w")
        self.entry_actor_id = tk.Entry(self.frame_update)
        self.entry_actor_id.grid(row=0, column=1, sticky="ew")
        tk.Label(self.frame_update, text="Новая зарплата").grid(
            row=1, column=0, sticky="w")
        self.entry_new_salary = tk.Entry(self.frame_update)
        self.entry_new_salary.grid(row=1, column=1, sticky="ew")
        tk.Button(self.frame_update, text="Обновить", command=lambda: self.data_controller.update_actor_salary(
            self)).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        tk.Label(self.frame_delete, text="Таблица").grid(
            row=1, column=0, sticky="w")
        self.table_delete_variable = tk.StringVar(
            value=self.table_add_options[0])
        tk.OptionMenu(self.frame_delete, self.table_delete_variable,
                      *self.table_add_options).grid(row=1, column=1, sticky="ew")
        tk.Label(self.frame_delete, text="ID").grid(
            row=2, column=0, sticky="w")
        self.entry_delete_id = tk.Entry(self.frame_delete)
        self.entry_delete_id.grid(row=2, column=1, sticky="ew")
        tk.Button(self.frame_delete, text="Удалить", command=lambda: self.data_controller.delete_record(
            self)).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        self.text_output = tk.Text(self.frame_output, wrap=tk.WORD)
        self.text_output.pack(fill=tk.BOTH, expand=True)
        tk.Button(self.root, text="Спектакли", command=lambda: self.data_controller.output_performances(
            self)).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        tk.Button(self.root, text="Актёры", command=lambda: self.data_controller.output_actors(
            self)).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        tk.Button(self.root, text="Роли", command=lambda: self.data_controller.output_roles(
            self)).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        tk.Button(self.root, text="Контракты", command=lambda: self.data_controller.output_contracts(
            self)).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Авторизация")
        self.root.geometry("300x180")
        
        tk.Label(root, text="Логин:").pack(pady=5)
        self.login_entry = tk.Entry(root)
        self.login_entry.pack(pady=5)
        
        tk.Label(root, text="Пароль:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        
        tk.Button(root, text="Войти", command=self.check_credentials).pack(pady=10)
        
        self.correct_login = "admin"
        self.correct_password = "admin123"

    def check_credentials(self):
        login = self.login_entry.get()
        password = self.password_entry.get()
        '''
        1) Логин и пароль не пустые.
        2) Логин содержит минимум 3 символа
        3) Пароль содержит минимум 6 символов
        4) Логин и пароль не содержат пробелы
        5) Пароль содержит хотя бы одну букву и одну цифру
        '''
        if not login or not password:
            messagebox.showerror("Ошибка", "Логин и пароль не могут быть пустыми")
            return
        
        if len(login) < 3:
            messagebox.showerror("Ошибка", "Логин должен содержать минимум 3 символа")
            return
        
        if len(password) < 6:
            messagebox.showerror("Ошибка", "Пароль должен содержать минимум 6 символов")
            return
        
        if " " in login or " " in password:
            messagebox.showerror("Ошибка", "Логин и пароль не должны содержать пробелы")
            return
        
        if not re.search(r'[A-Za-z]', login):
            messagebox.showerror("Ошибка", "Логин не должен содержать только цифры")
            return
        
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            messagebox.showerror("Ошибка", "Пароль должен содержать буквы и цифры")
            return
        
        if login == self.correct_login and password == self.correct_password:
            self.root.destroy()  
            self.on_login_success()  
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


    def main_app():
        root = tk.Tk()
        connection_string = {
            "host": "localhost",
            "user": "root",
            "password": "admin",
            "database": "mybase"
        }
        db = TheaterDatabase(connection_string)
        data_controller = DataController(db)
        app = TheaterUI(root, data_controller)
        root.protocol("WM_DELETE_WINDOW", lambda: data_controller.close_app(app))
        root.geometry("1000x630") 
        root.mainloop()


if __name__ == "__main__":
    login_root = tk.Tk()
    login_window = LoginWindow(login_root, lambda: LoginWindow.main_app())
    login_root.mainloop()
