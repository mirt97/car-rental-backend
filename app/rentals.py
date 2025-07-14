from flask import Blueprint, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from app.models import db, User, Car, Rental
from datetime import datetime
from sqlalchemy.exc import IntegrityError

rentals_bp = Blueprint('rentals', __name__)
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None

@rentals_bp.route('/rent', methods=['POST'])
@auth.login_required
def rent_car():
    current_user = auth.current_user()
    if current_user.role != 'user':
        return jsonify({'error': 'Sadece user rolündeki kullanıcılar araç kiralayabilir'}), 403

    data = request.get_json()
    required_fields = ['car_id', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Eksik alanlar var'}), 400

    try:
        car = Car.query.get(data['car_id'])
        if not car or not car.available:
            return jsonify({'error': 'Araç mevcut değil veya kiralanamaz durumda'}), 400

        # Tarihleri doğrula
        start_date = datetime.strptime(data['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(data['end_date'], "%Y-%m-%d").date()
        if start_date >= end_date:
            return jsonify({'error': 'Başlangıç tarihi, bitiş tarihinden önce olmalı'}), 400

        rental = Rental(
            user_id=current_user.id,
            car_id=car.id,
            start_date=start_date,
            end_date=end_date
        )

        car.available = False
        db.session.add(rental)
        db.session.commit()

        return jsonify({'message': 'Araç başarıyla kiralandı'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Veritabanı hatası'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
