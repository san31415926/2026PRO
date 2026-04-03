from flask import jsonify, request, session

from extensions import db
from models import Address, Comment, Favorite, Order, Product
from utils.product_utils import serialize_product


def register_member_routes(app):
    @app.route('/api/mobile/address', methods=['GET', 'POST'])
    def handle_address():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        if request.method == 'GET':
            addresses = Address.query.filter_by(user_id=user_id).order_by(Address.id.asc()).all()
            if addresses and not any(address.is_default for address in addresses):
                addresses[0].is_default = True
                db.session.commit()
            return jsonify({
                'code': 200,
                'data': [
                    {
                        'id': address.id,
                        'name': address.name,
                        'phone': address.phone,
                        'detail': address.detail,
                        'is_default': bool(address.is_default),
                    }
                    for address in sorted(addresses, key=lambda item: (not bool(item.is_default), item.id))
                ],
            })

        is_default = bool(request.json.get('is_default'))
        user_addresses = Address.query.filter_by(user_id=user_id).all()
        if not user_addresses:
            is_default = True
        if is_default:
            for address in user_addresses:
                address.is_default = False
        db.session.add(Address(
            user_id=user_id,
            name=request.json['name'],
            phone=request.json['phone'],
            detail=request.json['detail'],
            is_default=is_default,
        ))
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/mobile/address/<int:addr_id>/default', methods=['POST'])
    def set_default_address(addr_id):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        address = Address.query.filter_by(id=addr_id, user_id=user_id).first()
        if not address:
            return jsonify({'code': 404, 'msg': '地址不存在'})
        user_addresses = Address.query.filter_by(user_id=user_id).all()
        for item in user_addresses:
            item.is_default = item.id == address.id
        db.session.commit()
        return jsonify({'code': 200, 'msg': '设置成功'})

    @app.route('/api/mobile/favorite/toggle', methods=['POST'])
    def toggle_favorite():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        product_id = request.json.get('product_id')
        favorite = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
        if favorite:
            db.session.delete(favorite)
            action = 'remove'
            message = '已取消收藏'
        else:
            db.session.add(Favorite(user_id=user_id, product_id=product_id))
            action = 'add'
            message = '已收藏'
        db.session.commit()
        return jsonify({'code': 200, 'msg': message, 'action': action})

    @app.route('/api/mobile/favorites', methods=['GET'])
    def get_favorites():
        result = db.session.query(Favorite, Product).join(Product, Favorite.product_id == Product.id).filter(
            Favorite.user_id == session.get('user_id'),
        ).all()
        return jsonify({'code': 200, 'data': [serialize_product(product) for _, product in result]})

    @app.route('/api/mobile/comments/add', methods=['POST'])
    def add_comment():
        data = request.json
        db.session.add(Comment(
            user_id=session.get('user_id'),
            order_id=data['order_id'],
            content=data['content'],
            rating=data['rating'],
        ))
        order = Order.query.get(data['order_id'])
        order.status = 4
        db.session.commit()
        return jsonify({'code': 200})
