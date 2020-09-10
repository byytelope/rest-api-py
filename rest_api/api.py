import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

DB_URL = os.environ["DATABASE_URL"]

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(400))
    is_cold = db.Column(db.Boolean)
    is_hot = db.Column(db.Boolean)
    img = db.Column(db.String(400))
    price = db.Column(db.Float)
    in_stock = db.Column(db.Boolean)

    def __init__(self, name, description, is_cold, is_hot, img, price, in_stock):
        self.name = name
        self.description = description
        self.is_cold = is_cold
        self.is_hot = is_hot
        self.img = img
        self.price = price
        self.in_stock = in_stock


class ProductSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description", "is_cold", "is_hot", "img", "price", "in_stock")


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)


@app.route("/")
def home():
    return "<h1>It work la.</h1>"


@app.route("/products", methods=["POST"])
def add_product():
    name = request.json["name"]
    description = request.json["description"]
    is_cold = request.json["is_cold"]
    is_hot = request.json["is_hot"]
    img = request.json["img"]
    price = request.json["price"]
    in_stock = request.json["in_stock"]

    new_product = Product(name, description, is_cold, is_hot, img, price, in_stock)

    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


@app.route("/products/<id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get(id)

    name = request.json["name"]
    description = request.json["description"]
    is_cold = request.json["is_cold"]
    is_hot = request.json["is_hot"]
    img = request.json["img"]
    price = request.json["price"]
    in_stock = request.json["in_stock"]

    product.name = name
    product.description = description
    product.is_cold = is_cold
    product.is_hot = is_hot
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


if __name__ == "__main__":
    app.run(debug=True)
