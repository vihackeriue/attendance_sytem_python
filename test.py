import sys
import requests
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt


class ShiftHistoryWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.setWindowTitle("Danh sách lịch sử chấm công")
        self.setGeometry(100, 100, 800, 600)

        # Create a layout for the main window
        layout = QVBoxLayout()

        # Create and add a QLabel for the title
        title_label = QLabel("Danh sách lịch sử chấm công")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")  # Set larger font size
        layout.addWidget(title_label)

        # Create and add a QLineEdit for search functionality
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Tìm kiếm theo tên ca làm việc...")
        self.search_input.textChanged.connect(self.search_shifts)  # Connect to search function
        layout.addWidget(self.search_input)

        # Create a table widget to display shift history
        self.table = QTableWidget(self)
        layout.addWidget(self.table)

        # Set layout for the window
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize shifts_data as an empty list for filtering
        self.shifts_data = []

        # Fetch data from the API and populate the table
        self.fetch_and_display_shifts()

    def fetch_and_display_shifts(self):
        try:
            # Fetch shift history data from the Flask API
            response = requests.get(f'http://127.0.0.1:5000/api/shift/history?user_id={self.user_id}')
            response.raise_for_status()  # Check for HTTP errors

            if response.status_code == 200:
                shifts = response.json().get('shifts', [])  # Parse the JSON response and get 'shifts' key

                # Check if there are any shifts, if not, show a message
                if not shifts:
                    QtWidgets.QMessageBox.information(self, "Thông báo", "Bạn không có lịch sử chấm công.")
                    return

                # Store all the shifts data for searching
                self.shifts_data = shifts  # Store data for search functionality

                # Set the number of rows and columns in the table
                self.table.setRowCount(len(shifts))
                self.table.setColumnCount(3)

                # Set table headers
                self.table.setHorizontalHeaderLabels(['Tên Ca Làm Việc', 'Giờ Check-In', 'Trạng Thái'])

                # Populate the table with shift data
                self.display_shifts(shifts)

                # Resize columns to fit content
                self.table.resizeColumnsToContents()

                # Adjust window width to fit the table's width
                self.adjust_window_width()

            else:
                QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể lấy dữ liệu lịch sử chấm công.")
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.warning(self, "Lỗi Kết Nối", f"Không thể kết nối đến máy chủ: {str(e)}")

    def display_shifts(self, shifts):
        """Populate the table with shift data."""
        self.table.setRowCount(len(shifts))  # Set row count based on filtered shifts
        for row, shift in enumerate(shifts):
            self.table.setItem(row, 0, QTableWidgetItem(shift['shift_name']))
            self.table.setItem(row, 1, QTableWidgetItem(shift['check_in_time']))
            self.table.setItem(row, 2, QTableWidgetItem(shift['status']))

    def search_shifts(self):
        """Filter shifts based on search input."""
        search_term = self.search_input.text().lower()

        # Filter shifts based on the search term (case-insensitive)
        filtered_shifts = [shift for shift in self.shifts_data if search_term in shift['shift_name'].lower()]

        # Display filtered shifts
        self.display_shifts(filtered_shifts)

    def adjust_window_width(self):
        """Adjust window width to fit the table width."""
        table_width = sum([self.table.columnWidth(i) for i in range(self.table.columnCount())])
        self.setFixedWidth(table_width + 40)  # Add some padding for the window


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ShiftHistoryWindow(user_id=9)  # Replace with the actual user_id
    window.show()
    sys.exit(app.exec_())
