from flask import Blueprint, request, jsonify
from .models import db, Rental, Car
from .auth import auth
from datetime import datetime

rentals_bp = Blueprint('rentals', __name__, url_prefix='/rentals')

@rentals_bp.route('/rent', methods=['POST'])
@auth.login_required
def rent_car():
    data = request.get_json()
    car_id = data.get('car_id')

    car = Car.query.get(car_id)
    if not car:
        return jsonify({'error': 'Car not found'}), 404
    if car.is_available is False:
        return jsonify({'error': 'Car is already rented'}), 400

    rental = Rental(user_id=auth.current_user().id, car_id=car_id, start_date=datetime.utcnow())
    car.is_available = False

    db.session.add(rental)
    db.session.commit()

    return jsonify({'message': 'Car rented successfully'}), 200

@rentals_bp.route('/return/<int:rental_id>', methods=['POST'])
@auth.login_required
def return_car(rental_id):
    rental = Rental.query.get(rental_id)
    if not rental or rental.user_id != auth.current_user().id:
        return jsonify({'error': 'Rental not found'}), 404

    if rental.end_date is not None:
        return jsonify({'error': 'Car already returned'}), 400

    rental.end_date = datetime.utcnow()
    rental.car.is_available = True
    db.session.commit()

    return jsonify({'message': 'Car returned successfully'}), 200

@rentals_bp.route('/my', methods=['GET'])
@auth.login_required
def my_rentals():
    rentals = Rental.query.filter_by(user_id=auth.current_user().id).all()
    return jsonify([
        {
            'rental_id': r.id,
            'car_id': r.car_id,
            'start_date': r.start_date.isoformat(),
            'end_date': r.end_date.isoformat() if r.end_date else None
        } for r in rentals
    ])
