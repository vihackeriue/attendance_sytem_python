import sys
import requests
from PyQt5 import QtCore, QtWidgets
from session import UserManager  # Import UserManager để quản lý trạng thái người dùng

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.auth_manager = UserManager()  # Sử dụng UserManager để quản lý trạng thái người dùng

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 480, 620)
        self.setStyleSheet("background-color: rgb(54, 54, 54);")

        # Tạo các widget
        self.label = QtWidgets.QLabel("Login", self)
        self.label.setGeometry(190, 50, 121, 71)
        self.label.setStyleSheet("color:rgb(225, 225, 225); font-size:28pt;")

        self.username_label = QtWidgets.QLabel("Email", self)
        self.username_label.setGeometry(40, 160, 101, 31)
        self.username_label.setStyleSheet("font-size:15pt; color:rgb(255, 0, 127)")

        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setGeometry(170, 150, 241, 51)
        self.username_input.setStyleSheet("font-size:14pt; color:rgb(243, 243, 243)")

        self.password_label = QtWidgets.QLabel("Password", self)
        self.password_label.setGeometry(40, 270, 111, 31)
        self.password_label.setStyleSheet("font-size:15pt; color:rgb(255, 0, 127)")

        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setGeometry(170, 260, 241, 51)
        self.password_input.setStyleSheet("font-size:14pt; color:rgb(243, 243, 243)")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)  # Ẩn mật khẩu dưới dạng dấu sao

        self.login_button = QtWidgets.QPushButton("Login", self)
        self.login_button.setGeometry(270, 390, 141, 41)
        self.login_button.setStyleSheet("background-color: rgb(167, 168, 167); font-size:14pt; color:rgb(255, 255, 255)")
        self.login_button.clicked.connect(self.login)

        self.create_account_button = QtWidgets.QPushButton("Create Account", self)
        self.create_account_button.setGeometry(320, 340, 93, 28)
        self.create_account_button.setStyleSheet("color:rgb(255, 255, 255)")

        QtCore.QMetaObject.connectSlotsByName(self)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            # Gửi yêu cầu API đến server Flask để đăng nhập
            response = requests.post('http://127.0.0.1:5000/api/login', json={'username': username, 'password': password})
            response.raise_for_status()  # Kiểm tra nếu có lỗi HTTP

            if response.status_code == 200:
                user_data = response.json()
                if user_data['role'] == 'employee':
                    # Lưu user_id vào UserManager khi đăng nhập thành công
                    self.auth_manager.set_user_id(user_data['user_id'])

                    self.accept_login()
                else:
                    QtWidgets.QMessageBox.warning(self, "Lỗi", "Bạn không có quyền truy cập.")
            else:
                self.show_error_message()
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.warning(self, "Lỗi Kết Nối", f"Không thể kết nối đến máy chủ: {str(e)}")

    def accept_login(self):
        # Chuyển tới màn hình chính
        from main import MainWindow  # Chỉ nhập khẩu khi cần thiết
        self.main_window = MainWindow(self.auth_manager)
        self.main_window.show()
        self.close()

    def show_error_message(self):
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setWindowTitle("Login Failed")
        error_dialog.setText("Đăng nhập thất bại!")
        error_dialog.exec_()
