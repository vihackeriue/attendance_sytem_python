import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication

from session import UserManager  # Import UserManager to manage user authentication
import requests
from attendance import AttendanceWindow
from shift import ShiftWindow
from history import HistoryWindow
from login_ui import LoginWindow  # Import only when needed

class MainWindow(QtWidgets.QWidget):
    def __init__(self, auth_manager):
        super().__init__()

        self.auth_manager = auth_manager  # Receive AuthManager from LoginWindow
        self.user_id = self.auth_manager.get_user_id()

        if not self.user_id:  # If there's no user_id, show login window
            self.show_login_window()
        else:
            self.setup_ui()  # If logged in, show the main screen

    def show_login_window(self):

        login_dialog = LoginWindow(self.auth_manager)
        login_dialog.show()
        self.hide()  # Hide main window when login dialog is shown

    def setup_ui(self):
        self.setWindowTitle('Màn hình chính')
        self.setFixedSize(900, 650)  # Set fixed size for the main window

        # Set background color for the main window
        self.setStyleSheet("background-color: #2b2f3b;")  # Background color #2b2f3b

        # Main layout (vertical)
        main_layout = QtWidgets.QVBoxLayout()

        # Chức năng label with border (center aligned)
        func_label = QtWidgets.QLabel("Chức Năng")
        func_label.setStyleSheet(
            "border: 1px solid black; padding: 10px; font-size: 28px; font-weight: bold; color: #ffffff;")  # White text color
        func_label.setAlignment(QtCore.Qt.AlignCenter)  # Center align the label

        # Grid layout for buttons (2x2 grid)
        buttons_layout = QtWidgets.QGridLayout()
        button1 = QtWidgets.QPushButton("Check in")
        button2 = QtWidgets.QPushButton("Shift")
        button3 = QtWidgets.QPushButton("History")
        button4 = QtWidgets.QPushButton("Exit")

        # Set button styles (green background, white text)
        button_style = "background-color: #000080; color: #ffffff; font-size: 32px;"  # Navy blue background and white text
        for button in [button1, button2, button3, button4]:
            button.setFixedSize(350, 200)  # Make buttons square (350x200)
            button.setStyleSheet(button_style)  # Apply style to buttons

        buttons_layout.addWidget(button1, 0, 0)  # Button 1 at row 0, column 0
        buttons_layout.addWidget(button2, 0, 1)  # Button 2 at row 0, column 1
        buttons_layout.addWidget(button3, 1, 0)  # Button 3 at row 1, column 0
        buttons_layout.addWidget(button4, 1, 1)  # Button 4 at row 1, column 1
        buttons_layout.setSpacing(20)  # Add space between the buttons

        # Center the buttons layout within the window
        buttons_layout.setAlignment(QtCore.Qt.AlignCenter)  # Align buttons grid to the center

        # Connect buttons to their respective methods
        button1.clicked.connect(self.clock_in)
        button2.clicked.connect(self.shift)
        button3.clicked.connect(self.history)
        button4.clicked.connect(self.logout)

        # Add spacers to adjust the layout spacing
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        # Adding all widgets to the main layout

        main_layout.addWidget(func_label)
        main_layout.addLayout(buttons_layout)
        main_layout.addItem(spacer)  # Adding space between sections

        # Set main layout to window
        self.setLayout(main_layout)

    def clock_in(self):
        self.show_attendance_window()


    def shift(self):
        self.show_shift_window()

    def history(self):
        self.show_history_window()

    def logout(self):
        # Đăng xuất người dùng
        user_manager = UserManager()
        user_manager.logout()
        # Đóng ứng dụng hiện tại
        QApplication.quit()




    def show_attendance_window(self):
        self.attendance_window = AttendanceWindow(self.user_id)  # Create ClockInApp instance with user_id
        self.attendance_window.show()

    def show_shift_window(self):
        self.shift_window = ShiftWindow(self.user_id)  # Create ClockInApp instance with user_id
        self.shift_window.show()


    def show_history_window(self):
        self.history_window = HistoryWindow(self.user_id)  # Create ClockInApp instance with user_id
        self.history_window.show()

class AttendanceHistoryWindow(QtWidgets.QWidget):
    def __init__(self, history):
        super().__init__()

        self.setWindowTitle('Lịch sử chấm công')
        self.setGeometry(100, 100, 640, 480)

        self.history_list = QtWidgets.QListWidget(self)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.history_list)

        # Display attendance history
        for record in history:
            self.history_list.addItem(f"{record['date']} - Check In: {record['check_in_time']} | Check Out: {record['check_out_time']}")

        self.setLayout(self.layout)