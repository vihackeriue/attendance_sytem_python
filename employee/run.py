import sys
from PyQt5.QtWidgets import QApplication
from login_ui import LoginWindow  # Import giao diện đăng nhập
from session import UserManager  # Import lớp UserManager
from main import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Kiểm tra xem người dùng đã đăng nhập hay chưa
    user_manager = UserManager()
    if user_manager.is_logged_in():  # Nếu đã đăng nhập
        # Hiển thị màn hình chính
        window = MainWindow(user_manager)
        window.show()
    else:
        # Nếu chưa đăng nhập, hiển thị cửa sổ đăng nhập
        login_window = LoginWindow()
        login_window.show()

    sys.exit(app.exec_())
