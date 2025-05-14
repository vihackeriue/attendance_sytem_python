from collections import defaultdict
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app import mysql
from app.helpers import role_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

import plotly.graph_objects as go

@main.route('/home', methods=['GET'])
@login_required
@role_required('manager')
def home():
    cursor = mysql.connection.cursor()

    # Lấy dữ liệu cho tháng này
    today = datetime.now().date()
    cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM attendance
            WHERE MONTH(check_in_time) = %s AND YEAR(check_in_time) = %s
            GROUP BY status
        """, (today.month, today.year))

    results = cursor.fetchall()
    cursor.close()

    # Khởi tạo số liệu thống kê cho tháng này
    status_counts = {'present': 0, 'late': 0, 'absent': 0}
    for row in results:
        status_counts[row[0]] = row[1]

    # Tạo biểu đồ tròn với Plotly
    fig_pie = go.Figure(data=[go.Pie(labels=['Đúng giờ', 'Trễ', 'Vắng'],
                                     values=[status_counts['present'], status_counts['late'], status_counts['absent']],
                                     textinfo='percent+label')])

    fig_pie.update_layout(title='Biểu đồ chấm công tháng này')

    # Lấy dữ liệu cho 12 tháng qua
    cursor = mysql.connection.cursor()
    cursor.execute("""
            SELECT MONTH(check_in_time) AS month, YEAR(check_in_time) AS year, status, COUNT(*) AS count
            FROM attendance
            WHERE YEAR(check_in_time) = %s
            GROUP BY YEAR(check_in_time), MONTH(check_in_time), status
            ORDER BY YEAR(check_in_time), MONTH(check_in_time)
        """, (today.year,))

    results = cursor.fetchall()
    cursor.close()

    # Khởi tạo số liệu thống kê cho 12 tháng qua
    stats_monthly = defaultdict(lambda: defaultdict(int))
    for row in results:
        month = f"{row[1]}-{row[0]}"  # Format: YYYY-MM
        status = row[2]
        count = row[3]
        stats_monthly[month][status] = count

    months = list(stats_monthly.keys())
    present_count = [stats_monthly[month].get('present', 0) for month in months]
    late_count = [stats_monthly[month].get('late', 0) for month in months]
    absent_count = [stats_monthly[month].get('absent', 0) for month in months]

    # Tạo biểu đồ cột với Plotly
    fig_bar = go.Figure(data=[
        go.Bar(name='Đúng giờ', x=months, y=present_count, marker_color='green'),
        go.Bar(name='Trễ', x=months, y=late_count, marker_color='orange'),
        go.Bar(name='Vắng', x=months, y=absent_count, marker_color='red')
    ])

    fig_bar.update_layout(
        barmode='stack',  # Để các cột chồng lên nhau
        title="Biểu đồ thống kê chấm công trong 12 tháng qua",
        xaxis_title="Tháng",
        yaxis_title="Số ca"
    )

    # Chuyển biểu đồ thành base64 để hiển thị trên website
    graph_pie = fig_pie.to_html(full_html=False)
    graph_bar = fig_bar.to_html(full_html=False)

    return render_template('home.html', graph_pie=graph_pie, graph_bar=graph_bar)




@main.route('/employee_dashboard')
@login_required
@role_required('employee')
def employee_dashboard():
    return render_template('employee_dashboard.html', full_name=current_user.full_name)
