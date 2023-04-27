from flask import jsonify
from flask_restful import abort, Resource

from data import db_session
from data.parser import parser
from data.shoes import Shoe


# Функция аборта с проверкой кроссовка
def abort_if_shoe_not_found(shoe_id):
    session = db_session.create_session()
    news = session.query(Shoe).get(shoe_id)
    if not news:
        abort(404, message=f"Shoe {shoe_id} not found")


class ShoeResource(Resource):
    def get(self, shoe_id):  # получения одного кроссовка по id
        abort_if_shoe_not_found(shoe_id)
        session = db_session.create_session()
        shoe = session.query(Shoe).get(shoe_id)
        return jsonify({'shoe': shoe.to_dict(
            only=('id', 'name', 'category', 'price'))})

    def delete(self, shoe_id):  # удаление кроссовка по id
        abort_if_shoe_not_found(shoe_id)
        session = db_session.create_session()
        shoe = session.query(Shoe).get(shoe_id)
        session.delete(shoe)
        session.commit()
        return jsonify({'success': 'OK'})


class ShoesListResource(Resource):
    def get(self):  # получения всех кроссовок с бд
        session = db_session.create_session()
        shoes = session.query(Shoe).all()
        return jsonify({'shoes': [item.to_dict(
            only=('id', 'name', 'category', 'price')) for item in shoes]})

    def post(self):  # добавление кроссовка в бд
        args = parser.parse_args()
        print(args, 11)
        session = db_session.create_session()
        shoe = Shoe(
            name=args['name'],
            category=args['category'],
            price=args['price']
        )
        print(shoe.price)
        session.add(shoe)
        session.commit()
        return jsonify({'success': 'OK'})
