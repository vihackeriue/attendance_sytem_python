from datetime import datetime

from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager

mysql = MySQL()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.secret_key = 'your_secret_key'

    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = '123456'
    app.config['MYSQL_DB'] = 'attendance_system'

    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.controllers.home_controller import main as main_blueprint
    from app.controllers.auth_controller import auth as auth_blueprint
    from app.controllers.employee_controller import employee as employee_blueprint
    from app.controllers.shift_controller import shift as shift_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(employee_blueprint)
    app.register_blueprint(shift_blueprint)

    start_scheduler(app)
    return app

# Hàm kiểm tra và tự động cập nhật trạng thái vắng mặt
def auto_check_in_absent():
    cursor = mysql.connection.cursor()

    today = datetime.now().date()

    # Truy vấn các ca làm việc trong ngày hôm nay
    cursor.execute("""
        SELECT u.id, us.shift_id, s.end_time
        FROM user_shift us
        JOIN users u ON us.employee_id = u.id
        JOIN shifts s ON us.shift_id = s.id
    """, (today,))

    shifts_today = cursor.fetchall()

    for shift in shifts_today:
        employee_id = shift[0]
        shift_id = shift[1]
        shift_end_time = shift[2]

        # Chuyển đổi giờ kết thúc của ca làm việc thành datetime
        shift_end_time = datetime.combine(today, shift_end_time)

        # Kiểm tra xem nhân viên có điểm danh chưa
        cursor.execute("""
            SELECT COUNT(*) FROM attendance
            WHERE employee_id = %s AND shift_id = %s AND check_in_time >= %s
        """, (employee_id, shift_id, shift_end_time))

        count = cursor.fetchone()[0]

        if count == 0:
            # Nếu không có điểm danh trong ca, thêm bản ghi vắng mặt
            cursor.execute("""
                INSERT INTO attendance (employee_id, check_in_time, status, shift_id)
                VALUES (%s, %s, %s, %s)
            """, (employee_id, shift_end_time, 'absent', shift_id))
            mysql.connection.commit()

    cursor.close()

from apscheduler.schedulers.background import BackgroundScheduler
# Hàm này sẽ chạy sau khi ca làm việc kết thúc để kiểm tra vắng mặt và tự động thêm trạng thái absent
def start_scheduler(app):
    scheduler = BackgroundScheduler()
    # Thực hiện kiểm tra vào lúc giờ kết thúc của ca làm việc (ví dụ 10 phút sau giờ kết thúc)
    scheduler.add_job(auto_check_in_absent, 'cron', minute=59, hour=23)  # Cập nhật thời gian kiểm tra theo ca làm việc của bạn
    scheduler.start()

    # Lưu scheduler vào ứng dụng Flask để dừng khi ứng dụng ngừng
    app.scheduler = scheduler

