from flask import Blueprint, request, jsonify
from .models import Car
from . import db
from .auth import auth

cars_bp = Blueprint('cars_bp', __name__)

@cars_bp.route('/', methods=['GET'])
def list_cars():
    cars = Car.query.filter_by(available=True).all()
    return jsonify([
        {
            'id': car.id,
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'available': car.available
        }
        for car in cars
    ])

@cars_bp.route('/', methods=['POST'])
@auth.login_required
def add_car():
    user = auth.current_user()
    if not user.is_merchant():
        return jsonify({'error': 'Only merchants can add cars'}), 403

    data = request.get_json()
    car = Car(
        make=data['make'],
        model=data['model'],
        year=data['year'],
        available=True,
        merchant_id=user.id
    )
    db.session.add(car)
    db.session.commit()
    return jsonify({'message': 'Car added'}), 201

@cars_bp.route('/<int:car_id>', methods=['PUT'])
@auth.login_required
def update_car(car_id):
    user = auth.current_user()
    car = Car.query.get_or_404(car_id)

    if car.merchant_id != user.id:
        return jsonify({'error': 'You do not own this car'}), 403

    data = request.get_json()
    car.make = data.get('make', car.make)
    car.model = data.get('model', car.model)
    car.year = data.get('year', car.year)
    db.session.commit()
    return jsonify({'message': 'Car updated'})

@cars_bp.route('/<int:car_id>', methods=['DELETE'])
@auth.login_required
def delete_car(car_id):
    user = auth.current_user()
    car = Car.query.get_or_404(car_id)

    if car.merchant_id != user.id:
        return jsonify({'error': 'You do not own this car'}), 403

    db.session.delete(car)
    db.session.commit()
    return jsonify({'message': 'Car deleted'})
