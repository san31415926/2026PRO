import datetime

from flask import jsonify, request
from sqlalchemy import func

from extensions import db
from models import Comment, Member, Order, Product


def register_admin_routes(app):
    @app.route('/api/admin/members', methods=['GET'])
    def admin_get_members():
        members = Member.query.order_by(Member.id.desc()).all()
        return jsonify({
            'code': 200,
            'data': [
                {
                    'id': member.id,
                    'username': member.username,
                    'nickname': member.nickname,
                    'level': member.level,
                    'balance': float(member.balance),
                    'points': member.points,
                    'avatar': member.avatar,
                }
                for member in members
            ],
        })

    @app.route('/api/admin/member/recharge', methods=['POST'])
    def admin_recharge_member():
        data = request.json or {}
        member = Member.query.get(data.get('user_id'))
        if not member:
            return jsonify({'code': 400, 'msg': '用户不存在'})
        member.balance = float(member.balance) + float(data.get('amount', 0))
        db.session.commit()
        return jsonify({'code': 200, 'msg': '充值成功', 'balance': float(member.balance)})

    @app.route('/api/admin/comments', methods=['GET'])
    def get_comments():
        rows = (
            db.session.query(Comment, Member, Order)
            .join(Member, Comment.user_id == Member.id)
            .join(Order, Comment.order_id == Order.id)
            .order_by(Comment.id.desc())
            .all()
        )
        return jsonify({
            'code': 200,
            'data': [
                {
                    'id': comment.id,
                    'user': member.nickname,
                    'product': order.product_title,
                    'content': comment.content,
                    'rating': comment.rating,
                    'date': str(comment.created_at),
                }
                for comment, member, order in rows
            ],
        })

    @app.route('/api/admin/comments/<int:id>', methods=['DELETE'])
    def delete_comment(id):
        comment = Comment.query.get(id)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'code': 200})

    @app.route('/api/admin/stats', methods=['GET'])
    def get_stats():
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        total_sales = float(db.session.query(func.sum(Order.total_amount)).scalar() or 0)
        total_orders = Order.query.count()
        total_products = Product.query.filter_by(is_on_sale=True).count()
        total_members = Member.query.count()

        today_sales = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == today).scalar() or 0)
        yest_sales = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == yesterday).scalar() or 0)
        today_orders = Order.query.filter(func.date(Order.created_at) == today).count()
        yest_orders = Order.query.filter(func.date(Order.created_at) == yesterday).count()

        trend_sales = []
        trend_orders = []
        trend_dates = []
        for i in range(6, -1, -1):
            day = today - datetime.timedelta(days=i)
            sales = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == day).scalar() or 0)
            orders = Order.query.filter(func.date(Order.created_at) == day).count()
            trend_sales.append(round(sales, 2))
            trend_orders.append(orders)
            trend_dates.append(f'{day.month}/{day.day}')

        category_rows = (
            db.session.query(Order.category, func.sum(Order.total_amount), func.count(Order.id))
            .group_by(Order.category)
            .order_by(func.sum(Order.total_amount).desc())
            .limit(8)
            .all()
        )
        category_data = [
            {'name': category or '其他', 'sales': round(float(amount), 2), 'orders': int(count)}
            for category, amount, count in category_rows
            if category
        ]

        status_map = {0: '已取消', 1: '待发货', 2: '运输中', 3: '待评价', 4: '已完成', 5: '拼团中'}
        status_rows = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
        status_data = [{'name': status_map.get(status, f'状态{status}'), 'value': int(count)} for status, count in status_rows]
        pending_ship = Order.query.filter_by(status=1).count()

        low_stock_rows = (
            Product.query.filter(Product.stock < 10, Product.is_on_sale == True)
            .order_by(Product.stock.asc())
            .limit(5)
            .all()
        )
        low_stock = [{'id': product.id, 'title': product.title, 'stock': product.stock, 'img': product.cover_img} for product in low_stock_rows]

        hot_rows = (
            db.session.query(
                Order.product_title,
                Order.product_img,
                func.count(Order.id).label('count'),
                func.sum(Order.total_amount).label('amount'),
            )
            .group_by(Order.product_title, Order.product_img)
            .order_by(func.count(Order.id).desc())
            .limit(5)
            .all()
        )
        hot_data = [
            {'title': title, 'img': img, 'count': int(count), 'amount': round(float(amount), 2)}
            for title, img, count, amount in hot_rows
        ]

        level_rows = db.session.query(Member.level, func.count(Member.id)).group_by(Member.level).all()
        level_data = [
            {'name': ['', '普通会员', '黄金VIP', '钻石VIP'][level] if level <= 3 else f'等级{level}', 'value': int(count)}
            for level, count in level_rows
        ]
        avg_rating = float(db.session.query(func.avg(Comment.rating)).scalar() or 0)

        def pct(current, previous):
            if previous == 0:
                return None
            return round((current - previous) / previous * 100, 1)

        return jsonify({
            'code': 200,
            'data': {
                'total_sales': total_sales,
                'total_orders': total_orders,
                'total_products': total_products,
                'total_members': total_members,
                'today_sales': today_sales,
                'yest_sales': yest_sales,
                'today_orders': today_orders,
                'yest_orders': yest_orders,
                'sales_pct': pct(today_sales, yest_sales),
                'orders_pct': pct(today_orders, yest_orders),
                'aov': round(total_sales / total_orders, 2) if total_orders else 0,
                'pending_ship': pending_ship,
                'avg_rating': round(avg_rating, 1),
                'trend_dates': trend_dates,
                'trend_sales': trend_sales,
                'trend_orders': trend_orders,
                'category_data': category_data,
                'status_data': status_data,
                'hot_data': hot_data,
                'low_stock': low_stock,
                'level_data': level_data,
                'chart': [{'name': category or '其他', 'value': round(float(amount), 2)} for category, amount, _ in category_rows if category],
            },
        })
