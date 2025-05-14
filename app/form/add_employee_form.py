from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, IntegerField, DecimalField, SelectField, FileField
from wtforms.validators import InputRequired, Length, Email, Optional
from datetime import date

class EmployeeForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[InputRequired(), Length(min=3, max=50)])
    password = PasswordField('Mật khẩu', validators=[InputRequired(), Length(min=6)])
    full_name = StringField('Họ và tên', validators=[InputRequired(), Length(max=255)])
    dob = DateField('Ngày sinh', format='%Y-%m-%d', validators=[Optional()])
    address = StringField('Địa chỉ', validators=[Optional(), Length(max=255)])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=15)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    role = SelectField('Vai trò', choices=[('manager', 'Manager'), ('employee', 'Employee')], default='employee')
    salary = DecimalField('Lương', places=2, default=0.00, validators=[Optional()])
    face = FileField('Ảnh Khuôn Mặt', validators=[Optional()])

