from collections import defaultdict
from datetime import timedelta, datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app import mysql
from app.form.add_shift_form import ShiftForm
from app.helpers import role_required

shift = Blueprint('shift', __name__)

@shift.route('/shift/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_shift():
    form = ShiftForm()

    if form.validate_on_submit():
        shift_name = form.shift_name.data
        start_time = form.start_time.data
        end_time = form.end_time.data

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO shifts (shift_name, start_time, end_time)
            VALUES (%s, %s, %s)
        """, (shift_name, start_time, end_time))
        mysql.connection.commit()
        cursor.close()

        flash('Ca làm việc đã được thêm thành công!', 'success')
        return redirect(url_for('shift.shift_list'))

    return render_template('add_shift.html', form=form)


@shift.route('/shift/list', methods=['GET'])
@login_required
@role_required('manager')
def shift_list():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, shift_name, start_time, end_time FROM shifts")
    shifts = cursor.fetchall()
    cursor.close()

    return render_template('shift_list.html', shifts=shifts)


@shift.route('/shift/delete/<int:shift_id>', methods=['GET'])
@login_required
@role_required('manager')
def delete_shift(shift_id):
    # Tạo kết nối với cơ sở dữ liệu
    cursor = mysql.connection.cursor()

    # Xóa ca làm việc từ cơ sở dữ liệu
    cursor.execute("DELETE FROM shifts WHERE id = %s", (shift_id,))
    mysql.connection.commit()

    cursor.close()

    # Thông báo thành công và chuyển hướng về danh sách ca làm việc
    flash('Ca làm việc đã được xóa', 'success')
    return redirect(url_for('shift.shift_list'))


@shift.route('/shift/assign/<int:shift_id>', methods=['GET'])
@login_required
@role_required('manager')
def assign_employee_to_shift(shift_id):
    cursor = mysql.connection.cursor()

    # Lấy danh sách nhân viên chưa được gán vào ca làm việc này
    cursor.execute("""
        SELECT id, username, full_name FROM users
        WHERE id NOT IN (SELECT user_id FROM user_shift WHERE shift_id = %s)
        AND role != 'manager'
    """, (shift_id,))
    available_employees = cursor.fetchall()

    # Lấy danh sách nhân viên đã được gán vào ca làm việc này
    cursor.execute("""
        SELECT u.id, u.username, u.full_name FROM users u
        INNER JOIN user_shift us ON u.id = us.user_id
        WHERE us.shift_id = %s
    """, (shift_id,))
    assigned_employees = cursor.fetchall()

    cursor.close()

    return render_template('add_employee_to_shift.html', shift_id=shift_id,
                           employees=available_employees, assigned_employees=assigned_employees)


@shift.route('/shift/assign/<int:shift_id>', methods=['POST'])
@login_required
@role_required('manager')
def assign_employee_to_shift_post(shift_id):
    user_id = request.form['user_id']

    cursor = mysql.connection.cursor()

    # Kiểm tra nếu nhân viên đã được gán vào ca làm việc này
    cursor.execute("SELECT * FROM user_shift WHERE user_id = %s AND shift_id = %s", (user_id, shift_id))
    existing_assignment = cursor.fetchone()

    if existing_assignment:
        flash('Nhân viên này đã được gán vào ca làm việc này rồi', 'danger')
        return redirect(url_for('employee.assign_employee_to_shift', shift_id=shift_id))

    # Thêm nhân viên vào ca làm việc
    cursor.execute("""
        INSERT INTO user_shift (user_id, shift_id)
        VALUES (%s, %s)
    """, (user_id, shift_id))

    mysql.connection.commit()
    cursor.close()

    flash('Nhân viên đã được gán vào ca làm việc', 'success')
    return redirect(url_for('shift.assign_employee_to_shift', shift_id=shift_id))


@shift.route('/shift/remove_employee/<int:shift_id>/<int:user_id>', methods=['GET'])
@login_required
@role_required('manager')
def remove_employee_from_shift(shift_id, user_id):
    cursor = mysql.connection.cursor()

    # Xóa nhân viên khỏi ca làm việc trong bảng user_shift
    cursor.execute("""
        DELETE FROM user_shift
        WHERE shift_id = %s AND user_id = %s
    """, (shift_id, user_id))

    mysql.connection.commit()
    cursor.close()

    flash('Nhân viên đã được xóa khỏi ca làm việc', 'success')
    return redirect(url_for('shift.assign_employee_to_shift', shift_id=shift_id))


@shift.route('/api/shift/list', methods=['GET'])
def get_api_shift_list_by_user():
    # Lấy user_id từ tham số truy vấn
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        # Mở một cursor mới cho kết nối MySQL
        cursor = mysql.connection.cursor()

        # Truy vấn để lấy thông tin ca làm việc từ bảng shifts, kết hợp với bảng user_shift
        query = """
            SELECT s.id, s.shift_name, s.start_time, s.end_time
            FROM shifts s
            JOIN user_shift us ON s.id = us.shift_id
            WHERE us.user_id = %s
            ORDER BY s.start_time ASC
        """
        cursor.execute(query, (user_id,))
        shifts = cursor.fetchall()

        cursor.close()

        # Nếu không có ca làm việc, trả về danh sách rỗng
        shift_list = []
        if shifts:
            # Chuyển đổi đối tượng datetime hoặc timedelta thành chuỗi để JSON có thể serializable
            for shift in shifts:
                start_time = shift[2]
                end_time = shift[3]

                # Kiểm tra nếu là timedelta và chuyển thành chuỗi
                if isinstance(start_time, timedelta):
                    # Nếu là timedelta, chuyển thành giờ và phút
                    start_time = str(start_time)
                elif isinstance(start_time, datetime):
                    # Nếu là datetime, định dạng theo HH:MM
                    start_time = start_time.strftime('%H:%M')

                if isinstance(end_time, timedelta):
                    # Nếu là timedelta, chuyển thành giờ và phút
                    end_time = str(end_time)
                elif isinstance(end_time, datetime):
                    # Nếu là datetime, định dạng theo HH:MM
                    end_time = end_time.strftime('%H:%M')

                shift_data = {
                    "id": shift[0],
                    "shift_name": shift[1],
                    "start_time": start_time,  # Chuyển đổi từ datetime hoặc timedelta
                    "end_time": end_time      # Chuyển đổi từ datetime hoặc timedelta
                }
                shift_list.append(shift_data)

        # Trả về danh sách ca làm việc dưới dạng JSON, có thể là danh sách rỗng
        return jsonify({"shifts": shift_list}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@shift.route('/api/shift/history', methods=['GET'])
def get_attendance_history():
    user_id = request.args.get('user_id', type=int)

    if not user_id:
        return jsonify({"message": "User ID không hợp lệ"}), 400

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT attendance.id, shifts.shift_name, attendance.check_in_time, attendance.status
        FROM attendance
        JOIN shifts ON attendance.shift_id = shifts.id
        WHERE attendance.employee_id = %s
        ORDER BY attendance.check_in_time DESC
    """, (user_id,))

    attendance_records = cursor.fetchall()
    cursor.close()

    # If no attendance records, return an empty list
    if not attendance_records:
        return jsonify({"shifts": []})

    # Prepare the attendance records in a structured format
    shifts = [
        {
            "id": record[0],
            "shift_name": record[1],
            "check_in_time": record[2].strftime("%Y-%m-%d %H:%M:%S"),
            "status": record[3]
        }
        for record in attendance_records
    ]

    return jsonify({"shifts": shifts})

import requests
from decimal import Decimal
@shift.route('/employee/history/<int:user_id>', methods=['GET'])
def employee_history(user_id):
    # Kiểm tra tính hợp lệ của user_id
    if not user_id:
        return "User ID không hợp lệ", 400

    # Gọi API để lấy dữ liệu lịch sử chấm công
    response = requests.get(f'http://127.0.0.1:5000/api/shift/history?user_id={user_id}')

    if response.status_code != 200:
        return "Không thể lấy dữ liệu lịch sử chấm công", 500

    # Parse dữ liệu trả về từ API
    data = response.json()
    shifts = data.get('shifts', [])

    # Tính toán thống kê
    total_shifts = len(shifts)
    present_count = sum(1 for shift in shifts if shift['status'] == 'present')
    late_count = sum(1 for shift in shifts if shift['status'] == 'late')
    absent_count = sum(1 for shift in shifts if shift['status'] == 'absent')

    # Lấy mức lương cơ bản của nhân viên từ bảng users
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT salary FROM users WHERE id = %s
    """, (user_id,))
    salary = cursor.fetchone()[0]
    salary = Decimal(salary)

    # Tính tiền lương: salary * present_count + (salary * 10% của late_count)
    total_salary = salary * present_count + (salary * Decimal('0.10') * late_count)
    # Định dạng tiền tệ
    formatted_salary = "{:,.2f}".format(total_salary)
    # Trả về thống kê và tiền lương dưới dạng JSON
    stats = {
        "total_shifts": total_shifts,
        "present_count": present_count,
        "late_count": late_count,
        "absent_count": absent_count,
        "total_salary": formatted_salary  # Tiền lương tính toán được
    }

    # Render template và truyền dữ liệu cho template
    return render_template('employee_history.html', shifts=shifts, stats=stats)







