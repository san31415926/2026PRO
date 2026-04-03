import datetime

from extensions import db


class Admin(db.Model):
    __tablename__ = 'sys_admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(255))


class SystemConfig(db.Model):
    __tablename__ = 'sys_config'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.String(200))
    desc = db.Column(db.String(200))


class SystemCoupon(db.Model):
    __tablename__ = 'sys_coupon'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    amount = db.Column(db.Numeric(10, 2))
    min_spend = db.Column(db.Numeric(10, 2))
    limit_level = db.Column(db.Integer, default=1)
    stock = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    price = db.Column(db.Numeric(10, 2))
    cover_img = db.Column(db.String(255))
    category = db.Column(db.String(200), default='其他')
    description = db.Column(db.String(1000))
    is_on_sale = db.Column(db.Boolean, default=True)
    stock = db.Column(db.Integer, default=999)
    is_seckill = db.Column(db.Boolean, default=False)
    seckill_price = db.Column(db.Numeric(10, 2), nullable=True)
    seckill_stock = db.Column(db.Integer, default=0)
    seckill_limit_per_user = db.Column(db.Integer, default=1)
    seckill_start_at = db.Column(db.DateTime, nullable=True)
    seckill_end_at = db.Column(db.DateTime, nullable=True)


class Banner(db.Model):
    __tablename__ = 'banner'
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(255))
    note = db.Column(db.String(100))


class Member(db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    nickname = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    avatar = db.Column(db.String(255), default='https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg')
    hero_text = db.Column(db.String(100), default='鸟为什么会飞')


class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    detail = db.Column(db.String(200))
    is_default = db.Column(db.Boolean, default=False)


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    num = db.Column(db.Integer, default=1)


class UserCoupon(db.Model):
    __tablename__ = 'user_coupon'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    sys_coupon_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    amount = db.Column(db.Numeric(10, 2))
    min_spend = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Integer, default=0)


class GroupTeam(db.Model):
    __tablename__ = 'group_team'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True)
    product_id = db.Column(db.Integer)
    initiator_id = db.Column(db.Integer)
    current_num = db.Column(db.Integer, default=1)
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(50))
    user_id = db.Column(db.Integer)
    product_title = db.Column(db.String(200))
    product_img = db.Column(db.String(255))
    total_amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Integer, default=1)
    address_snapshot = db.Column(db.String(500))
    category = db.Column(db.String(50), default='其他')
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    group_team_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.Integer, nullable=True)
    tracking_no = db.Column(db.String(50), nullable=True)
    shipped_at = db.Column(db.DateTime, nullable=True)
    is_seckill_order = db.Column(db.Boolean, default=False)


class Favorite(db.Model):
    __tablename__ = 'favorite'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    order_id = db.Column(db.Integer)
    content = db.Column(db.String(500))
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
