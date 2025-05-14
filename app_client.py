import sys
import cv2
import requests
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget

class ClockInApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Chấm Công Khuôn Mặt')
        self.setGeometry(100, 100, 640, 480)

        self.video_capture = cv2.VideoCapture(0)  # Khởi tạo camera
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.clock_in_button = QPushButton("Chấm Công", self)
        self.clock_in_button.clicked.connect(self.clock_in)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.clock_in_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.timer.start(30)  # Cập nhật hình ảnh mỗi 30ms

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
            # Chuyển đổi hình ảnh thành tệp và gửi lên server Flask
            _, img = cv2.imencode('.jpg', frame)
            files = {'image': ('face.jpg', img.tobytes(), 'image/jpeg')}
            user_id = 9  # Đây là ID nhân viên, thay thế bằng cách lấy từ session hoặc nhập vào

            response = requests.post(f'http://127.0.0.1:5000/clock-in/{user_id}', files=files)
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Thông báo", "Chấm công thành công!")
            else:
                QtWidgets.QMessageBox.warning(self, "Lỗi", response.json().get("message", "Có lỗi xảy ra!"))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ClockInApp()
    window.show()
    sys.exit(app.exec_())
