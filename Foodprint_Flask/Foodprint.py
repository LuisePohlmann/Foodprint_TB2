# powershell: create virtualenvironment, start it and navigate to folder, then run
# install everything (flask, gunicorn, pandas ...)
# pip freeze > requirements.txt
import pandas as pd
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import InputRequired

import App
from config import Config

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


@app.route('/profile')
def profile():
    return 'Profile'


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


@app.route("/Me")
def Me():
    return render_template("Me.html")


if __name__ == "__main__":
    app = create()
    db.create_all(app=app)
    app.run(debug=True)
