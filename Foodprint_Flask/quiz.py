from flask_wtf import FlaskForm as Form
from wtforms import RadioField
from wtforms.validators import ValidationError
from random import randrange

points = 0


class CorrectAnswer(object):
    def __init__(self, answer):
        self.answer = answer

    def __call__(self, form, field):
        message = 'Incorrect answer.'
        if field.data != self.answer:
            raise ValidationError(message)
        global points
        points+=1

questions = 2
class PopQuiz(Form):
    class Meta:
        csrf = False

    q1 = RadioField(
        "The answer to question one is False.",
        choices=[('True', 'True'), ('False', 'False')],
        validators=[CorrectAnswer('False')]
    )
    q2 = RadioField(
        "The answer to question two is False.",
        choices=[('JES', 'JES'), ('False', 'False'), ("NO", "NO"), ("Yes", "Yes")],
        validators=[CorrectAnswer('JES')]
    )
