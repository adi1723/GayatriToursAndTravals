from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

db = SQLAlchemy(app)

# --- Models ---
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    available = db.Column(db.Boolean, default=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in hours
    client = db.relationship('Client', backref='bookings')
    vehicle = db.relationship('Vehicle', backref='bookings')

# --- Utility / Decorators ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('Please login as admin to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def home():
    return redirect(url_for('client_home'))

@app.route('/client/home')
def client_home():
    client = None
    client_name = None

    if 'client_email' in session:
        client = Client.query.filter_by(email=session['client_email']).first()
        if client:
            client_name = client.first_name
    elif 'user' in session and session['user'] == 'Guest':
        client_name = 'Guest'

    vehicles = Vehicle.query.filter_by(available=True).all()

    return render_template('client/client_home.html',
                           client=client,
                           client_name=client_name,
                           vehicles=vehicles,
                           images={
                               "aura": url_for('static', filename='images/aura.png'),
                               "aura_contact": url_for('static', filename='images/aura_contact.png'),
                               "img1": url_for('static', filename='images/img1.png'),
                               "img2": url_for('static', filename='images/img2.png'),
                               "img3": url_for('static', filename='images/img3.png'),
                               "img4": url_for('static', filename='images/img4.png'),
                               "img5": url_for('static', filename='images/img5.png'),
                            "Aura_video": url_for('static', filename='images/Aura_video.mp4')  # Replace with your video URL or static path

                           })

# ----------------------- CLIENT ROUTES -----------------------

@app.route('/client/register', methods=['GET', 'POST'])
def client_register():
    if request.method == 'POST':
        data = request.form
        if data['password'] != data['confirm_password']:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('client_register'))

        hashed_password = generate_password_hash(data['password'])

        new_client = Client(
            first_name=data['first_name'],
            middle_name=data.get('middle_name', ''),
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            address_line1=data['address'],
            city=data['city'],
            state=data['state'],
            pincode=data['pincode'],
            password=hashed_password
        )
        db.session.add(new_client)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('client_login'))

    return render_template('client/client_register.html')

@app.route('/client/login', methods=['GET', 'POST'])
def client_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        client = Client.query.filter_by(email=email).first()

        if client and check_password_hash(client.password, password):
            session['client_email'] = email
            session['client_id'] = client.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('client_home'))
        flash('Invalid credentials. Please try again.', 'danger')

    return render_template('client/client_login.html')

@app.route('/guest/login', methods=['POST'])
def guest_login():
    session['user'] = 'Guest'
    flash('Logged in as Guest', 'info')
    return redirect(url_for('client_home'))

@app.route('/client/about')
def client_about():
    client_name = None
    if 'client_email' in session:
        client = Client.query.filter_by(email=session['client_email']).first()
        if client:
            client_name = client.first_name
    return render_template('client/client_about.html', client_name=client_name)

@app.route('/client/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        try:
            distance = float(request.form['distance'])
            car_type = request.form['car_type']

            if car_type not in ['CNG', 'Petrol', 'Diesel']:
                flash('Invalid car type selected.', 'danger')
                return redirect(url_for('client_home'))

            rate_per_km = 22 if car_type == 'CNG' else 25
            final_price = distance * rate_per_km

            return render_template('client/services.html', 
                                   final_price=final_price, 
                                   distance=distance, 
                                   car_type=car_type)
        except ValueError:
            flash('Please enter a valid distance.', 'danger')
            return redirect(url_for('client_home'))

    # Show calculation form if GET
    return render_template('client/services.html')

@app.route('/client/packages')
def client_packages():
    client_name = None
    if 'client_email' in session:
        client = Client.query.filter_by(email=session['client_email']).first()
        if client:
            client_name = client.first_name
    return render_template('client/client_packages.html', client_name=client_name)


@app.route('/client/vehicles')
def client_view_vehicles():
    vehicles = Vehicle.query.filter_by(available=True).all()
    return render_template('client/client_vehicle_view.html', vehicles=vehicles)

@app.route('/client/book/<int:vehicle_id>', methods=['GET', 'POST'])
def book_vehicle(vehicle_id):
    if 'client_id' not in session:
        flash("Please login to book a vehicle.", "warning")
        return redirect(url_for('client_login'))

    vehicle = Vehicle.query.get_or_404(vehicle_id)

    if request.method == 'POST':
        booking_date = request.form['booking_date']
        booking_time = request.form['booking_time']
        duration = int(request.form['duration'])

        booking = Booking(
            client_id=session.get('client_id'),
            vehicle_id=vehicle_id,
            booking_date=booking_date,
            booking_time=booking_time,
            duration=duration
        )
        db.session.add(booking)
        db.session.commit()
        flash('Your booking has been confirmed.', 'success')
        return redirect(url_for('booking_confirmation', booking_id=booking.id))

    return render_template('client/client_booking.html', vehicle=vehicle)

@app.route('/client/booking/confirmation/<int:booking_id>')
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    vehicle = Vehicle.query.get_or_404(booking.vehicle_id)
    client = Client.query.get_or_404(booking.client_id)
    return render_template('client/confirm_booking.html', booking=booking, vehicle=vehicle, client=client)

# ----------------------- ADMIN ROUTES -----------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            flash('Admin logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')

    return render_template('admin/admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

@app.route('/admin/clients')
@admin_required
def admin_clients():
    clients = Client.query.all()
    return render_template('admin/admin_clients.html', clients=clients)

@app.route('/admin/vehicles')
@admin_required
def admin_vehicles():
    vehicles = Vehicle.query.all()
    return render_template('admin/admin_vehicles.html', vehicles=vehicles)

@app.route('/admin/bookings')
@admin_required
def booking_management():
    bookings = Booking.query.all()
    return render_template('admin/booking_management.html', bookings=bookings)

@app.route('/admin/vehicles/add', methods=['GET', 'POST'])
@admin_required
def add_vehicle():
    if request.method == 'POST':
        data = request.form
        image = request.files.get('image')
        image_url = 'static/images/default.png'

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = image_path

        new_vehicle = Vehicle(
            make=data['make'],
            model=data['model'],
            year=int(data['year']),
            description=data['description'],
            rate=float(data['rate']),
            image_url=image_url,
            available=True
        )
        db.session.add(new_vehicle)
        db.session.commit()
        flash('Vehicle added successfully.', 'success')
        return redirect(url_for('admin_vehicles'))

    return render_template('admin/add_vehicle.html')

# ----------------------- COMMON -----------------------

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

# Initialize DB
with app.app_context():
    db.create_all()

# Run App
if __name__ == '__main__':
    app.run(debug=True)
