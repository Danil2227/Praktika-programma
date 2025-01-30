import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QMessageBox, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QTableWidget, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QFont
import pymysql

def create_connection():
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            database='donationprogramma',  # Replace with your actual database name
            port=3306,
            cursorclass=pymysql.cursors.DictCursor,
            ssl={'ssl': False}
        )
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.center()
        self.apply_styles()

    def setup_ui(self):
        self.username_label = QLabel("Логин:", self)
        self.username_label.move(350, 200)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите ваш логин")
        self.username_input.setFixedWidth(200)
        self.username_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.username_input.move(300, 230)

        self.password_label = QLabel("Пароль:", self)
        self.password_label.move(350, 280)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(200)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.move(300, 310)

        self.login_button = QPushButton("Войти", self)
        self.login_button.setFixedWidth(100)
        self.login_button.move(350, 370)
        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите как логин, так и пароль.")
            return

        connection = create_connection()

        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM users WHERE username=%s AND password=%s"
                    cursor.execute(query, (username, password))
                    result = cursor.fetchone()

                    if result:
                        QMessageBox.information(self, "Успешный вход", "Вы успешно вошли в систему.")
                        self.open_new_window()
                    else:
                        QMessageBox.warning(self, "Ошибка входа", "Вы ввели неправильный логин или пароль.")
            except pymysql.Error as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def open_new_window(self):
        self.new_window = MenuWindow()
        self.new_window.show()
        self.close()

    def center(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
            }
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Меню")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.center()
        self.apply_styles()
        self.load_project_count()
        self.load_total_donations()
        self.load_total_needed()

    def setup_ui(self):
        stats_label = QLabel("Статистика", self)
        stats_label.setFixedWidth(200)
        stats_label.move(325, 300)
        stats_label.setFont(QFont("Segoe UI", 17))

        self.total_donations_label = QLabel("Всего пожертвований:", self)
        self.total_donations_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.total_donations_label.move(20, 350)
        self.total_donations_label.setFont(QFont("Segoe UI", 14))

        self.total_projects_label = QLabel("Всего проектов:", self)
        self.total_projects_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.total_projects_label.move(20, 450)
        self.total_projects_label.setFont(QFont("Segoe UI", 14))

        self.total_needed_label = QLabel("Сколько всего нужно собрать:", self)
        self.total_needed_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.total_needed_label.move(20, 550)
        self.total_needed_label.setFont(QFont("Segoe UI", 14))

        self.projects_button = QPushButton("Проекты", self)
        self.projects_button.setFixedWidth(150)
        self.projects_button.move(35, 20)
        self.projects_button.setFont(QFont("Segoe UI", 10))
        self.projects_button.clicked.connect(self.handle_projects)

        self.add_project_button = QPushButton("Добавить проект", self)
        self.add_project_button.setFixedWidth(150)
        self.add_project_button.move(620, 20)
        self.add_project_button.setFont(QFont("Segoe UI", 10))
        self.add_project_button.clicked.connect(self.handle_add_project)

        self.donors_button = QPushButton("Жертвователи", self)
        self.donors_button.setFixedWidth(150)
        self.donors_button.move(425, 20)
        self.donors_button.setFont(QFont("Segoe UI", 10))
        self.donors_button.clicked.connect(self.handle_donors)

        self.payments_button = QPushButton("Платежи", self)
        self.payments_button.setFixedWidth(150)
        self.payments_button.move(230, 20)
        self.payments_button.setFont(QFont("Segoe UI", 10))
        self.payments_button.clicked.connect(self.handle_payments)

        self.exit_button = QPushButton("Выход", self)
        self.exit_button.setFixedWidth(150)
        self.exit_button.move(325, 80)
        self.exit_button.setFont(QFont("Segoe UI", 10))
        self.exit_button.clicked.connect(self.close_application)

    def load_project_count(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT COUNT(*) AS total_count FROM proekts"
                    cursor.execute(query)
                    result = cursor.fetchone()
                    total_count = result['total_count'] if result else 0
                    self.total_projects_label.setText(f"Всего проектов: {total_count}")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def load_total_donations(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT SUM(summalive) AS total_donations FROM livedonaters"
                    cursor.execute(query)
                    result = cursor.fetchone()
                    total_donations = result['total_donations'] if result and result['total_donations'] else 0
                    self.total_donations_label.setText(f"Всего пожертвований: {total_donations}")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def load_total_needed(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT SUM(SkolkoVsego) AS total_needed FROM proekts"
                    cursor.execute(query)
                    result = cursor.fetchone()
                    total_needed = result['total_needed'] if result and result['total_needed'] else 0
                    self.total_needed_label.setText(f"Сколько всего нужно собрать: {total_needed}")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def handle_projects(self):
        self.projects_window = ProjectsWindow()
        self.projects_window.show()
        self.close()

    def handle_add_project(self):
        self.add_project_window = AddProjectWindow()
        self.add_project_window.show()
        self.close()

    def handle_donors(self):
        self.donors_window = DonorsWindow()
        self.donors_window.show()
        self.close()

    def handle_payments(self):
        self.payments_window = PaymentsWindow()
        self.payments_window.show()
        self.close()

    def close_application(self):
        QApplication.quit()

    def center(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

class PaymentsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Платежи")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.center()
        self.load_payments()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.table_widget = QTableWidget(self)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #e3f2fd;
                border: 1px solid #1e88e5;
            }
            QHeaderView::section {
                background-color: #1e88e5;
                color: white;
                font-weight: bold;
            }
            QTableWidgetItem {
                padding: 10px;
            }
        """)
        self.table_widget.setFont(QFont("Segoe UI", 10))
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_widget)

        self.back_button = QPushButton("Назад", self)
        self.back_button.setFixedWidth(100)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e88e5;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_payments(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT code_live, nick, summalive FROM livedonaters"
                    cursor.execute(query)
                    payments = cursor.fetchall()

                    if payments:
                        columns = list(payments[0].keys())
                        self.table_widget.setRowCount(len(payments))
                        self.table_widget.setColumnCount(len(columns))
                        self.table_widget.setHorizontalHeaderLabels(columns)

                        for row_index, payment in enumerate(payments):
                            for col_index, key in enumerate(payment.keys()):
                                value = payment.get(key, "")
                                item = QTableWidgetItem(str(value))
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                self.table_widget.setItem(row_index, col_index, item)
                    else:
                        QMessageBox.information(self, "Информация", "Нет доступных платежей.")
                        self.table_widget.setRowCount(0)
                        self.table_widget.setColumnCount(0)
                        self.table_widget.setHorizontalHeaderLabels([])
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(0)
                self.table_widget.setHorizontalHeaderLabels([])
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            self.table_widget.setHorizontalHeaderLabels([])

    def go_back(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

    def center(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

class AddProjectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить проект")
        self.setFixedSize(400, 400)
        self.setup_ui()
        self.center()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.code_label = QLabel("Код проекта:", self)
        self.code_input = QLineEdit(self)
        self.code_input.setPlaceholderText("Введите код проекта")

        self.name_label = QLabel("Название проекта:", self)
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Введите название проекта")

        self.sum_label = QLabel("Сумма сбора:", self)
        self.sum_input = QLineEdit(self)
        self.sum_input.setPlaceholderText("Введите сумму сбора")

        self.description_label = QLabel("Описание проекта:", self)
        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText("Введите описание проекта")

        self.time_label = QLabel("Дата окончания сбора:", self)
        self.time_input = QLineEdit(self)
        self.time_input.setPlaceholderText("Введите дату")

        self.create_button = QPushButton("Создать", self)
        self.create_button.clicked.connect(self.create_project)

        self.cancel_button = QPushButton("Отмена", self)
        self.cancel_button.clicked.connect(self.return_to_menu)

        layout.addWidget(self.code_label)
        layout.addWidget(self.code_input)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.sum_label)
        layout.addWidget(self.sum_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.time_label)
        layout.addWidget(self.time_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_project(self):
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        summa = self.sum_input.text().strip()
        opisanie = self.description_input.text().strip()
        time = self.time_input.text().strip()

        if not all([code, name, summa, opisanie, time]):
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        try:
            summa_value = float(summa)
        except ValueError:
            QMessageBox.warning(self, "Ошибка ввода", "Сумма сбора должна быть числом.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = """
                        INSERT INTO proekts (code_proetks, NameProekt, SkolkoVsego, OpisanieProekta, TimeProekts)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (code, name, summa_value, opisanie, time))
                    connection.commit()
                    QMessageBox.information(self, "Успех", "Проект успешно создан.")
                    self.return_to_menu()
            except pymysql.Error as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def return_to_menu(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

    def center(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #2980b9;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QHBoxLayout QPushButton:last-child {
                background-color: #e74c3c;
            }
            QHBoxLayout QPushButton:last-child:hover {
                background-color: #c0392b;
            }
        """)

class ProjectsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Проекты")
        self.setFixedSize(1000, 700)  # Увеличение размера окна
        self.setup_ui()
        self.center()
        self.load_projects()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.table_widget = QTableWidget(self)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #e3f2fd;
                border: 1px solid #1e88e5;
            }
            QHeaderView::section {
                background-color: #1e88e5;
                color: white;
                font-weight: bold;
            }
            QTableWidgetItem {
                padding: 10px;
            }
        """)
        self.table_widget.setFont(QFont("Segoe UI", 10))
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()
        self.donate_button = self.create_button("Сделать пожертвование", 200)
        self.donate_button.clicked.connect(self.open_donation_dialog)

        self.delete_button = self.create_button("Удалить проект", 150)
        self.delete_button.clicked.connect(self.handle_delete_project)

        self.stop_button = self.create_button("Остановить сбор", 150)
        self.stop_button.clicked.connect(self.stop_collection)

        self.resume_button = self.create_button("Возобновить сбор", 150)  # Добавлена кнопка "Возобновить сбор"
        self.resume_button.clicked.connect(self.resume_collection)  # Подключение функции возобновления сбора

        self.back_button = self.create_button("Назад", 100)
        self.back_button.clicked.connect(self.go_back)

        button_layout.addWidget(self.donate_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.resume_button)  # Добавление кнопки в макет
        button_layout.addStretch()
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_button(self, text, width):
        button = QPushButton(text, self)
        button.setFixedWidth(width)
        button.setFont(QFont("Segoe UI", 10))
        button.setStyleSheet("""
            QPushButton {
                background-color: #42a5f5;
                color: white;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        return button

    def load_projects(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM proekts"
                    cursor.execute(query)
                    projects = cursor.fetchall()

                    if projects:
                        columns = list(projects[0].keys())
                        self.table_widget.setRowCount(len(projects))
                        self.table_widget.setColumnCount(len(columns))
                        self.table_widget.setHorizontalHeaderLabels([self.translate_header(col) for col in columns])

                        for row_index, project in enumerate(projects):
                            for col_index, key in enumerate(project.keys()):
                                value = project.get(key, "")
                                item = QTableWidgetItem(str(value))
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                self.table_widget.setItem(row_index, col_index, item)
                    else:
                        QMessageBox.information(self, "Информация", "Нет доступных проектов.")
                        self.table_widget.setRowCount(0)
                        self.table_widget.setColumnCount(0)
                        self.table_widget.setHorizontalHeaderLabels([])
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(0)
                self.table_widget.setHorizontalHeaderLabels([])
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            self.table_widget.setHorizontalHeaderLabels([])

    def translate_header(self, header):
        translations = {
            'code_proetks': 'Код проекта',
            'SummaSbora': 'Сумма сбора',
            'collection_active': 'Статус сбора'
        }
        return translations.get(header, header)

    def open_donation_dialog(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Выбор проекта", "Пожалуйста, выберите проект для пожертвования.")
            return

        selected_row = selected_items[0].row()
        project_code_item = self.table_widget.item(selected_row, 0)
        project_status_item = self.table_widget.item(selected_row, 2)  # Assuming status is in the third column

        if not project_code_item or not project_status_item:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить код или статус проекта.")
            return

        project_code = project_code_item.text()
        project_status = project_status_item.text()

        if project_status == "Остановлен":
            QMessageBox.warning(self, "Ошибка", "Нельзя сделать пожертвование для остановленного проекта.")
            return

        self.donation_dialog = DonationDialog(project_code, self)
        self.donation_dialog.exec()

    def handle_delete_project(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Выбор проекта", "Пожалуйста, выберите проект для удаления.")
            return

        selected_row = selected_items[0].row()
        project_code_item = self.table_widget.item(selected_row, 0)
        if not project_code_item:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить код проекта.")
            return

        project_code = project_code_item.text()

        reply = QMessageBox.question(
            self,
            "Подтвердите удаление",
            f"Вы уверены, что хотите удалить проект с кодом '{project_code}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            connection = create_connection()
            if connection:
                try:
                    with connection.cursor() as cursor:
                        delete_query = "DELETE FROM proekts WHERE code_proetks = %s"
                        cursor.execute(delete_query, (project_code,))
                        connection.commit()
                        QMessageBox.information(self, "Успех", "Проект успешно удален.")
                        self.load_projects()
                except pymysql.MySQLError as e:
                    QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
                finally:
                    connection.close()
            else:
                QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def stop_collection(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Выбор проекта", "Пожалуйста, выберите проект для остановки сбора.")
            return

        selected_row = selected_items[0].row()
        project_code_item = self.table_widget.item(selected_row, 0)
        if not project_code_item:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить код проекта.")
            return

        project_code = project_code_item.text()

        reply = QMessageBox.question(
            self,
            "Подтвердите остановку сбора",
            f"Вы уверены, что хотите остановить сбор для проекта с кодом '{project_code}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            connection = create_connection()
            if connection:
                try:
                    with connection.cursor() as cursor:
                        update_query = "UPDATE proekts SET Status = 'Остановлен' WHERE code_proetks = %s"
                        cursor.execute(update_query, (project_code,))
                        connection.commit()
                        QMessageBox.information(self, "Успех", "Сбор успешно остановлен.")
                        self.load_projects()
                except pymysql.MySQLError as e:
                    QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
                finally:
                    connection.close()
            else:
                QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def resume_collection(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Выбор проекта", "Пожалуйста, выберите проект для возобновления сбора.")
            return

        selected_row = selected_items[0].row()
        project_code_item = self.table_widget.item(selected_row, 0)
        if not project_code_item:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить код проекта.")
            return

        project_code = project_code_item.text()

        reply = QMessageBox.question(
            self,
            "Подтвердите возобновление сбора",
            f"Вы уверены, что хотите возобновить сбор для проекта с кодом '{project_code}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            connection = create_connection()
            if connection:
                try:
                    with connection.cursor() as cursor:
                        update_query = "UPDATE proekts SET Status = 'Активен' WHERE code_proetks = %s"
                        cursor.execute(update_query, (project_code,))
                        connection.commit()
                        QMessageBox.information(self, "Успех", "Сбор успешно возобновлен.")
                        self.load_projects()
                except pymysql.MySQLError as e:
                    QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
                finally:
                    connection.close()
            else:
                QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def go_back(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

    def center(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

class DonationDialog(QDialog):
    def __init__(self, project_code, parent_window):
        super().__init__()
        self.setWindowTitle("Сделать пожертвование")
        self.setFixedSize(300, 200)
        self.project_code = project_code
        self.parent_window = parent_window
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.amount_label = QLabel("Сумма пожертвования:", self)
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Введите сумму")

        self.nickname_label = QLabel("Ник:", self)
        self.nickname_input = QLineEdit(self)
        self.nickname_input.setPlaceholderText("Введите ваш ник")

        self.donate_button = QPushButton("Пожертвовать", self)
        self.donate_button.clicked.connect(self.make_donation)

        layout.addWidget(self.amount_label)
        layout.addWidget(self.amount_input)
        layout.addWidget(self.nickname_label)
        layout.addWidget(self.nickname_input)
        layout.addWidget(self.donate_button)

        self.setLayout(layout)

    def make_donation(self):
        amount_text = self.amount_input.text().strip()
        nickname = self.nickname_input.text().strip()

        if not amount_text or not nickname:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка ввода", "Сумма пожертвования должна быть положительным числом.")
            return

        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Check project status
                    status_query = "SELECT Status FROM proekts WHERE code_proetks = %s"
                    cursor.execute(status_query, (self.project_code,))
                    project = cursor.fetchone()

                    if project and project['Status'] == 'Остановлен':
                        QMessageBox.warning(self, "Ошибка", "Нельзя сделать пожертвование для остановленного проекта.")
                        return

                    # Update the donation amount in the proekts table
                    update_query = """
                        UPDATE proekts SET SummaSbora = SummaSbora + %s WHERE code_proetks = %s
                    """
                    cursor.execute(update_query, (amount, self.project_code))
                    connection.commit()

                    # Check if the donor already exists
                    select_query = "SELECT * FROM donater WHERE nick = %s"
                    cursor.execute(select_query, (nickname,))
                    donor = cursor.fetchone()

                    if donor:
                        # Update the existing donor's donation amount
                        update_donor_query = "UPDATE donater SET summa = summa + %s WHERE nick = %s"
                        cursor.execute(update_donor_query, (amount, nickname))
                    else:
                        # Insert a new donor record
                        insert_donor_query = "INSERT INTO donater (nick, summa) VALUES (%s, %s)"
                        cursor.execute(insert_donor_query, (nickname, amount))

                    connection.commit()

                    # Insert the donation into the livedonaters table
                    insert_query = """
                        INSERT INTO livedonaters (nick, summalive)
                        VALUES (%s, %s)
                    """
                    cursor.execute(insert_query, (nickname, amount))
                    connection.commit()

                    QMessageBox.information(
                        self,
                        "Успех",
                        "Пожертвование успешно добавлено."
                    )
                    self.parent_window.load_projects()  # Refresh the projects window
                    self.accept()

            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                border: 1px solid #2980b9;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

class DonorsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Жертвователи")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.center()
        self.load_donors()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.table_widget = QTableWidget(self)
        self.table_widget.setStyleSheet("""
            QTableWidget {
                background-color: #e3f2fd;
                border: 1px solid #1e88e5;
            }
            QHeaderView::section {
                background-color: #1e88e5;
                color: white;
                font-weight: bold;
            }
            QTableWidgetItem {
                padding: 10px;
            }
        """)
        self.table_widget.setFont(QFont("Segoe UI", 10))
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_widget)

        self.back_button = QPushButton("Назад", self)
        self.back_button.setFixedWidth(100)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e88e5;
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_donors(self):
        connection = create_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM donater"
                    cursor.execute(query)
                    donors = cursor.fetchall()

                    if donors:
                        columns = list(donors[0].keys())
                        self.table_widget.setRowCount(len(donors))
                        self.table_widget.setColumnCount(len(columns))
                        self.table_widget.setHorizontalHeaderLabels(columns)

                        for row_index, donor in enumerate(donors):
                            for col_index, key in enumerate(donor.keys()):
                                value = donor.get(key, "")
                                item = QTableWidgetItem(str(value))
                                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                self.table_widget.setItem(row_index, col_index, item)
                    else:
                        QMessageBox.information(self, "Информация", "Нет доступных жертвователей.")
                        self.table_widget.setRowCount(0)
                        self.table_widget.setColumnCount(0)
                        self.table_widget.setHorizontalHeaderLabels([])
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Произошла ошибка: {e}")
                self.table_widget.setRowCount(0)
                self.table_widget.setColumnCount(0)
                self.table_widget.setHorizontalHeaderLabels([])
            finally:
                connection.close()
        else:
            QMessageBox.critical(self, "Ошибка подключения", "Не удалось подключиться к базе данных.")
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            self.table_widget.setHorizontalHeaderLabels([])

    def go_back(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

    def center(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())