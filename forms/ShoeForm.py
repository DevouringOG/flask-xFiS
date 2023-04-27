from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, FloatField, MultipleFileField
from wtforms.validators import DataRequired


class ShoeForm(FlaskForm):
    images = MultipleFileField("Upload a photo of sneakers in jpg format with the names: title.jpg и top.jpg",
                               validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    category = SelectField("Category", choices=["Men's Shoes", "Basketball Shoes", "Shoes", "Men's Golf Shoes"],
                           validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    submit = SubmitField("Add")
