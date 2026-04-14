from flask import jsonify, request

from extensions import db
from models import Banner, Comment, Member, Order, Product
from utils.product_utils import parse_dt, serialize_product


def register_product_routes(app):
    @app.route('/api/products', methods=['GET', 'POST'])
    def handle_products():
        if request.method == 'GET':
            products = Product.query.order_by(Product.id.desc()).all()
            return jsonify({'code': 200, 'data': [serialize_product(product) for product in products]})
        try:
            data = request.json
            new_product = Product(
                title=data.get('title', '未命名商品'),
                price=float(data.get('price', 0)),
                cover_img=data.get('img', ''),
                category=data.get('category', '其他'),
                description=data.get('description', ''),
                is_on_sale=True,
                stock=int(data.get('stock', 999)),
                is_seckill=bool(data.get('is_seckill')),
                seckill_price=float(data.get('seckill_price')) if data.get('seckill_price') not in (None, '') else None,
                seckill_stock=int(data.get('seckill_stock', 0) or 0),
                seckill_limit_per_user=int(data.get('seckill_limit_per_user', 1) or 1),
                seckill_start_at=parse_dt(data.get('seckill_start_at')),
                seckill_end_at=parse_dt(data.get('seckill_end_at')),
            )
            db.session.add(new_product)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '发布成功'})
        except Exception:
            return jsonify({'code': 500, 'msg': '发布失败'})

    @app.route('/api/products/<int:id>', methods=['PUT', 'DELETE'])
    def modify_product(id):
        product = Product.query.get(id)
        if request.method == 'PUT':
            data = request.json
            product.title = data.get('title')
            product.price = data.get('price')
            product.cover_img = data.get('img')
            product.category = data.get('category')
            product.description = data.get('description')
            if data.get('stock') is not None:
                product.stock = int(data.get('stock'))
            product.is_seckill = bool(data.get('is_seckill'))
            product.seckill_price = float(data.get('seckill_price')) if data.get('seckill_price') not in (None, '') else None
            product.seckill_stock = int(data.get('seckill_stock', 0) or 0)
            product.seckill_limit_per_user = int(data.get('seckill_limit_per_user', 1) or 1)
            product.seckill_start_at = parse_dt(data.get('seckill_start_at'))
            product.seckill_end_at = parse_dt(data.get('seckill_end_at'))
            db.session.commit()
            return jsonify({'code': 200})
        db.session.delete(product)
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/products/<int:id>/status', methods=['POST'])
    def toggle_status(id):
        product = Product.query.get(id)
        product.is_on_sale = not product.is_on_sale
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/products/<int:id>/comments', methods=['GET'])
    def get_product_comments(id):
        rows = db.session.query(Comment, Member, Order).join(
            Order, Comment.order_id == Order.id,
        ).join(
            Member, Comment.user_id == Member.id,
        ).filter(
            Order.product_id == id,
        ).order_by(Comment.id.desc()).all()
        data = [
            {
                'id': comment.id,
                'user': member.nickname,
                'avatar': member.avatar,
                'rating': comment.rating,
                'content': comment.content,
                'date': comment.created_at.strftime('%Y-%m-%d'),
            }
            for comment, member, _ in rows
        ]
        return jsonify({'code': 200, 'data': data})

    @app.route('/api/banners', methods=['GET', 'POST'])
    def handle_banners():
        if request.method == 'GET':
            banners = Banner.query.all()
            return jsonify({'code': 200, 'data': [{'id': banner.id, 'img': banner.img, 'note': banner.note} for banner in banners]})
        data = request.json
        db.session.add(Banner(img=data['img'], note=data.get('note', '')))
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/banners/<int:id>', methods=['DELETE'])
    def delete_banner(id):
        banner = Banner.query.get(id)
        db.session.delete(banner)
        db.session.commit()
        return jsonify({'code': 200})
