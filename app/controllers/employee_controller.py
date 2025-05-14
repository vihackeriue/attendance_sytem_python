from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import mysql
from app.form.add_employee_form import EmployeeForm
from werkzeug.security import generate_password_hash
from app.helpers import role_required
from werkzeug.utils import secure_filename
import face_recognition
import cv2
import os
import numpy as np

employee = Blueprint('employee', __name__)




@employee.route('/employee/add_or_edit/<int:user_id>', methods=['GET', 'POST'])
@employee.route('/employee/add_or_edit/', methods=['GET', 'POST'])
@login_required
@role_required('manager')
# def add_or_edit_employee(user_id=None):
#     # Nếu có user_id, lấy thông tin nhân viên
#     if user_id:
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT id, username, full_name, dob, address, phone, email, role, salary, manager_id FROM users WHERE id = %s", (user_id,))
#         user = cursor.fetchone()
#         cursor.close()
#
#         # Nếu không tìm thấy nhân viên
#         if not user:
#             flash('Nhân viên không tồn tại', 'danger')
#             return redirect(url_for('main.employee_list'))
#
#         # Tạo form với dữ liệu của nhân viên cần chỉnh sửa
#         form = EmployeeForm(obj=user)  # Dữ liệu cũ sẽ được điền vào form
#     else:
#         # Nếu không có user_id, tạo form trống để thêm nhân viên mới
#         form = EmployeeForm()
#
#     if form.validate_on_submit():
#         username = form.username.data
#         password = generate_password_hash(form.password.data)  # Mã hóa mật khẩu
#         full_name = form.full_name.data
#         dob = form.dob.data
#         address = form.address.data
#         phone = form.phone.data
#         email = form.email.data
#         role = form.role.data
#         salary = form.salary.data
#
#         # Thêm hoặc cập nhật dữ liệu vào cơ sở dữ liệu
#         cursor = mysql.connection.cursor()
#         if user_id:
#             # Cập nhật thông tin nhân viên (bỏ qua trường status)
#             cursor.execute("""
#                 UPDATE users
#                 SET username = %s, password = %s, full_name = %s, dob = %s, address = %s, phone = %s, email = %s,
#                     role = %s, salary = %s, manager_id = %s
#                 WHERE id = %s
#             """, (username, password, full_name, dob, address, phone, email, role, salary, current_user.id, user_id))  # Cập nhật thông tin mà không thay đổi status
#             flash('Thông tin nhân viên đã được cập nhật', 'success')
#         else:
#             # Thêm nhân viên mới
#             cursor.execute("""
#                 INSERT INTO users (username, password, full_name, dob, address, phone, email, role, salary, manager_id)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """, (username, password, full_name, dob, address, phone, email, role, salary, current_user.id))  # Sử dụng `current_user.id` làm manager_id
#             flash('Nhân viên mới đã được thêm', 'success')
#
#         mysql.connection.commit()
#         cursor.close()
#
#         return redirect(url_for('employee.employee_list'))
#
#     return render_template('add_employee.html', form=form, user=user if user_id else None)

def add_or_edit_employee(user_id=None):
    # Nếu có user_id, lấy thông tin nhân viên
    if user_id:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, full_name, dob, address, phone, email, role, salary, manager_id, face_vector FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            flash('Nhân viên không tồn tại', 'danger')
            return redirect(url_for('main.employee_list'))

        form = EmployeeForm(obj=user)
    else:
        form = EmployeeForm()

    # Đảm bảo thư mục 'uploads' tồn tại
    upload_folder = os.path.join('static', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)  # Tạo thư mục nếu chưa tồn tại

    if form.validate_on_submit():
        username = form.username.data
        password = generate_password_hash(form.password.data)  # Mã hóa mật khẩu
        full_name = form.full_name.data
        dob = form.dob.data
        address = form.address.data
        phone = form.phone.data
        email = form.email.data
        role = form.role.data
        salary = form.salary.data

        # Xử lý khuôn mặt nếu có ảnh khuôn mặt được tải lên
        face_encoding = None
        if form.face.data:
            file = form.face.data
            if file:
                filename = secure_filename(file.filename)  # Lấy tên tệp an toàn
                filepath = os.path.join(upload_folder, filename)  # Đặt đường dẫn lưu tệp
                file.save(filepath)  # Lưu tệp vào thư mục đã chỉ định

                # Chuyển đổi ảnh khuôn mặt thành mã hóa khuôn mặt
                image = cv2.imread(filepath)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_image)

                if len(face_encodings) > 0:
                    face_encoding = face_encodings[0].tobytes()  # Chuyển numpy array thành bytes
                else:
                    flash('Không thể nhận diện khuôn mặt trong ảnh', 'danger')
                    return redirect(url_for('employee.employee_list'))

        cursor = mysql.connection.cursor()
        if user_id:
            cursor.execute("""
                UPDATE users 
                SET username = %s, password = %s, full_name = %s, dob = %s, address = %s, phone = %s, email = %s, 
                    role = %s, salary = %s, manager_id = %s, face_vector = %s
                WHERE id = %s
            """, (username, password, full_name, dob, address, phone, email, role, salary, current_user.id, face_encoding if face_encoding else None, user_id))
            flash('Thông tin nhân viên đã được cập nhật', 'success')
        else:
            cursor.execute("""
                INSERT INTO users (username, password, full_name, dob, address, phone, email, role, salary, manager_id, face_vector)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, password, full_name, dob, address, phone, email, role, salary, current_user.id, face_encoding if face_encoding else None))
            flash('Nhân viên mới đã được thêm', 'success')

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('employee.employee_list'))

    return render_template('add_employee.html', form=form, user=user if user_id else None)

@employee.route('/employee/list')
@login_required
@role_required('manager')
def employee_list():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, username, full_name, email, phone, salary, status, manager_id FROM users WHERE role != 'manager'
    """)
    employees = cursor.fetchall()
    cursor.close()

    return render_template('employee_list.html', users=employees)


@employee.route('/employee/lock/<int:user_id>', methods=['GET'])
@login_required
@role_required('manager')
def lock_employee(user_id):
    # Xử lý khóa người dùng
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET status = 0 WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()
    flash('Nhân viên đã bị khóa', 'success')
    return redirect(url_for('employee.employee_list'))

@employee.route('/employee/view/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def view_employee(user_id):
    # Lấy thông tin nhân viên và cho phép chỉnh sửa thông tin
    pass


# Lấy danh sách nhân viên và mã hóa khuôn mặt
def get_employee_face_encoding(employee_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, face_vector FROM users WHERE id = %s", (employee_id,))
    employee = cursor.fetchone()
    cursor.close()
    cursor.close()

    if employee:
        face_vector = employee[1]
        if face_vector:
            return np.frombuffer(face_vector)
    return None

# Route chấm công
@employee.route('/clock-in/<int:user_id>', methods=['POST'])
def clock_in(user_id):
    # Lấy mã hóa khuôn mặt của nhân viên từ cơ sở dữ liệu
    stored_face_encoding = get_employee_face_encoding(user_id)

    if stored_face_encoding is None or stored_face_encoding.size == 0:
        return jsonify({"message": "Không tìm thấy khuôn mặt của nhân viên"}), 404

    # Nhận diện khuôn mặt từ ảnh chụp qua webcam
    file = request.files.get('image')  # Ảnh chụp từ client (webcam)

    # Lấy shift_id từ POST data
    shift_id = request.form.get('shift_id')

    if not shift_id:
        return jsonify({"message": "Shift ID không hợp lệ"}), 400

    # Kiểm tra nếu có ảnh và lưu ảnh
    upload_folder = os.path.join('static', 'uploads')
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        image = cv2.imread(filepath)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_image)

        if len(face_encodings) > 0:
            # So sánh khuôn mặt từ ảnh chụp với khuôn mặt trong cơ sở dữ liệu
            threshold = 0.4  # Ngưỡng so sánh, điều chỉnh ngưỡng nếu cần
            match = face_recognition.compare_faces([stored_face_encoding], face_encodings[0], tolerance=threshold)

            if match[0]:
                # Lấy thông tin ca làm việc từ cơ sở dữ liệu
                cursor = mysql.connection.cursor()
                cursor.execute("""SELECT start_time, end_time FROM shifts WHERE id = %s""", (shift_id,))
                shift = cursor.fetchone()

                if shift is None:
                    return jsonify({"message": "Không tìm thấy ca làm việc"}), 404

                # Chuyển đổi shift_start_time từ string 'HH:MM:SS' thành datetime
                shift_start_time_str = shift[0]  # shift_start_time là kiểu 'HH:MM:SS'
                shift_start_time = datetime.strptime(str(shift_start_time_str), "%H:%M:%S").replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

                shift_end_time = shift[1]  # shift_end_time có thể cần xử lý tương tự nếu nó là 'HH:MM:SS'

                # Kiểm tra thời gian hiện tại có nằm trong khoảng thời gian của ca làm việc không
                current_time = datetime.now()

                if current_time < shift_start_time:
                    return jsonify({"message": "Chưa đến giờ làm việc"}), 400

                # Kiểm tra thời gian trễ
                time_diff = current_time - shift_start_time  # time_diff là đối tượng timedelta

                # Kiểm tra thời gian trễ bằng cách lấy số phút trong timedelta
                if time_diff <= timedelta(minutes=10):
                    status = 'present'
                elif time_diff <= timedelta(minutes=20):
                    status = 'late'
                else:
                    return jsonify({"message": "Trễ quá 20 phút, không thể chấm công"}), 400

                # Thực hiện chấm công
                cursor.execute("""INSERT INTO attendance (employee_id, check_in_time, status, shift_id)
                                  VALUES (%s, %s, %s, %s)""", (user_id, current_time, status, shift_id))
                mysql.connection.commit()
                cursor.close()
                return jsonify({"message": "Chấm công thành công!"}), 200
            else:
                return jsonify({"message": "Khuôn mặt không khớp!"}), 400
        else:
            return jsonify({"message": "Không phát hiện khuôn mặt!"}), 400

    return jsonify({"message": "Không có ảnh được gửi đến"}), 400


from decimal import Decimal
from flask import jsonify

@employee.route('/api/employee/salary/<int:month>/<int:year>', methods=['GET'])
def employee_salary_by_month_api(month, year):
    cursor = mysql.connection.cursor()

    # Thực hiện truy vấn SQL để tính tổng lương
    cursor.execute("""
        SELECT
            u.id AS employee_id,
            u.full_name,
            u.salary,
            SUM(
                CASE 
                    WHEN a.status = 'present' THEN u.salary
                    WHEN a.status = 'late' THEN u.salary * 0.9
                    ELSE 0
                END
            ) AS total_salary,
            a.salary_status,
            MONTH(a.check_in_time) AS month,
            YEAR(a.check_in_time) AS year
        FROM
            attendance a
        JOIN
            users u ON a.employee_id = u.id
        WHERE
            MONTH(a.check_in_time) = %s AND YEAR(a.check_in_time) = %s
        GROUP BY
            a.employee_id, a.salary_status, YEAR(a.check_in_time), MONTH(a.check_in_time)
        ORDER BY
            employee_id, year, month
    """, (month, year))

    results = cursor.fetchall()
    cursor.close()

    # Dữ liệu trả về sẽ bao gồm thông tin tổng lương của nhân viên
    employees_salary = []

    for row in results:
        employee_id, full_name, salary, total_salary, salary_status, month, year = row
        employees_salary.append({
            'employee_id': employee_id,
            'full_name': full_name,
            'salary': "{:,.2f}".format(salary),
            'total_salary': "{:,.2f}".format(total_salary),
            'salary_status': 'Paid' if salary_status == 1 else 'Unpaid',
            'month': month,
            'year': year
        })

    return jsonify({'employees_salary': employees_salary})

import requests
import plotly.graph_objects as go
from plotly.io import to_html

@employee.route('/employee/salary', methods=['GET'])
@login_required
@role_required('manager')
def employee_salary():
    # Lấy tháng và năm từ URL (hoặc mặc định tháng và năm hiện tại)
    month = request.args.get('month', default=datetime.now().month, type=int)
    year = request.args.get('year', default=datetime.now().year, type=int)

    # Gọi API nội bộ để lấy dữ liệu lương của nhân viên
    response = requests.get(f'http://127.0.0.1:5000/api/employee/salary/{month}/{year}')

    if response.status_code != 200:
        return "Không thể lấy dữ liệu lương", 500

    # Parse dữ liệu trả về từ API
    data = response.json()
    employees_salary = data.get('employees_salary', [])

    # Thống kê số tiền đã thanh toán và chưa thanh toán
    paid_total = sum(Decimal(emp['total_salary'].replace(',', '')) for emp in employees_salary if emp['salary_status'] == 'Paid')
    unpaid_total = sum(Decimal(emp['total_salary'].replace(',', '')) for emp in employees_salary if emp['salary_status'] == 'Unpaid')

    # Tạo biểu đồ tròn sử dụng Plotly
    fig_pie = go.Figure(data=[go.Pie(labels=['Đã Thanh Toán', 'Chưa Thanh Toán'],
                                     values=[paid_total, unpaid_total],
                                     textinfo='percent+label',
                                     marker_colors=['#2ca02c', '#d62728'])])

    fig_pie.update_layout(title=f"Tổng Lương Nhân Viên Tháng {month}/{year}")

    # Chuyển plot thành HTML và render template
    chart_html = to_html(fig_pie, full_html=False)

    return render_template('employee_salary.html', employees_salary=employees_salary, month=month, year=year, chart_html=chart_html)


@employee.route('/employee/salary/detail/<int:employee_id>', methods=['GET'])
@login_required
@role_required('manager')
def employee_salary_detail(employee_id):
    cursor = mysql.connection.cursor()

    # Truy vấn thông tin chi tiết về nhân viên
    cursor.execute("""
        SELECT id, full_name, salary, status, role FROM users WHERE id = %s
    """, (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        return jsonify({"message": "Employee not found"}), 404

    # Truy vấn các ca chấm công chưa thanh toán
    cursor.execute("""
        SELECT a.id, s.shift_name, a.check_in_time, a.check_out_time, a.status
        FROM attendance a
        JOIN shifts s ON a.shift_id = s.id
        WHERE a.employee_id = %s AND a.salary_status = 0
    """, (employee_id,))
    attendance_details = cursor.fetchall()

    # Tính tổng tiền thanh toán
    total_payment = 0
    salary = employee[2]  # Lấy lương cơ bản của nhân viên

    for attendance in attendance_details:
        if attendance[4] == 'present':  # Kiểm tra trạng thái 'present'
            total_payment += salary
        elif attendance[4] == 'late':  # Kiểm tra trạng thái 'late'
            total_payment += Decimal(salary) * Decimal('0.9')   # giảm 10% khi đi trễ

    cursor.close()

    # Chuẩn bị dữ liệu trả về
    employee_data = {
        "employee_id": employee[0],
        "full_name": employee[1],
        "salary": "{:,.0f}".format(employee[2]),
        "status": "Active" if employee[3] == 1 else "Inactive",
        "role": employee[4],
        "attendance_details": [
            {
                "attendance_id": a[0],
                "shift_name": a[1],
                "check_in_time": a[2].strftime('%Y-%m-%d %H:%M:%S'),
                "check_out_time": a[3].strftime('%Y-%m-%d %H:%M:%S') if a[3] else None,
                "status": a[4]
            }
            for a in attendance_details
        ],
        "total_payment": "{:,.0f}".format(total_payment)
    }

    return render_template('employee_salary_detail.html', employee=employee_data)


@employee.route('/employee/pay_salary/<int:employee_id>', methods=['POST'])
@login_required
@role_required('manager')
def pay_salary(employee_id):
    cursor = mysql.connection.cursor()

    # Cập nhật trạng thái salary_status = 1 cho các ca chưa thanh toán
    cursor.execute("""
        UPDATE attendance
        SET salary_status = 1
        WHERE employee_id = %s AND salary_status = 0
    """, (employee_id,))
    mysql.connection.commit()

    cursor.close()

    return redirect(url_for('employee.employee_salary'))



