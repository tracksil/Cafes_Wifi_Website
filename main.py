from flask import Flask, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, URL
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    image = StringField('Cafe Image (URL)', validators=[DataRequired(), URL()])
    location = StringField('Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    city = StringField('City Name', validators=[DataRequired()])
    sockets = SelectField('Has Sockets', choices=["Yes", "No"], validators=[DataRequired()])
    toilet = SelectField('Has Toilet', choices=["Yes", "No"], validators=[DataRequired()])
    wifi = SelectField('Has Wifi', choices=["Yes", "No"], validators=[DataRequired()])
    calls = SelectField('Can Take Calls', choices=["Yes", "No"], validators=[DataRequired()])
    seats = SelectField('How many seats they have', choices=["0-10", "10-20", "20-30", "30-40", "40-50", "50+"],
                        validators=[DataRequired()])
    price = StringField('Coffee Price in £', validators=[DataRequired()])
    submit = SubmitField('Submit')


class DeleteForm(FlaskForm):
    id = IntegerField('Cafe ID', validators=[DataRequired()])
    key = StringField('Key', validators=[DataRequired()])
    submit = SubmitField('Submit')


def to_dict(cafe_list):
    cafes_list = []
    for cafe in cafe_list:
        if cafe[5] == 1:
            sockets = 'Yes'
        else:
            sockets = 'No'
        if cafe[6] == 1:
            toilet = 'Yes'
        else:
            toilet = 'No'
        if cafe[7] == 1:
            wifi = 'Yes'
        else:
            wifi = 'No'
        if cafe[8] == 1:
            call = 'Yes'
        else:
            call = 'No'
        each_cafe = {
            'id': cafe[0],
            'name': cafe[1],
            'map_url': cafe[2],
            'img_url': cafe[3],
            'location': cafe[4],
            'has_sockets': sockets,
            'has_toilet': toilet,
            'has_wifi': wifi,
            'can_take_calls': call,
            'seats': cafe[9],
            'coffee_price': cafe[10]
        }
        cafes_list.append(each_cafe)
    return cafes_list


def create_cafe(cafe):
    sqlite_connection = sqlite3.connect('cafes.db')
    cursor = sqlite_connection.cursor()
    sql = '''INSERT INTO cafe
    (name,map_url,img_url,location,has_sockets,has_toilet,has_wifi,can_take_calls,seats,coffee_price)
    VALUES(?,?,?,?,?,?,?,?,?,?)'''
    cursor.execute(sql, cafe)
    sqlite_connection.commit()


all_info = ['Name', 'Map URL', 'Image URL', 'Location', 'Has Sockets',
            'Has Toilet', 'Has Wifi', 'Can Take Calls', 'Seats', 'Coffee Price']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/cafes', methods=['GET'])
def all_cafes():
    sqlite_connection = sqlite3.connect('cafes.db')
    cursor = sqlite_connection.cursor()

    rows = cursor.execute("""SELECT * from cafe""").fetchall()

    sqlite_connection.commit()
    sqlite_connection.close()

    list_of_cafes = to_dict(rows)

    return render_template('cafes.html', cafes=list_of_cafes, info=all_info)


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        if form.sockets.data == "Yes":
            socket = 1
        else:
            socket = 0
        if form.toilet.data == "Yes":
            toilet = 1
        else:
            toilet = 0
        if form.wifi.data == "Yes":
            wifi = 1
        else:
            wifi = 0
        if form.calls.data == "Yes":
            calls = 1
        else:
            calls = 0
        cafe = (form.cafe.data, form.location.data, form.image.data, form.city.data,
                socket, toilet, wifi, calls, form.seats.data, f"£{form.price.data}")
        create_cafe(cafe)
        return redirect(url_for('all_cafes'))
    return render_template('add.html', form=form)


@app.route('/delete', methods=["GET", "POST"])
def delete_cafe():
    form = DeleteForm()
    if form.validate_on_submit():
        if form.key.data == "TopSecretAPIKey":
            sqlite_connection = sqlite3.connect('cafes.db')
            cursor = sqlite_connection.cursor()
            sql = 'DELETE FROM cafe WHERE id=?'
            cursor.execute(sql, (form.id.data,))
            sqlite_connection.commit()

            return redirect(url_for('all_cafes'))

        else:
            return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."})

    return render_template('delete.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)
