import sys
import cv2
import requests
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QPushButton, QComboBox, QWidget


class AttendanceWindow(QtWidgets.QMainWindow):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.setWindowTitle('Chấm Công Khuôn Mặt')
        self.setGeometry(100, 100, 640, 480)

        # Set background color for the window
        self.setStyleSheet("background-color: #2b2f3b;")  # Set background color #2b2f3b

        self.video_capture = cv2.VideoCapture(0)  # Initialize camera
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        # Add label for "Chấm Công"
        self.clock_in_label = QtWidgets.QLabel("Chấm Công", self)
        self.clock_in_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff; ")  # White text color

        self.clock_in_button = QtWidgets.QPushButton("Chấm Công", self)
        self.clock_in_button.setStyleSheet("background-color: #ff6f00; color: #ffffff; font-size: 24px; font-weight: bold;")  # Blue button with white text
        self.clock_in_button.clicked.connect(self.clock_in)

        # ComboBox for selecting work shift
        self.shift_combo_box = QComboBox(self)
        self.shift_combo_box.setPlaceholderText("Chọn ca làm việc...")
        self.load_shifts()  # Load available shifts from API
        self.shift_combo_box.setStyleSheet("font-size: 14pt; color: #ffffff; background-color: #ff6f00;")  # White text, dark background

        # Create layout for the window
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.clock_in_label)  # Add the label first
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.shift_combo_box)
        self.layout.addWidget(self.clock_in_button)

        container = QtWidgets.QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.timer.start(30) # Update frame every 30ms

    def load_shifts(self):
        """Load available shifts from the API."""
        response = requests.get(f'http://127.0.0.1:5000/api/shift/list?user_id={self.user_id}')
        if response.status_code == 200:
            shifts = response.json().get('shifts', [])
            for shift in shifts:
                self.shift_combo_box.addItem(shift['shift_name'], shift['id'])  # Add shift to combo box
        else:
            QtWidgets.QMessageBox.warning(self, "Lỗi", "Không thể tải danh sách ca làm việc!")

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Convert frame to QImage
            height, width, channels = frame.shape
            bytes_per_line = channels * width
            image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
            pixmap = QPixmap(image)
            self.image_label.setPixmap(pixmap)

    def clock_in(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Convert image to file and send to Flask server
            _, img = cv2.imencode('.jpg', frame)
            files = {'image': ('face3.jpg', img.tobytes(), 'image/jpeg')}

            # Get the selected shift ID from the combo box
            selected_shift_id = self.shift_combo_box.currentData()

            # Send the clock-in request with the selected shift ID
            data = {'shift_id': selected_shift_id}
            response = requests.post(f'http://127.0.0.1:5000/clock-in/{self.user_id}', files=files, data=data)

            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Thông báo", "Chấm công thành công!")
            else:
                QtWidgets.QMessageBox.warning(self, "Lỗi", response.json().get("message", "Có lỗi xảy ra!"))

    # tắt thiết bị khi tắt chức năng
    def closeEvent(self, event):
        """Handle window close event and release the camera."""
        self.video_capture.release()  # Release the camera when the window is closed
        event.accept()  # Proceed with closing the window
