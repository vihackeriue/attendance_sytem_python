from flask_wtf import FlaskForm
from wtforms import StringField, TimeField
from wtforms.validators import InputRequired

class ShiftForm(FlaskForm):
    shift_name = StringField('Tên ca làm việc', validators=[InputRequired()])
    start_time = TimeField('Thời gian bắt đầu', format='%H:%M', validators=[InputRequired()])
    end_time = TimeField('Thời gian kết thúc', format='%H:%M', validators=[InputRequired()])
