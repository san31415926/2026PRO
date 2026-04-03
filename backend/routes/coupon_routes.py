from flask import jsonify, request, session

from extensions import db
from models import Member, SystemCoupon, UserCoupon


def register_coupon_routes(app):
    @app.route('/api/admin/coupons', methods=['GET'])
    def admin_get_coupons():
        coupons = SystemCoupon.query.all()
        return jsonify({
            'code': 200,
            'data': [
                {
                    'id': coupon.id,
                    'name': coupon.name,
                    'amount': float(coupon.amount),
                    'min_spend': float(coupon.min_spend),
                    'limit_level': coupon.limit_level,
                    'stock': coupon.stock,
                }
                for coupon in coupons
            ],
        })

    @app.route('/api/admin/coupons', methods=['POST'])
    def admin_add_coupon():
        data = request.json
        new_coupon = SystemCoupon(
            name=data['name'],
            amount=float(data['amount']),
            min_spend=float(data['min_spend']),
            limit_level=int(data.get('limit_level', 1)),
            stock=int(data.get('stock', 100)),
        )
        db.session.add(new_coupon)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '添加成功'})

    @app.route('/api/admin/coupons/<int:id>', methods=['PUT'])
    def admin_update_coupon(id):
        coupon = SystemCoupon.query.get(id)
        data = request.json
        coupon.name = data['name']
        coupon.amount = float(data['amount'])
        coupon.min_spend = float(data['min_spend'])
        coupon.limit_level = int(data['limit_level'])
        coupon.stock = int(data['stock'])
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/admin/coupons/<int:id>', methods=['DELETE'])
    def admin_delete_coupon(id):
        coupon = SystemCoupon.query.get(id)
        db.session.delete(coupon)
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/mobile/coupon/market', methods=['GET'])
    def get_coupon_market():
        coupons = SystemCoupon.query.filter(SystemCoupon.stock > 0).all()
        return jsonify({
            'code': 200,
            'data': [
                {
                    'id': coupon.id,
                    'name': coupon.name,
                    'amount': float(coupon.amount),
                    'min_spend': float(coupon.min_spend),
                    'limit_level': coupon.limit_level,
                    'desc': (f'满{float(coupon.min_spend)}可用' if coupon.min_spend > 0 else '无门槛'),
                }
                for coupon in coupons
            ],
        })

    @app.route('/api/mobile/coupon/get', methods=['POST'])
    def get_coupon():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        coupon_id = request.json.get('id')
        system_coupon = SystemCoupon.query.get(coupon_id)
        if not system_coupon:
            return jsonify({'code': 400, 'msg': '优惠券不存在'})
        if system_coupon.stock <= 0:
            return jsonify({'code': 400, 'msg': '手慢了，已抢光'})
        user = Member.query.get(user_id)
        if user.level < system_coupon.limit_level:
            level_names = {1: '普通会员', 2: '黄金VIP', 3: '钻石VIP'}
            return jsonify({'code': 400, 'msg': f'仅限 {level_names.get(system_coupon.limit_level)} 领取'})
        if UserCoupon.query.filter_by(user_id=user_id, sys_coupon_id=system_coupon.id).first():
            return jsonify({'code': 400, 'msg': '您已领取过该券'})
        system_coupon.stock -= 1
        db.session.add(UserCoupon(
            user_id=user_id,
            sys_coupon_id=system_coupon.id,
            name=system_coupon.name,
            amount=system_coupon.amount,
            min_spend=system_coupon.min_spend,
            status=0,
        ))
        db.session.commit()
        return jsonify({'code': 200, 'msg': '领取成功'})

    @app.route('/api/mobile/coupon/my', methods=['GET'])
    def my_coupons():
        coupons = UserCoupon.query.filter_by(user_id=session.get('user_id'), status=0).all()
        return jsonify({
            'code': 200,
            'data': [
                {
                    'id': coupon.id,
                    'name': coupon.name,
                    'amount': float(coupon.amount),
                    'min_spend': float(coupon.min_spend),
                }
                for coupon in coupons
            ],
        })
