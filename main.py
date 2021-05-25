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
    return render_template('index.html')


# display random cafe
@app.route('/random')
def choose_random():
    cafes = db.session.query(Cafe).all()
    choice = random.choice(cafes)
    return j(x=choice)


# display all cafes — takes some type conversion due to trouble with jsonify
@app.route('/all', methods=['GET'])
def get_cafes():
    cafes = db.session.query(Cafe).all()

    # compile list of cafes
    cafe_list = []
    for c in cafes:
        entry = j(x=c).json
        cafe_list.append(entry)

    # convert list to dictionary for json output on screen
    cafe_json = {}
    for item in cafe_list:
        name = item['name']
        cafe_json[name] = item

    return cafe_json


# search via api for specific location, tenders first result
@app.route('/search')
def search():
    query_location = request.args.get('loc')
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return j(x=cafe)
    else:
        return jsonify(error={'Not Found': "Sorry, we don't have a cafe at that location."})


# adds cafe to database
@app.route('/add', methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('location'),
        seats=request.form.get('seats'),

        # booleans would TypeError crash without parser json.loads()
        has_toilet=json.loads(request.form.get('has_toilet')),
        has_wifi=json.loads(request.form.get('has_wifi')),
        has_sockets=json.loads(request.form.get('has_sockets')),
        can_take_calls=json.loads(request.form.get('can_take_calls')),

        coffee_price=request.form.get('coffee_price'),
    )

    db.session.add(new_cafe)
    db.session.commit()

    return redirect(url_for('home'))


# updates coffee price of a given cafe via id (id can be retreived via a get request)
@app.route('/update_price/<string:cafe_id>', methods=['GET', 'PATCH'])
def update_price(cafe_id):
    query_cafe = Cafe.query.get(cafe_id)

    if query_cafe:
        new_price = request.form.get('new_price')
        query_cafe.coffee_price = new_price
        db.session.commit()

        # passes along updated json as confirmation, plus 200 status code
        return j(x=query_cafe), 200

        # passes along json formatted error message (in keeping with style), plus 404 re: id
    else:
        return {'error': {'not found': 'no such id found'}}, 404


@app.route('/close_shop/<string:cafe_id>', methods=['GET', 'DELETE'])
def remove_entry(cafe_id):

    target_cafe = Cafe.query.get(cafe_id)

    if target_cafe:
        secret_key = request.form.get('secret_key')
        if secret_key == 'TopSecretKey':
            db.session.delete(target_cafe)
            db.session.commit()
            return {'removed': {'success': f'{target_cafe.name} deleted'}}, 404

        else:
            return {'error': {'forbidden': 'authorization failed'}}, 403

    else:
        return {'error': {'not found': 'no such id found'}}, 404


if __name__ == '__main__':
    app.run(debug=True)
