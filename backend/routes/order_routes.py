import datetime
import random
import string
from datetime import timedelta

from flask import jsonify, request, session

from extensions import db
from models import Address, Cart, GroupTeam, Member, Order, Product, SystemConfig, UserCoupon
from utils.product_utils import (
    get_seckill_status,
    get_user_seckill_order_count,
    has_explicit_seckill_config,
    is_group_product,
    is_seckill_product,
    serialize_product,
)


def register_order_routes(app):
    def dedupe_group_orders_for_display(orders):
        deduped = []
        seen_group_keys = set()
        for order in orders:
            if order.group_team_id:
                key = (order.user_id, order.group_team_id, order.product_id or order.product_title)
                if key in seen_group_keys:
                    continue
                seen_group_keys.add(key)
            deduped.append(order)
        return deduped

    @app.route('/api/mobile/order', methods=['POST'])
    def create_order():
        user_id = session.get('user_id')
        data = request.json or {}
        product = Product.query.get(data.get('product_id'))
        user = Member.query.get(user_id)
        address = Address.query.get(data.get('address_id'))
        if not address:
            return jsonify({'code': 400, 'msg': '请选择地址'})
        if not product:
            return jsonify({'code': 404, 'msg': '商品不存在'})

        is_group_item = is_group_product(product)
        is_seckill_item = is_seckill_product(product)
        if not is_seckill_item and product.stock is not None and product.stock <= 0:
            return jsonify({'code': 400, 'msg': '该商品已售罄'})

        group_action = data.get('group_action')
        discount_cfg = SystemConfig.query.filter_by(key='group_buy_discount').first()
        group_discount = float(discount_cfg.value) if discount_cfg else 0.8

        if is_seckill_item:
            seckill_status = get_seckill_status(product)
            if seckill_status == 'upcoming':
                return jsonify({'code': 400, 'msg': '秒杀未开始'})
            if seckill_status == 'ended':
                return jsonify({'code': 400, 'msg': '秒杀已结束'})
            if seckill_status == 'sold_out':
                return jsonify({'code': 400, 'msg': '秒杀已售罄'})
            if data.get('coupon_id') or data.get('use_points'):
                return jsonify({'code': 400, 'msg': '秒杀商品不支持优惠券和积分抵扣'})
            limit = int(product.seckill_limit_per_user or 1)
            bought_count = get_user_seckill_order_count(user_id, product)
            if bought_count >= limit:
                return jsonify({'code': 400, 'msg': f'秒杀商品每人限购 {limit} 件'})
            base_amount = float(product.seckill_price if product.seckill_price is not None else product.price)
        elif is_group_item and group_action:
            base_amount = float(product.price) * group_discount
        else:
            member_discount = 0.9 if user.level == 2 else (0.8 if user.level == 3 else 1)
            base_amount = float(product.price) * member_discount

        coupon_deduct = 0
        if data.get('coupon_id'):
            user_coupon = UserCoupon.query.get(data.get('coupon_id'))
            if user_coupon and user_coupon.status == 0:
                coupon_deduct = float(user_coupon.amount)
                user_coupon.status = 1

        points_deduct = 0
        if data.get('use_points'):
            max_deduct = max(base_amount - coupon_deduct, 0)
            needed_points = int(max_deduct * 100)
            if user.points >= needed_points:
                points_deduct = max_deduct
                user.points -= needed_points
            else:
                points_deduct = user.points / 100.0
                user.points = 0

        final_amount = max(base_amount - coupon_deduct - points_deduct, 0)
        if user.balance < final_amount:
            return jsonify({'code': 400, 'msg': '余额不足'})
        user.balance = float(user.balance) - final_amount

        required_people_cfg = SystemConfig.query.filter_by(key='group_buy_people').first()
        required_people = int(required_people_cfg.value) if required_people_cfg and required_people_cfg.value else 2

        order_status = 1
        team_id = None
        team_completed = False
        if is_group_item and group_action:
            if group_action == 'create':
                existing_leader_order = (
                    db.session.query(Order, GroupTeam)
                    .join(GroupTeam, Order.group_team_id == GroupTeam.id)
                    .filter(
                        Order.user_id == user.id,
                        Order.product_id == product.id,
                        Order.status == 5,
                        GroupTeam.initiator_id == user.id,
                        GroupTeam.status == 0,
                    )
                    .order_by(Order.id.desc())
                    .first()
                )
                if existing_leader_order:
                    existing_order, existing_team = existing_leader_order
                    return jsonify({
                        'code': 200,
                        'msg': '鎴愬姛',
                        'balance': float(user.balance),
                        'points': user.points,
                        'order_id': existing_order.id,
                        'group_code': existing_team.code,
                    })

                group_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                new_team = GroupTeam(
                    code=group_code,
                    product_id=product.id,
                    initiator_id=user.id,
                    current_num=1,
                    status=0,
                )
                db.session.add(new_team)
                db.session.flush()
                team_id = new_team.id
                order_status = 5
            elif group_action == 'join':
                group_code = data.get('group_code')
                existing_join_order = (
                    db.session.query(Order, GroupTeam)
                    .join(GroupTeam, Order.group_team_id == GroupTeam.id)
                    .filter(
                        Order.user_id == user.id,
                        Order.product_id == product.id,
                        Order.status.in_([1, 2, 3, 4, 5]),
                        GroupTeam.code == group_code,
                    )
                    .order_by(Order.id.desc())
                    .first()
                )
                if existing_join_order:
                    existing_order, existing_team = existing_join_order
                    return jsonify({
                        'code': 200,
                        'msg': '鎴愬姛',
                        'balance': float(user.balance),
                        'points': user.points,
                        'order_id': existing_order.id,
                        'group_code': existing_team.code,
                    })

                team = GroupTeam.query.filter_by(code=group_code, status=0).first()
                if not team:
                    return jsonify({'code': 400, 'msg': '拼团码无效或已过期'})
                if team.product_id != product.id:
                    return jsonify({'code': 400, 'msg': '拼团码商品不匹配'})
                team.current_num += 1
                team_id = team.id
                if team.current_num >= required_people:
                    team.status = 1
                    team_completed = True
                    order_status = 1
                else:
                    order_status = 5

        if is_seckill_item:
            if has_explicit_seckill_config(product):
                product.seckill_stock = int(product.seckill_stock or 0) - 1
            elif product.stock is not None:
                product.stock -= 1
        elif product.stock is not None:
            product.stock -= 1

        order = Order(
            order_no=f"ORD{random.randint(1000, 9999)}",
            user_id=user.id,
            product_title=product.title,
            product_img=product.cover_img,
            total_amount=final_amount,
            status=order_status,
            address_snapshot=f"{address.name} {address.detail}",
            category=product.category,
            group_team_id=team_id,
            product_id=product.id,
            is_seckill_order=is_seckill_item,
        )
        db.session.add(order)
        db.session.flush()

        if is_group_item and group_action and team_completed and team_id:
            Order.query.filter_by(group_team_id=team_id, status=5).update({'status': 1})
        db.session.commit()

        result = {
            'code': 200,
            'msg': '成功',
            'balance': float(user.balance),
            'points': user.points,
            'order_id': order.id,
        }
        if is_group_item and group_action == 'create':
            team = GroupTeam.query.get(team_id)
            result['group_code'] = team.code
        return jsonify(result)

    @app.route('/api/mobile/cart/add', methods=['POST'])
    def add_cart():
        user_id = session.get('user_id')
        product = Product.query.get((request.json or {}).get('product_id'))
        if not product:
            return jsonify({'code': 404, 'msg': '商品不存在'})
        cart = Cart.query.filter_by(user_id=user_id, product_id=product.id).first()
        if is_seckill_product(product):
            status = get_seckill_status(product)
            if status == 'upcoming':
                return jsonify({'code': 400, 'msg': '秒杀未开始，暂时不能加入购物车'})
            if status == 'ended':
                return jsonify({'code': 400, 'msg': '秒杀已结束'})
            if status == 'sold_out':
                return jsonify({'code': 400, 'msg': '秒杀商品已售罄'})
            limit = int(product.seckill_limit_per_user or 1)
            current_num = cart.num if cart else 0
            if current_num >= limit:
                return jsonify({'code': 400, 'msg': f'秒杀商品每人限购 {limit} 件'})
        if cart:
            cart.num += 1
        else:
            db.session.add(Cart(user_id=user_id, product_id=product.id, num=1))
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/mobile/cart/list', methods=['GET'])
    def get_cart_list():
        rows = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id).filter(
            Cart.user_id == session.get('user_id')
        ).all()
        return jsonify({
            'code': 200,
            'data': [{**serialize_product(product), 'id': cart.id, 'product_id': product.id, 'num': cart.num} for cart, product in rows],
        })

    @app.route('/api/mobile/cart/update', methods=['POST'])
    def update_cart():
        cart = Cart.query.get(request.json['id'])
        count = request.json['num']
        if count <= 0:
            db.session.delete(cart)
        else:
            product = Product.query.get(cart.product_id)
            if product and is_seckill_product(product):
                status = get_seckill_status(product)
                limit = int(product.seckill_limit_per_user or 1)
                if status != 'active':
                    return jsonify({'code': 400, 'msg': '该秒杀商品当前不可调整数量'})
                if count > limit:
                    return jsonify({'code': 400, 'msg': f'秒杀商品每人限购 {limit} 件'})
            cart.num = count
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/mobile/cart/checkout', methods=['POST'])
    def cart_checkout():
        user_id = session.get('user_id')
        data = request.json or {}
        address = Address.query.get(data.get('address_id'))
        if not address:
            return jsonify({'code': 400, 'msg': '请选择地址'})

        user = Member.query.get(user_id)
        coupon_id = data.get('coupon_id')
        use_points = data.get('use_points')

        seckill_cart_rows = []
        for cart_id in data.get('cart_ids', []):
            cart = Cart.query.get(cart_id)
            if not cart:
                continue
            product = Product.query.get(cart.product_id)
            if product and is_seckill_product(product):
                seckill_cart_rows.append((cart, product))

        if seckill_cart_rows:
            if coupon_id:
                return jsonify({'code': 400, 'msg': '秒杀商品加入购物车后结算时不支持优惠券'})
            if use_points:
                return jsonify({'code': 400, 'msg': '秒杀商品加入购物车后结算时不支持积分抵扣'})

            total_amount = 0
            orders = []
            to_delete = []
            for cart, product in seckill_cart_rows:
                seckill_status = get_seckill_status(product)
                if seckill_status == 'upcoming':
                    return jsonify({'code': 400, 'msg': f'《{product.title}》秒杀未开始'})
                if seckill_status == 'ended':
                    return jsonify({'code': 400, 'msg': f'《{product.title}》秒杀已结束'})
                if seckill_status == 'sold_out':
                    return jsonify({'code': 400, 'msg': f'《{product.title}》已售罄'})
                limit = int(product.seckill_limit_per_user or 1)
                bought_count = get_user_seckill_order_count(user_id, product)
                if bought_count + cart.num > limit:
                    return jsonify({'code': 400, 'msg': f'《{product.title}》每人限购 {limit} 件'})
                amount = float(product.seckill_price if product.seckill_price is not None else product.price) * cart.num
                total_amount += amount
                if has_explicit_seckill_config(product):
                    product.seckill_stock = int(product.seckill_stock or 0) - cart.num
                elif product.stock is not None:
                    product.stock -= cart.num
                orders.append(Order(
                    order_no=f"CT{random.randint(1000, 9999)}",
                    user_id=user.id,
                    product_title=f"{product.title} x{cart.num}",
                    product_img=product.cover_img,
                    total_amount=amount,
                    status=1,
                    address_snapshot=f"{address.name} {address.detail}",
                    category=product.category,
                    product_id=product.id,
                    is_seckill_order=True,
                ))
                to_delete.append(cart)

            if user.balance < total_amount:
                return jsonify({'code': 400, 'msg': '余额不足'})
            user.balance = float(user.balance) - total_amount
            db.session.add_all(orders)
            for cart in to_delete:
                db.session.delete(cart)
            db.session.commit()
            return jsonify({'code': 200, 'msg': '成功', 'balance': float(user.balance), 'points': user.points})

        total_amount = 0
        items = []
        for cart_id in data.get('cart_ids', []):
            cart = Cart.query.get(cart_id)
            if not cart:
                continue
            product = Product.query.get(cart.product_id)
            if is_seckill_product(product):
                return jsonify({'code': 400, 'msg': f'《{product.title}》为秒杀商品，请直接购买'})
            if product.stock is not None and product.stock <= 0:
                return jsonify({'code': 400, 'msg': f'《{product.title}》已售罄，请移除后再结算'})
            discount = 0.9 if user.level == 2 else (0.8 if user.level == 3 else 1)
            amount = float(product.price) * cart.num * discount
            total_amount += amount
            items.append({'cart': cart, 'product': product, 'amount': amount})

        coupon_deduct = 0
        if coupon_id:
            user_coupon = UserCoupon.query.get(coupon_id)
            if user_coupon and user_coupon.status == 0:
                if total_amount >= float(user_coupon.min_spend):
                    coupon_deduct = float(user_coupon.amount)
                    user_coupon.status = 1
                else:
                    return jsonify({'code': 400, 'msg': '未满足优惠券使用门槛'})

        points_deduct = 0
        if use_points:
            max_deduct = max(total_amount - coupon_deduct, 0)
            needed_points = int(max_deduct * 100)
            if user.points >= needed_points:
                points_deduct = max_deduct
                user.points -= needed_points
            else:
                points_deduct = user.points / 100.0
                user.points = 0

        final_amount = max(total_amount - coupon_deduct - points_deduct, 0)
        if user.balance < final_amount:
            return jsonify({'code': 400, 'msg': '余额不足'})
        user.balance = float(user.balance) - final_amount

        orders = []
        to_delete = []
        for item in items:
            if item['product'].stock is not None:
                item['product'].stock -= item['cart'].num
            orders.append(Order(
                order_no=f"CT{random.randint(1000, 9999)}",
                user_id=user.id,
                product_title=f"{item['product'].title} x{item['cart'].num}",
                product_img=item['product'].cover_img,
                total_amount=item['amount'],
                status=1,
                address_snapshot=f"{address.name} {address.detail}",
                category=item['product'].category,
                product_id=item['product'].id,
            ))
            to_delete.append(item['cart'])

        db.session.add_all(orders)
        for cart in to_delete:
            db.session.delete(cart)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '成功', 'balance': float(user.balance), 'points': user.points})

    @app.route('/api/mobile/orders/<int:id>', methods=['GET'])
    def get_order_detail(id):
        order = Order.query.get(id)
        if order.status == 5 and order.group_team_id:
            team = GroupTeam.query.get(order.group_team_id)
            if team and team.status == 0 and datetime.datetime.now() > team.created_at + timedelta(minutes=10):
                team.status = 2
                order.status = 6
                db.session.commit()

        team_code = ''
        if order.group_team_id:
            team = GroupTeam.query.get(order.group_team_id)
            if team:
                team_code = team.code

        return jsonify({
            'code': 200,
            'data': {
                'no': order.order_no,
                'title': order.product_title,
                'img': order.product_img,
                'amount': float(order.total_amount),
                'status': order.status,
                'address': order.address_snapshot,
                'date': str(order.created_at),
                'group_code': team_code,
                'tracking_no': order.tracking_no,
            },
        })

    @app.route('/api/admin/orders', methods=['GET'])
    def admin_get_orders():
        rows = db.session.query(Order, Member).join(Member, Order.user_id == Member.id).order_by(Order.id.desc()).all()
        deduped_rows = []
        seen_group_keys = set()
        for order, member in rows:
            if order.group_team_id:
                key = (order.user_id, order.group_team_id, order.product_id or order.product_title)
                if key in seen_group_keys:
                    continue
                seen_group_keys.add(key)
            deduped_rows.append((order, member))
        return jsonify({
            'code': 200,
            'data': [
                {
                    'id': order.id,
                    'no': order.order_no,
                    'user': member.nickname,
                    'title': order.product_title,
                    'img': order.product_img,
                    'amount': float(order.total_amount),
                    'status': order.status,
                    'date': str(order.created_at),
                    'tracking_no': order.tracking_no or '',
                }
                for order, member in deduped_rows
            ],
        })

    @app.route('/api/admin/orders/<int:id>/ship', methods=['POST'])
    def ship_order(id):
        order = Order.query.get(id)
        if not order:
            return jsonify({'code': 404, 'msg': '订单不存在'})
        if order.status != 1:
            return jsonify({'code': 400, 'msg': '当前订单状态不可发货'})
        data = request.json or {}
        tracking_no = (data.get('tracking_no') or '').strip()
        if not tracking_no:
            return jsonify({'code': 400, 'msg': '请填写快递单号'})
        order.status = 2
        order.tracking_no = tracking_no
        order.shipped_at = datetime.datetime.now()
        db.session.commit()
        return jsonify({'code': 200, 'tracking_no': order.tracking_no})

    @app.route('/api/mobile/orders/<int:id>/cancel', methods=['POST'])
    def cancel_order(id):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        order = Order.query.get(id)
        if not order or order.user_id != user_id:
            return jsonify({'code': 400, 'msg': '订单不存在'})
        if order.status != 1:
            return jsonify({'code': 400, 'msg': '该订单无法取消'})
        user = Member.query.get(user_id)
        user.balance = float(user.balance) + float(order.total_amount)
        if order.product_id:
            product = Product.query.get(order.product_id)
            if product:
                if order.is_seckill_order:
                    product.seckill_stock = int(product.seckill_stock or 0) + 1
                elif product.stock is not None:
                    product.stock += 1
        order.status = 0
        db.session.commit()
        return jsonify({'code': 200, 'msg': '已取消', 'balance': float(user.balance)})

    @app.route('/api/mobile/my_orders', methods=['GET'])
    def my_orders():
        orders = Order.query.filter_by(user_id=session.get('user_id')).order_by(Order.id.desc()).all()
        orders = dedupe_group_orders_for_display(orders)
        return jsonify({
            'code': 200,
            'data': [
                {
                    'id': order.id,
                    'no': order.order_no,
                    'title': order.product_title,
                    'img': order.product_img,
                    'amount': float(order.total_amount),
                    'status': order.status,
                }
                for order in orders
            ],
        })

    @app.route('/api/mobile/orders/<int:id>/confirm', methods=['POST'])
    def confirm_receipt(id):
        order = Order.query.get(id)
        order.status = 3
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/mobile/orders/<int:id>/logistics', methods=['GET'])
    def get_order_logistics(id):
        order = Order.query.get(id)
        if not order:
            return jsonify({'code': 404})
        traces = []
        base_time = order.created_at or datetime.datetime.now()
        tracking_no = order.tracking_no or '待分配'

        def build_trace(time_point, desc):
            return {'time': time_point.strftime('%Y-%m-%d %H:%M:%S'), 'desc': desc}

        traces.append(build_trace(base_time, f'订单已提交，系统正在处理。订单号：{order.order_no}'))
        traces.append(build_trace(base_time + timedelta(minutes=8), '支付成功，订单进入商家备货队列'))
        traces.append(build_trace(base_time + timedelta(minutes=25), '仓库已接单，正在进行商品分拣'))
        if order.status >= 2:
            ship_time = order.shipped_at or (base_time + timedelta(hours=2))
            traces.append(build_trace(ship_time - timedelta(minutes=20), '商品复核完成，包裹已完成出库扫描'))
            traces.append(build_trace(ship_time, f'商家已发货，快递单号：{tracking_no}'))
            traces.append(build_trace(ship_time + timedelta(minutes=40), f'快件已由仓库揽收，运输单号：{tracking_no}'))
            traces.append(build_trace(ship_time + timedelta(hours=6), '快件运输中，已发往目的地分拨中心'))
            traces.append(build_trace(ship_time + timedelta(hours=12), '包裹已到达区域分拨中心，正在安排转运'))
        if order.status >= 3:
            receive_time = (order.shipped_at or base_time) + timedelta(days=1)
            traces.append(build_trace(receive_time - timedelta(hours=6), '包裹已到达派送站点，等待快递员出仓'))
            traces.append(build_trace(receive_time - timedelta(hours=3), '快递员正在派送，请保持电话畅通'))
            traces.append(build_trace(receive_time, '订单已签收，感谢您使用 Smart Mall'))
        return jsonify({'code': 200, 'data': sorted(traces, key=lambda item: item['time'], reverse=True)})
