from flask import Flask, jsonify, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import random
import json
from pprint import pprint

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

def j(x):
    return jsonify({
        'id': x.id,
        'name': x.name,
        'map_url': x.map_url,
        'img_url': x.img_url,
        'location': x.location,
        'seats': x.seats,
        'has_toilet': x.has_toilet,
        'has_wifi': x.has_wifi,
        'has_sockets': x.has_sockets,
        'can_take_calls': x.can_take_calls,
        'coffee_price': x.coffee_price,
    })


@app.route("/")
def home():
    return render_template("index.html")


# http GET route
@app.route('/random')
def choose_random():
    cafes = db.session.query(Cafe).all()
    choice = random.choice(cafes)
    return j(x=choice)


@app.route("/all")
def get_cafes():
    cafes = db.session.query(Cafe).all()

    # compile list of cafes
    cafe_list = []
    for c in cafes:
        entry = j(x=c).json
        cafe_list.append(entry)

    # convert list to dictionary — why?
    cafe_json = {}
    for item in cafe_list:
        name = item['name']
        cafe_json[name] = item

    # example of iteration (personal reference)
    # for x in cafe_json:
    #     print(cafe_json[x]['has_wifi'])

    return cafe_json



@app.route('/search')
def search():

    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return j(x=cafe)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})

if __name__ == '__main__':
    app.run(debug=True)
