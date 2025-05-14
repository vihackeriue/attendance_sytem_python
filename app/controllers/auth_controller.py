from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import User
from app import mysql
from flask_login import current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Nếu đã đăng nhập, chuyển sang trang chính
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, password, full_name, role FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[3], user_data[4])
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@auth.route('/api/login', methods=['POST'])
def loginAPI():
    username = request.json.get('username')
    password = request.json.get('password')

    # Truy vấn người dùng từ cơ sở dữ liệu
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, username, password, full_name, role FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()
    cursor.close()

    # Kiểm tra tên đăng nhập và mật khẩu
    if user_data and check_password_hash(user_data[2], password):
        user = User(user_data[0], user_data[1], user_data[3], user_data[4])
        login_user(user)
        return jsonify({"message": "Login successful", "user_id": user.id, "role": user.role}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 400


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))
