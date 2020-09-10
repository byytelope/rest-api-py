import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import create_database, database_exists, drop_database

app = Flask(__name__)
CORS(app)
BASEDIR = os.path.abspath(os.path.dirname(__file__))

DB_URL = f"sqlite:///{os.path.join(BASEDIR, 'db.sqlite')}"

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))
    temperature = db.Column(db.String(10))
    img = db.Column(db.String(200))
    price = db.Column(db.Float)
    in_stock = db.Column(db.Boolean)

    def __init__(self, name, description, temperature, img, price, in_stock):
        self.name = name
        self.description = description
        self.temperature = temperature
        self.img = img
        self.price = price
        self.in_stock = in_stock


class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description", "temperature", "img", "price", "in_stock")


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@app.route("/products", methods=["POST"])
def add_product():
    name = request.json["name"]
    description = request.json["description"]
    temperature = request.json["temperature"]
    img = request.json["img"]
    price = request.json["price"]
    in_stock = request.json["in_stock"]

    new_product = Product(name, description, temperature, img, price, in_stock)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


@app.route("/products/<id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get(id)

    name = request.json["name"]
    description = request.json["description"]
    temperature = request.json["temperature"]
    img = request.json["img"]
    price = request.json["price"]
    in_stock = request.json["in_stock"]

    product.name = name
    product.description = description
    product.temperature = temperature
    product.img = img
    product.price = price
    product.in_stock = in_stock

    db.session.commit()

    return product_schema.jsonify(product)


@app.route("/products/<id>", methods=["GET"])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)


@app.route("/products", methods=["GET"])
def get_all_products():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)

    return jsonify(result)


@app.route("/products/<id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)


@app.cli.command("resetdb")
def resetdb_command():
    if database_exists(DB_URL):
        print("Deleting database.")
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print("Creating database.")
        create_database(DB_URL)

    print("Creating tables.")
    db.create_all()
    print("Shiny!")


if __name__ == "__main__":
    app.run(threaded=True)
