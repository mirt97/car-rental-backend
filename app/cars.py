from flask import Blueprint, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from app.models import db, User, Car
from sqlalchemy.exc import IntegrityError

cars_bp = Blueprint('cars', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

# Araç ekleme (sadece merchant rolü)
@cars_bp.route('/cars', methods=['POST'])
@auth.login_required
def add_car():
    current_user = auth.current_user()
    if current_user.role != 'merchant':
        return jsonify({'error': 'Sadece merchant kullanıcılar araç ekleyebilir'}), 403

    data = request.get_json()
    required_fields = ['brand', 'model', 'year']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Eksik alanlar var'}), 400

    try:
        new_car = Car(
            brand=data['brand'],
            model=data['model'],
            year=int(data['year']),
            available=True
        )
        db.session.add(new_car)
        db.session.commit()
        return jsonify({'message': 'Araç başarıyla eklendi'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Veritabanı hatası'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Araç listeleme (herkes erişebilir)
@cars_bp.route('/cars', methods=['GET'])
def list_cars():
    cars = Car.query.all()
    result = []
    for car in cars:
        result.append({
            'id': car.id,
            'brand': car.brand,
            'model': car.model,
            'year': car.year,
            'available': car.available
        })
    return jsonify(result), 200
