from flask_wtf import FlaskForm
from wtforms import  SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, equal_to

class LoginForm(FlaskForm):
    gebruikersnaam = StringField("Gebruikersnaam", validators=[
                                 DataRequired(), Length(min=2, max=20)])
    wachtwoord = PasswordField("Wachtwoord", validators=[DataRequired()])
    herinner = BooleanField("Herinner mij")
    indienen = SubmitField("Log in")
