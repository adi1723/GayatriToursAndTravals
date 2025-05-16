# create_db.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite URI for your database
db = SQLAlchemy(app)

# Define the Client model
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))  # Optional
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Later we can store hashed passwords
    created_at = db.Column(db.DateTime, server_default=db.func.now())  # Auto time stamp

# Drop the existing tables and recreate them based on the model
with app.app_context():
    db.drop_all()  # Drop all existing tables
    db.create_all()  # Create new tables

print("Database recreated successfully.")
