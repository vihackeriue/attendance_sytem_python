import sys
import requests
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class ShiftWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.setWindowTitle("Danh sách ca làm việc của bạn")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout for the main window
        layout = QVBoxLayout()

        # Create and add a QLabel for the title
        title_label = QLabel("Danh sách ca làm việc của bạn")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")  # Set larger font size
        layout.addWidget(title_label)

        # Create a table widget to display shifts
        self.table = QTableWidget(self)
        layout.addWidget(self.table)

        # Set layout for the window
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Fetch data from the API and populate the table
        self.fetch_and_display_shifts()

    def fetch_and_display_shifts(self):
        try:
            # Fetch shift data from the Flask API
            response = requests.get(f'http://127.0.0.1:5000/api/shift/list?user_id={self.user_id}')
            response.raise_for_status()  # Check for HTTP errors

            if response.status_code == 200:
                shifts = response.json().get('shifts', [])  # Parse the JSON response and get 'shifts' key

                # Check if there are any shifts, if not, show a message
                if not shifts:
                    QtWidgets.QMessageBox.information(self, "Thông báo", "Bạn hiện tại không có ca làm việc nào.")
                    return

                # Set the number of rows and columns in the table
                self.table.setRowCount(len(shifts))
                self.table.setColumnCount(3)

                # Set table headers
                self.table.setHorizontalHeaderLabels(['Tên Ca Làm Việc', 'Thời Gian Bắt Đầu', 'Thời Gian Kết Thúc'])

                # Populate the table with shift data
                for row, shift in enumerate(shifts):
                    self.table.setItem(row, 0, QTableWidgetItem(shift['shift_name']))
                    self.table.setItem(row, 1, QTableWidgetItem(shift['start_time']))
                    self.table.setItem(row, 2, QTableWidgetItem(shift['end_time']))

                # Resize columns to fit content
                self.table.resizeColumnsToContents()

                # Adjust window width to fit the table's width
                self.adjust_window_width()

            else:
                QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể lấy dữ liệu ca làm việc.")
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.warning(self, "Lỗi Kết Nối", f"Không thể kết nối đến máy chủ: {str(e)}")

    def adjust_window_width(self):
        # Adjust window width to fit the table width
        table_width = sum([self.table.columnWidth(i) for i in range(self.table.columnCount())])
        self.setFixedWidth(table_width + 40)  # Add some padding for the window