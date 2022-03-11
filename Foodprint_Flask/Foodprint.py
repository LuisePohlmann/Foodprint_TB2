# powershell: create virtualenvironment, start it and navigate to folder, then run
# install everything (flask, gunicorn, pandas ...)
# pip freeze > requirements.txt

import pandas as pd
from flask import request, flash, Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import SelectField
from wtforms.validators import InputRequired

import App
import models
from config import Config
from quiz import PopQuiz

db = SQLAlchemy()
df = App.get_values()
list_of_foods = App.list(df)
app = Flask(__name__)


def create():
    global app
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from Foodprint_Flask.models import User
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app

    return app


class AddFoodForm(FlaskForm):
    new_food = SelectField('Food', validators=[InputRequired()])
    plastic = SelectField("Plastic")


@app.route("/Home", methods=["POST", "GET"])
def home():
    thisweek = App.totals()
    form = AddFoodForm()
    return render_template("Home.html", thisweek_CO2=thisweek["CO2"], thisweek_water=thisweek["water"], thisweek_plastic=thisweek["plastic"], form=form)


@app.route("/seasonal")
def seasonal():
    return redirect("https://www.seasonalfoodguide.org/")


@app.route("/Quiz")
def quiz():
    return render_template("Quiz.html")


@app.route("/passed")
def passed():
    return render_template("passed.html")


@app.route("/quiz", methods=["GET", "POST"])
def wtf_quiz():
    form = PopQuiz()
    form.validate_on_submit()
    from quiz import points, questions, quiz_achieve
    if points / questions >= quiz_achieve:
        return render_template("passed.html", value=f"Youve gotten {(points / questions) * 100}% of the questions right")

    return render_template("quiz.html", form=form)


@app.route("/Add_Food", methods=["POST", "GET"])
def add_food():
    form = AddFoodForm()
    form.new_food.choices = list_of_foods
    form.plastic.choices = [0, 1, 2, 3]
    if form.validate_on_submit():
        new_food = form.new_food.data
        plastic = form.plastic.data
        food = df[df["Food product"] == new_food]
        App.get_footprints(food, plastic)
        CO2 = float(food["CO2"] / 10)
        water = float(food["Water"] / 10)
        return render_template("added_Food.html", new_food=new_food, CO2=CO2, water=water, plastic=plastic)
    return render_template("Add_Food.html", form=form)


@app.route("/Statistics")
def stats():
    import pandas as pd
    App.last_weeks(pd.read_csv("data/history.csv", index_col=[0]))
    data = App.sort_for_stats(pd.read_csv("data/week_1.csv", index_col=[0]))
    weeks = App.compare_weeks()
    CO2_max = App.largest_table(pd.read_csv("data/history.csv", index_col=[0]))[1]
    CO2_max_table = CO2_max.to_html()
    water_max = App.largest_table(pd.read_csv("data/history.csv", index_col=[0]))[0]
    water_max_table = water_max.to_html()
    return render_template("Statistics.html", labels=data[0], CO2_values=data[1], water_values=data[2], plastic_values=data[3], labels_weeks=weeks[0], CO2_weeks=weeks[1], water_weeks=weeks[2], message1=weeks[3], message2=weeks[4], tables=[CO2_max_table, water_max_table], titles=["CO2 Maximum", "Water Maximum"])


@app.route("/test")
def test():
    data = App.sort_for_stats(pd.read_csv("data/week_1.csv", index_col=[0]))
    return render_template("test.html", labels=data[0], CO2_values=data[1], water_values=data[2], plastic_values=data[3])


@app.route("/")
def Login():
    return render_template("Login.html")


@app.route("/Tips")
def Tips():
    return render_template("Tips.html")


@app.route("/Me", methods=["POST", "GET"])
def Me():
    from auth import loggedInUser as liu
    if liu is None:
        return redirect(url_for('auth.login'))
    return render_template("Me.html")


@app.route("/User")
def User():
    from auth import loggedInUser as liu
    if liu is not None:
        return render_template("User.html")
    return redirect(url_for('auth.login'))


@app.route("/usernameChange", methods=["POST"])
def user_change():
    username = request.form.get("username")
    password_current = request.form.get("password")
    from auth import loggedInUser as liu
    if not check_password_hash(liu.password, password_current):
        flash('Current password is incorrect')
        return redirect(url_for('User'))
    if liu is not None:
        user = models.User().query.filter_by(id=liu.id).first()
        user.name = username
        liu.name = username
        db.session.commit()
        return redirect(url_for('Me'))
    else:
        return redirect(url_for('auth.login'))


@app.route("/Password")
def Password():
    from auth import loggedInUser as liu
    if liu is not None:
        return render_template("password_change.html")
    return redirect(url_for('auth.login'))


@app.route("/passwordChange", methods=["POST"])
def password_change():
    password_again = request.form.get("again_password")
    password_new = request.form.get("new_password")
    password_current = request.form.get("current_password")
    if password_new != password_again:
        flash('Passwords do not match')
        return redirect(url_for('Password'))
    from auth import loggedInUser as liu
    if not check_password_hash(liu.password, password_current):
        flash('Current password is incorrect')
        return redirect(url_for('Password'))
    if liu is not None:

        user = models.User().query.filter_by(id=liu.id).first()
        user.password = generate_password_hash(password_new, method='sha256')
        liu.password = generate_password_hash(password_new, method='sha256')
        db.session.commit()
        return redirect(url_for('Me'))
    else:
        return redirect(url_for('auth.login'))


if __name__ == "__main__":
    app = create()
    db.create_all(app=app)
    app.run(debug=True)
