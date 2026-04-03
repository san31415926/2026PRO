import os
import random
import string
import io
import datetime
import uuid
from datetime import timedelta
from flask import Flask, jsonify, request, session, send_file, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, inspect, text, or_, and_
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- 1. 鍒濆鍖栭厤缃?---
app = Flask(__name__)
app.secret_key = 'panweiyu_secret_key'

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'mysql+pymysql://root:panweiyu123@localhost/smart_mall'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 图片上传文件夹配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

db = SQLAlchemy(app)


def parse_dt(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value
    value = str(value).strip()
    if not value:
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M:%S'):
        try:
            return datetime.datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def format_dt(value):
    if not value:
        return None
    return value.strftime('%Y-%m-%d %H:%M:%S')


def is_group_product(product):
    return ('拼团' in (product.category or ''))


def is_seckill_product(product):
    return bool(getattr(product, 'is_seckill', False) or ('秒杀' in (product.category or '')))


def has_explicit_seckill_config(product):
    return any([
        product.seckill_price is not None,
        product.seckill_start_at is not None,
        product.seckill_end_at is not None,
        int(product.seckill_stock or 0) > 0
    ])


def get_seckill_available_stock(product):
    if has_explicit_seckill_config(product):
        return int(product.seckill_stock or 0)
    return int(product.stock if product.stock is not None else 0)


def get_seckill_status(product):
    if not is_seckill_product(product):
        return 'none'
    now = datetime.datetime.now()
    start_at = product.seckill_start_at
    end_at = product.seckill_end_at
    if start_at and now < start_at:
        return 'upcoming'
    if end_at and now > end_at:
        return 'ended'
    if get_seckill_available_stock(product) <= 0:
        return 'sold_out'
    return 'active'


def get_effective_product_stock(product):
    if is_seckill_product(product):
        return get_seckill_available_stock(product)
    return int(product.stock if product.stock is not None else 999)


def get_effective_product_price(product):
    if is_seckill_product(product) and get_seckill_status(product) == 'active':
        return float(product.seckill_price if product.seckill_price is not None else product.price)
    return float(product.price)


def get_user_seckill_order_count(user_id, product):
    conditions = [Order.user_id == user_id, Order.status != 0]
    product_match = []
    if product.id:
        product_match.append(Order.product_id == product.id)
    if product.title:
        product_match.append(Order.product_title == product.title)
        product_match.append(Order.product_title.like(f"{product.title} x%"))
    conditions.append(or_(*product_match))
    conditions.append(or_(Order.is_seckill_order == True, Order.category.like('%秒杀%')))
    return Order.query.filter(and_(*conditions)).count()


def serialize_product(product):
    seckill_status = get_seckill_status(product)
    return {
        'id': product.id,
        'title': product.title,
        'price': float(product.price),
        'img': product.cover_img,
        'category': product.category,
        'description': product.description,
        'is_on_sale': product.is_on_sale,
        'stock': int(product.stock if product.stock is not None else 999),
        'is_seckill': is_seckill_product(product),
        'seckill_price': float(product.seckill_price) if product.seckill_price is not None else None,
        'seckill_stock': int(product.seckill_stock or 0),
        'seckill_limit_per_user': int(product.seckill_limit_per_user or 1),
        'seckill_start_at': format_dt(product.seckill_start_at),
        'seckill_end_at': format_dt(product.seckill_end_at),
        'seckill_status': seckill_status,
        'display_price': get_effective_product_price(product),
        'display_stock': get_effective_product_stock(product),
    }


# --- 2. 璺ㄥ煙閰嶇疆 ---
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        origin = request.headers.get('Origin')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response


@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers.pop('Access-Control-Allow-Origin', None)
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


# --- 3. 鏁版嵁搴撴ā鍨?---
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
    category = db.Column(db.String(200), default='鍏朵粬')
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
    category = db.Column(db.String(50), default='鍏朵粬')
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


# --- 4. 鎺ュ彛閫昏緫 ---

@app.route('/api/common/config', methods=['GET'])
def get_system_config():
    defaults = {'group_buy_people': '2', 'seckill_time_limit': '5', 'group_buy_discount': '0.8'}
    try:
        configs = SystemConfig.query.all()
        res = defaults.copy()
        for c in configs: res[c.key] = c.value
        return jsonify({'code': 200, 'data': res})
    except:
        return jsonify({'code': 200, 'data': defaults})


@app.route('/api/admin/config', methods=['POST'])
def update_system_config():
    data = request.json
    for key, val in data.items():
        cfg = SystemConfig.query.filter_by(key=key).first()
        if not cfg:
            db.session.add(SystemConfig(key=key, value=str(val)))
        else:
            cfg.value = str(val)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '配置已更新'})


@app.route('/api/mobile/profile/update', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '璇峰厛鐧诲綍'})
    user = Member.query.get(user_id)
    data = request.json
    new_nickname = data.get('nickname')
    new_avatar = data.get('avatar')
    new_hero_text = (data.get('hero_text') or '').strip()
    if new_nickname:
        user.nickname = new_nickname
    if new_avatar:
        user.avatar = new_avatar
    if new_hero_text:
        user.hero_text = new_hero_text[:20]
    if new_nickname or new_avatar or new_hero_text:
        db.session.commit()
        return jsonify({'code': 200, 'msg': '淇敼鎴愬姛', 'nickname': user.nickname, 'avatar': user.avatar,
                        'hero_text': user.hero_text})
    return jsonify({'code': 400, 'msg': '没有可更新的内容'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'code': 400, 'msg': '未检测到文件'})
    file = request.files['file']
    if file.filename == '': return jsonify({'code': 400, 'msg': '文件名不能为空'})
    try:
        ext = 'jpg'
        if '.' in file.filename: ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'code': 200, 'url': f'http://localhost:5000/uploads/{filename}'})
    except:
        return jsonify({'code': 500})


@app.route('/uploads/<filename>')
def uploaded_file(filename): return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    # 鍘绘暟鎹簱閲屾煡璇㈢鐞嗗憳
    admin = Admin.query.filter_by(username=username, password=password).first()
    if not admin:
        return jsonify({'code': 400, 'msg': '账号或密码错误，请检查后重试'})

    session['admin_id'] = admin.id
    return jsonify({'code': 200, 'data': {'id': admin.id, 'nickname': admin.nickname, 'avatar': admin.avatar}})


@app.route('/api/admin/register', methods=['POST'])
def admin_register():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username:
        return jsonify({'code': 400, 'msg': '璐﹀彿涓嶈兘涓虹┖'})
    if len(username) < 3:
        return jsonify({'code': 400, 'msg': '账号至少 3 位'})
    if not password:
        return jsonify({'code': 400, 'msg': '瀵嗙爜涓嶈兘涓虹┖'})
    if len(password) < 6:
        return jsonify({'code': 400, 'msg': '密码至少 6 位'})

    exist = Admin.query.filter_by(username=username).first()
    if exist:
        return jsonify({'code': 400, 'msg': '账号已存在'})

    new_admin = Admin(
        username=username,
        password=password,
        nickname=f'{username}管理员',
        avatar='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    )
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'code': 200, 'msg': '娉ㄥ唽鎴愬姛'})


# --- 鍟嗗搧鎺ュ彛 (淇敼锛氬鍔?description 瀛楁) ---
@app.route('/api/products', methods=['GET', 'POST'])
def handle_products():
    if request.method == 'GET':
        products = Product.query.order_by(Product.id.desc()).all()
        return jsonify({'code': 200, 'data': [serialize_product(p) for p in products]})
    try:
        data = request.json
        new_p = Product(
            title=data.get('title', '未命名商品'),
            price=float(data.get('price', 0)),
            cover_img=data.get('img', ''),
            category=data.get('category', '鍏朵粬'),
            description=data.get('description', ''),
            is_on_sale=True,
            stock=int(data.get('stock', 999)),
            is_seckill=bool(data.get('is_seckill')),
            seckill_price=float(data.get('seckill_price')) if data.get('seckill_price') not in (None, '') else None,
            seckill_stock=int(data.get('seckill_stock', 0) or 0),
            seckill_limit_per_user=int(data.get('seckill_limit_per_user', 1) or 1),
            seckill_start_at=parse_dt(data.get('seckill_start_at')),
            seckill_end_at=parse_dt(data.get('seckill_end_at'))
        )
        db.session.add(new_p)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '鍙戝竷鎴愬姛'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': '鍙戝竷澶辫触'})


@app.route('/api/products/<int:id>', methods=['PUT', 'DELETE'])
def modify_product(id):
    p = Product.query.get(id)
    if request.method == 'PUT':
        data = request.json
        p.title = data.get('title')
        p.price = data.get('price')
        p.cover_img = data.get('img')
        p.category = data.get('category')
        p.description = data.get('description')
        if data.get('stock') is not None:
            p.stock = int(data.get('stock'))
        p.is_seckill = bool(data.get('is_seckill'))
        p.seckill_price = float(data.get('seckill_price')) if data.get('seckill_price') not in (None, '') else None
        p.seckill_stock = int(data.get('seckill_stock', 0) or 0)
        p.seckill_limit_per_user = int(data.get('seckill_limit_per_user', 1) or 1)
        p.seckill_start_at = parse_dt(data.get('seckill_start_at'))
        p.seckill_end_at = parse_dt(data.get('seckill_end_at'))
        db.session.commit()
        return jsonify({'code': 200})
    db.session.delete(p)
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/products/<int:id>/status', methods=['POST'])
def toggle_status(id):
    p = Product.query.get(id)
    p.is_on_sale = not p.is_on_sale
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/products/<int:id>/comments', methods=['GET'])
def get_product_comments(id):
    rows = db.session.query(Comment, Member, Order).join(Order, Comment.order_id == Order.id).join(Member, Comment.user_id == Member.id).filter(Order.product_id == id).order_by(Comment.id.desc()).all()
    data = [{'id': c.id, 'user': m.nickname, 'avatar': m.avatar, 'rating': c.rating, 'content': c.content, 'date': c.created_at.strftime('%Y-%m-%d')} for c, m, o in rows]
    return jsonify({'code': 200, 'data': data})


# --- 杞挱鍥炬帴鍙?---
@app.route('/api/banners', methods=['GET', 'POST'])
def handle_banners():
    if request.method == 'GET':
        banners = Banner.query.all()
        return jsonify({'code': 200, 'data': [{'id': b.id, 'img': b.img, 'note': b.note} for b in banners]})
    data = request.json
    db.session.add(Banner(img=data['img'], note=data.get('note', '')))
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/banners/<int:id>', methods=['DELETE'])
def delete_banner(id):
    b = Banner.query.get(id)
    db.session.delete(b)
    db.session.commit()
    return jsonify({'code': 200})


# --- 鐢ㄦ埛璁よ瘉鎺ュ彛 ---
@app.route('/api/mobile/register', methods=['POST'])
def mobile_register():
    if Member.query.filter_by(username=request.json['username']).first(): return jsonify({'code': 400, 'msg': '账号已存在'})
    user = Member(username=request.json['username'], password=request.json['password'],
                  nickname=f"鐢ㄦ埛{random.randint(100, 999)}", balance=10000.00, points=500,
                  hero_text='鸟为什么会飞')
    db.session.add(user)
    db.session.flush()

    newcomer_coupon = SystemCoupon.query.filter(SystemCoupon.name.like('%新人%')).order_by(SystemCoupon.id.asc()).first()
    if not newcomer_coupon:
        newcomer_coupon = SystemCoupon(name='新人礼券', amount=10.00, min_spend=0.00, limit_level=1, stock=999)
        db.session.add(newcomer_coupon)
        db.session.flush()
    granted_coupon_name = None
    if newcomer_coupon and newcomer_coupon.stock > 0:
        newcomer_coupon.stock -= 1
        db.session.add(UserCoupon(
            user_id=user.id,
            sys_coupon_id=newcomer_coupon.id,
            name=newcomer_coupon.name,
            amount=newcomer_coupon.amount,
            min_spend=newcomer_coupon.min_spend,
            status=0
        ))
        granted_coupon_name = newcomer_coupon.name

    db.session.commit()
    return jsonify({
        'code': 200,
        'msg': '注册成功',
        'newcomer_coupon_received': bool(granted_coupon_name),
        'newcomer_coupon_name': granted_coupon_name
    })


@app.route('/api/mobile/login', methods=['POST'])
def mobile_login():
    u = Member.query.filter_by(username=request.json['username'], password=request.json['password']).first()
    if not u: return jsonify({'code': 401, 'msg': '閿欒'})
    session['user_id'] = u.id
    return jsonify({'code': 200,
                    'data': {'id': u.id, 'nickname': u.nickname, 'level': u.level, 'balance': float(u.balance),
                             'points': u.points, 'avatar': u.avatar, 'hero_text': u.hero_text or '鸟为什么会飞'}})


@app.route('/api/mobile/signin', methods=['POST'])
def user_signin():
    u = Member.query.get(session.get('user_id'))
    u.points += 100
    db.session.commit()
    return jsonify({'code': 200, 'msg': f'绛惧埌+100', 'points': u.points})


# --- 浼樻儬鍒告帴鍙?---
@app.route('/api/admin/coupons', methods=['GET'])
def admin_get_coupons():
    coupons = SystemCoupon.query.all()
    return jsonify({'code': 200, 'data': [
        {'id': c.id, 'name': c.name, 'amount': float(c.amount), 'min_spend': float(c.min_spend),
         'limit_level': c.limit_level, 'stock': c.stock} for c in coupons]})
    return jsonify({'code': 200, 'data': [
        {'id': c.id, 'name': c.name, 'amount': float(c.amount), 'min_spend': float(c.min_spend),
         'limit_level': c.limit_level, 'stock': c.stock} for c in coupons]})


@app.route('/api/admin/coupons', methods=['POST'])
def admin_add_coupon():
    data = request.json
    new_c = SystemCoupon(name=data['name'], amount=float(data['amount']), min_spend=float(data['min_spend']),
                         limit_level=int(data.get('limit_level', 1)), stock=int(data.get('stock', 100)))
    db.session.add(new_c)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '娣诲姞鎴愬姛'})


@app.route('/api/admin/coupons/<int:id>', methods=['PUT'])
def admin_update_coupon(id):
    c = SystemCoupon.query.get(id)
    data = request.json
    c.name = data['name']
    c.amount = float(data['amount'])
    c.min_spend = float(data['min_spend'])
    c.limit_level = int(data['limit_level'])
    c.stock = int(data['stock'])
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/admin/coupons/<int:id>', methods=['DELETE'])
def admin_delete_coupon(id):
    c = SystemCoupon.query.get(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/coupon/market', methods=['GET'])
def get_coupon_market():
    coupons = SystemCoupon.query.filter(SystemCoupon.stock > 0).all()
    return jsonify({'code': 200, 'data': [
        {'id': c.id, 'name': c.name, 'amount': float(c.amount), 'min_spend': float(c.min_spend),
         'limit_level': c.limit_level, 'desc': (f'满{float(c.min_spend)}可用' if c.min_spend > 0 else '无门槛')} for c in
        coupons]})


@app.route('/api/mobile/coupon/get', methods=['POST'])
def get_coupon():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '璇峰厛鐧诲綍'})
    sys_coupon_id = request.json.get('id')
    sys_coupon = SystemCoupon.query.get(sys_coupon_id)
    if not sys_coupon: return jsonify({'code': 400, 'msg': '浼樻儬鍒镐笉瀛樺湪'})
    if sys_coupon.stock <= 0: return jsonify({'code': 400, 'msg': '手慢了，已抢光'})
    user = Member.query.get(user_id)
    if user.level < sys_coupon.limit_level:
        level_names = {1: '普通会员', 2: '黄金VIP', 3: '钻石VIP'}
        return jsonify({'code': 400, 'msg': f'浠呴檺 {level_names.get(sys_coupon.limit_level)} 棰嗗彇'})
    if UserCoupon.query.filter_by(user_id=user_id, sys_coupon_id=sys_coupon.id).first():
        return jsonify({'code': 400, 'msg': '您已领取过该券'})
    sys_coupon.stock -= 1
    db.session.add(
        UserCoupon(user_id=user_id, sys_coupon_id=sys_coupon.id, name=sys_coupon.name, amount=sys_coupon.amount,
                   min_spend=sys_coupon.min_spend, status=0))
    db.session.commit()
    return jsonify({'code': 200, 'msg': '棰嗗彇鎴愬姛'})


@app.route('/api/mobile/coupon/my', methods=['GET'])
def my_coupons():
    cs = UserCoupon.query.filter_by(user_id=session.get('user_id'), status=0).all()
    return jsonify({'code': 200,
                    'data': [{'id': c.id, 'name': c.name, 'amount': float(c.amount), 'min_spend': float(c.min_spend)}
                             for c in cs]})


@app.route('/api/mobile/vip/upgrade', methods=['POST'])
def upgrade_vip():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '璇峰厛鐧诲綍'})
    target_level = request.json.get('level')
    user = Member.query.get(user_id)
    if user.level >= target_level: return jsonify({'code': 400, 'msg': '您已是该等级或更高等级'})
    user.level = target_level
    db.session.commit()
    return jsonify({'code': 200, 'msg': '鍗囩骇鎴愬姛', 'level': user.level})


@app.route('/api/mobile/address', methods=['GET', 'POST'])
def handle_address():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'code': 401, 'msg': '请先登录'})
    if request.method == 'GET':
        addrs = Address.query.filter_by(user_id=user_id).order_by(Address.id.asc()).all()
        if addrs and not any(a.is_default for a in addrs):
            addrs[0].is_default = True
            db.session.commit()
        return jsonify(
            {'code': 200, 'data': [
                {'id': a.id, 'name': a.name, 'phone': a.phone, 'detail': a.detail, 'is_default': bool(a.is_default)}
                for a in sorted(addrs, key=lambda item: (not bool(item.is_default), item.id))
            ]})

    is_default = bool(request.json.get('is_default'))
    user_addrs = Address.query.filter_by(user_id=user_id).all()
    if not user_addrs:
        is_default = True
    if is_default:
        for addr in user_addrs:
            addr.is_default = False
    db.session.add(Address(
        user_id=user_id,
        name=request.json['name'],
        phone=request.json['phone'],
        detail=request.json['detail'],
        is_default=is_default
    ))
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/address/<int:addr_id>/default', methods=['POST'])
def set_default_address(addr_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'code': 401, 'msg': '请先登录'})
    addr = Address.query.filter_by(id=addr_id, user_id=user_id).first()
    if not addr:
        return jsonify({'code': 404, 'msg': '地址不存在'})
    user_addrs = Address.query.filter_by(user_id=user_id).all()
    for item in user_addrs:
        item.is_default = item.id == addr.id
    db.session.commit()
    return jsonify({'code': 200, 'msg': '设置成功'})


@app.route('/api/mobile/order', methods=['POST'])
def create_order():
    user_id = session.get('user_id')
    data = request.json
    p = Product.query.get(data.get('product_id'))
    u = Member.query.get(user_id)
    addr = Address.query.get(data.get('address_id'))
    if not addr: return jsonify({'code': 400, 'msg': '璇烽€夋嫨鍦板潃'})
    if not p:
        return jsonify({'code': 404, 'msg': '商品不存在'})

    is_group_item = is_group_product(p)
    is_seckill_item = is_seckill_product(p)
    if not is_seckill_item and p.stock is not None and p.stock <= 0:
        return jsonify({'code': 400, 'msg': '该商品已售罄'})

    group_action = data.get('group_action')

    discount_cfg = SystemConfig.query.filter_by(key='group_buy_discount').first()
    group_discount = float(discount_cfg.value) if discount_cfg else 0.8

    if is_seckill_item:
        seckill_status = get_seckill_status(p)
        if seckill_status == 'upcoming':
            return jsonify({'code': 400, 'msg': '秒杀未开始'})
        if seckill_status == 'ended':
            return jsonify({'code': 400, 'msg': '秒杀已结束'})
        if seckill_status == 'sold_out':
            return jsonify({'code': 400, 'msg': '秒杀已售罄'})
        if data.get('coupon_id') or data.get('use_points'):
            return jsonify({'code': 400, 'msg': '秒杀商品不支持优惠券和积分抵扣'})
        bought_count = get_user_seckill_order_count(user_id, p)
        if bought_count >= int(p.seckill_limit_per_user or 1):
            return jsonify({'code': 400, 'msg': f'秒杀商品每人限购 {int(p.seckill_limit_per_user or 1)} 件'})
        base = float(p.seckill_price if p.seckill_price is not None else p.price)
    elif is_group_item and group_action:
        base = float(p.price) * group_discount
    else:
        member_discount = 0.9 if u.level == 2 else (0.8 if u.level == 3 else 1)
        base = float(p.price) * member_discount

    deduct = 0
    if data.get('coupon_id'):
        uc = UserCoupon.query.get(data.get('coupon_id'))
        if uc and uc.status == 0:
            deduct = float(uc.amount)
            uc.status = 1

    p_deduct = 0
    if data.get('use_points'):
        max_d = base - deduct
        if max_d < 0: max_d = 0
        needed = int(max_d * 100)
        if u.points >= needed:
            p_deduct = max_d
            u.points -= needed
        else:
            p_deduct = u.points / 100.0
            u.points = 0

    final = base - deduct - p_deduct
    if final < 0: final = 0

    if u.balance < final: return jsonify({'code': 400, 'msg': '余额不足'})
    u.balance = float(u.balance) - final

    order_status = 1
    team_id = None

    if is_group_item and group_action:
        if group_action == 'create':
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            new_team = GroupTeam(code=code, product_id=p.id, initiator_id=u.id, current_num=1, status=0)
            db.session.add(new_team)
            db.session.flush()
            team_id = new_team.id
            order_status = 5
        elif group_action == 'join':
            code = data.get('group_code')
            team = GroupTeam.query.filter_by(code=code, status=0).first()
            if not team: return jsonify({'code': 400, 'msg': '拼团码无效或已过期'})
            if team.product_id != p.id: return jsonify({'code': 400, 'msg': '鎷煎洟鐮佸晢鍝佷笉鍖归厤'})
            team.current_num += 1
            team.status = 1
            team_id = team.id
            order_status = 1
            leader_order = Order.query.filter_by(group_team_id=team.id, status=5).first()
            if leader_order: leader_order.status = 1

    if is_seckill_item:
        if has_explicit_seckill_config(p):
            p.seckill_stock = int(p.seckill_stock or 0) - 1
        elif p.stock is not None:
            p.stock -= 1
    elif p.stock is not None:
        p.stock -= 1
    o = Order(order_no=f"ORD{random.randint(1000, 9999)}", user_id=u.id, product_title=p.title, product_img=p.cover_img,
              total_amount=final, status=order_status, address_snapshot=f"{addr.name} {addr.detail}",
              category=p.category, group_team_id=team_id, product_id=p.id, is_seckill_order=is_seckill_item)
    db.session.add(o)
    db.session.commit()

    ret_data = {'code': 200, 'msg': '鎴愬姛', 'balance': float(u.balance), 'points': u.points, 'order_id': o.id}
    if is_group_item and group_action == 'create':
        team = GroupTeam.query.get(team_id)
        ret_data['group_code'] = team.code

    return jsonify(ret_data)


@app.route('/api/mobile/cart/add', methods=['POST'])
def add_cart():
    u = session.get('user_id')
    p = Product.query.get(request.json.get('product_id'))
    if not p:
        return jsonify({'code': 404, 'msg': '商品不存在'})
    if is_seckill_product(p):
        return jsonify({'code': 400, 'msg': '秒杀商品请直接购买'})
    c = Cart.query.filter_by(user_id=u, product_id=p.id).first()
    if c:
        c.num += 1
    else:
        db.session.add(Cart(user_id=u, product_id=p.id, num=1))
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/cart/list', methods=['GET'])
def get_cart_list():
    res = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id).filter(
        Cart.user_id == session.get('user_id')).all()
    return jsonify({'code': 200, 'data': [
        {**serialize_product(p), 'id': c.id, 'product_id': p.id, 'num': c.num} for c, p in res]})


@app.route('/api/mobile/cart/update', methods=['POST'])
def update_cart():
    c = Cart.query.get(request.json['id'])
    n = request.json['num']
    if n <= 0:
        db.session.delete(c)
    else:
        c.num = n
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/cart/checkout', methods=['POST'])
def cart_checkout():
    user_id = session.get('user_id')
    data = request.json
    addr = Address.query.get(data.get('address_id'))
    if not addr: return jsonify({'code': 400, 'msg': '璇烽€夋嫨鍦板潃'})

    user = Member.query.get(user_id)
    coupon_id = data.get('coupon_id')
    use_points = data.get('use_points')

    total = 0
    items = []
    for cid in data.get('cart_ids'):
        c = Cart.query.get(cid)
        if c:
            p = Product.query.get(c.product_id)
            if is_seckill_product(p):
                return jsonify({'code': 400, 'msg': f'《{p.title}》为秒杀商品，请直接购买'})
            if p.stock is not None and p.stock <= 0:
                return jsonify({'code': 400, 'msg': f'《{p.title}》已售罄，请移除后再结算'})
            discount = 0.9 if user.level == 2 else (0.8 if user.level == 3 else 1)
            amt = float(p.price) * c.num * discount
            total += amt
            items.append({'c': c, 'p': p, 'amt': amt})

    c_deduct = 0
    if coupon_id:
        uc = UserCoupon.query.get(coupon_id)
        if uc and uc.status == 0:
            if total >= float(uc.min_spend):
                c_deduct = float(uc.amount)
                uc.status = 1
            else:
                return jsonify({'code': 400, 'msg': '未满足优惠券使用门槛'})

    p_deduct = 0
    if use_points:
        max_d = total - c_deduct
        if max_d < 0: max_d = 0
        needed = int(max_d * 100)
        if user.points >= needed:
            p_deduct = max_d
            user.points -= needed
        else:
            p_deduct = user.points / 100.0
            user.points = 0

    final = total - c_deduct - p_deduct
    if final < 0: final = 0

    if user.balance < final: return jsonify({'code': 400, 'msg': '浣欓涓嶈冻'})
    user.balance = float(user.balance) - final
    orders = []
    to_del = []
    for i in items:
        if i['p'].stock is not None:
            i['p'].stock -= i['c'].num
        orders.append(Order(order_no=f"CT{random.randint(1000, 9999)}", user_id=user.id,
                            product_title=f"{i['p'].title} x{i['c'].num}", product_img=i['p'].cover_img,
                            total_amount=i['amt'], status=1, address_snapshot=f"{addr.name} {addr.detail}",
                            category=i['p'].category, product_id=i['p'].id))
        to_del.append(i['c'])

    db.session.add_all(orders)
    for c in to_del: db.session.delete(c)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '鎴愬姛', 'balance': float(user.balance), 'points': user.points})


@app.route('/api/mobile/orders/<int:id>', methods=['GET'])
def get_order_detail(id):
    o = Order.query.get(id)
    if o.status == 5 and o.group_team_id:
        team = GroupTeam.query.get(o.group_team_id)
        if team and team.status == 0:
            if datetime.datetime.now() > team.created_at + timedelta(minutes=10):
                team.status = 2
                o.status = 6
                db.session.commit()

    team_code = ''
    if o.group_team_id:
        team = GroupTeam.query.get(o.group_team_id)
        if team: team_code = team.code

    return jsonify({'code': 200, 'data': {'no': o.order_no, 'title': o.product_title, 'img': o.product_img,
                                          'amount': float(o.total_amount), 'status': o.status,
                                          'address': o.address_snapshot, 'date': str(o.created_at),
                                          'group_code': team_code, 'tracking_no': o.tracking_no}})


@app.route('/api/admin/orders', methods=['GET'])
def admin_get_orders():
    res = db.session.query(Order, Member).join(Member, Order.user_id == Member.id).order_by(Order.id.desc()).all()
    return jsonify({'code': 200, 'data': [
        {'id': o.id, 'no': o.order_no, 'user': m.nickname, 'title': o.product_title, 'img': o.product_img,
         'amount': float(o.total_amount), 'status': o.status, 'date': str(o.created_at),
         'tracking_no': o.tracking_no or ''} for o, m in res]})


@app.route('/api/admin/orders/<int:id>/ship', methods=['POST'])
def ship_order(id):
    o = Order.query.get(id)
    if not o:
        return jsonify({'code': 404, 'msg': '订单不存在'})
    if o.status != 1:
        return jsonify({'code': 400, 'msg': '当前订单状态不可发货'})
    data = request.json or {}
    tracking_no = (data.get('tracking_no') or '').strip()
    if not tracking_no:
        return jsonify({'code': 400, 'msg': '请填写快递单号'})
    o.status = 2
    o.tracking_no = tracking_no
    o.shipped_at = datetime.datetime.now()
    db.session.commit()
    return jsonify({'code': 200, 'tracking_no': o.tracking_no})


@app.route('/api/mobile/orders/<int:id>/cancel', methods=['POST'])
def cancel_order(id):
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '璇峰厛鐧诲綍'})
    o = Order.query.get(id)
    if not o or o.user_id != user_id: return jsonify({'code': 400, 'msg': '订单不存在'})
    if o.status != 1: return jsonify({'code': 400, 'msg': '该订单无法取消'})
    u = Member.query.get(user_id)
    u.balance = float(u.balance) + float(o.total_amount)
    if o.product_id:
        p = Product.query.get(o.product_id)
        if p:
            if o.is_seckill_order:
                p.seckill_stock = int(p.seckill_stock or 0) + 1
            elif p.stock is not None:
                p.stock += 1
    o.status = 0
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已取消', 'balance': float(u.balance)})


@app.route('/api/admin/members', methods=['GET'])
def admin_get_members():
    members = Member.query.order_by(Member.id.desc()).all()
    return jsonify({'code': 200, 'data': [
        {'id': m.id, 'username': m.username, 'nickname': m.nickname, 'level': m.level,
         'balance': float(m.balance), 'points': m.points, 'avatar': m.avatar} for m in members]})


@app.route('/api/admin/member/recharge', methods=['POST'])
def admin_recharge_member():
    data = request.json
    m = Member.query.get(data.get('user_id'))
    if not m: return jsonify({'code': 400, 'msg': '用户不存在'})
    m.balance = float(m.balance) + float(data.get('amount', 0))
    db.session.commit()
    return jsonify({'code': 200, 'msg': '充值成功', 'balance': float(m.balance)})


@app.route('/api/mobile/my_orders', methods=['GET'])
def my_orders():
    orders = Order.query.filter_by(user_id=session.get('user_id')).order_by(Order.id.desc()).all()
    return jsonify({'code': 200, 'data': [
        {'id': o.id, 'no': o.order_no, 'title': o.product_title, 'img': o.product_img, 'amount': float(o.total_amount),
         'status': o.status} for o in orders]})


@app.route('/api/mobile/orders/<int:id>/confirm', methods=['POST'])
def confirm_receipt(id):
    o = Order.query.get(id)
    o.status = 3
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/favorite/toggle', methods=['POST'])
def toggle_favorite():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '璇峰厛鐧诲綍'})
    product_id = request.json.get('product_id')
    f = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
    action = ''
    if f:
        db.session.delete(f)
        action = 'remove'
        msg = '已取消收藏'
    else:
        db.session.add(Favorite(user_id=user_id, product_id=product_id))
        action = 'add'
        msg = '已收藏'
    db.session.commit()
    return jsonify({'code': 200, 'msg': msg, 'action': action})


@app.route('/api/mobile/favorites', methods=['GET'])
def get_favorites():
    res = db.session.query(Favorite, Product).join(Product, Favorite.product_id == Product.id).filter(
        Favorite.user_id == session.get('user_id')).all()
    return jsonify({'code': 200, 'data': [serialize_product(p) for f, p in res]})


@app.route('/api/mobile/comments/add', methods=['POST'])
def add_comment():
    data = request.json
    db.session.add(Comment(user_id=session.get('user_id'), order_id=data['order_id'], content=data['content'],
                           rating=data['rating']))
    o = Order.query.get(data['order_id'])
    o.status = 4
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/admin/comments', methods=['GET'])
def get_comments():
    res = db.session.query(Comment, Member, Order).join(Member, Comment.user_id == Member.id).join(Order,
                                                                                                   Comment.order_id == Order.id).order_by(
        Comment.id.desc()).all()
    return jsonify({'code': 200, 'data': [
        {'id': c.id, 'user': m.nickname, 'product': o.product_title, 'content': c.content, 'rating': c.rating,
         'date': str(c.created_at)} for c, m, o in res]})


@app.route('/api/admin/comments/<int:id>', methods=['DELETE'])
def delete_comment(id):
    c = Comment.query.get(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    # 鍩虹 KPI
    total_sales = float(db.session.query(func.sum(Order.total_amount)).scalar() or 0)
    total_orders = Order.query.count()
    total_products = Product.query.filter_by(is_on_sale=True).count()
    total_members = Member.query.count()

    # 浠婃棩 vs 鏄ㄦ棩
    today_sales = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == today).scalar() or 0)
    yest_sales  = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == yesterday).scalar() or 0)
    today_orders = Order.query.filter(func.date(Order.created_at) == today).count()
    yest_orders  = Order.query.filter(func.date(Order.created_at) == yesterday).count()
    today_members = Member.query.filter(func.date(Member.id > 0)).count()  # 鍗犱綅锛屼笅闈㈢敤娉ㄥ唽鏃ユ湡
    new_members_today = 0  # Member 鏃犳敞鍐屾椂闂村瓧娈碉紝浠?浠ｆ浛

    # 近 7 天每日数据
    trend_sales, trend_orders, trend_dates = [], [], []
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        s = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == d).scalar() or 0)
        c = Order.query.filter(func.date(Order.created_at) == d).count()
        trend_sales.append(round(s, 2))
        trend_orders.append(c)
        trend_dates.append(f'{d.month}/{d.day}')
    # 鍒嗙被閿€鍞 Top 8
    cat_stats = db.session.query(Order.category, func.sum(Order.total_amount), func.count(Order.id))\
        .group_by(Order.category).order_by(func.sum(Order.total_amount).desc()).limit(8).all()
    category_data = [{'name': c or '鍏朵粬', 'sales': round(float(a), 2), 'orders': int(n)} for c, a, n in cat_stats if c]

    # 订单状态分布
    status_map = {0: '已取消', 1: '待发货', 2: '运输中', 3: '待评价', 4: '已完成', 5: '拼团中'}
    status_rows = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    status_data = [{'name': status_map.get(s, f'状态{s}'), 'value': int(c)} for s, c in status_rows]
    # 寰呭彂璐ц鍗曟暟
    pending_ship = Order.query.filter_by(status=1).count()

    # 浣庡簱瀛樺晢鍝?(搴撳瓨 < 10)
    low_stock = Product.query.filter(Product.stock < 10, Product.is_on_sale == True).order_by(Product.stock.asc()).limit(5).all()
    low_stock_data = [{'id': p.id, 'title': p.title, 'stock': p.stock, 'img': p.cover_img} for p in low_stock]

    # 鐑攢鍟嗗搧 Top 5
    hot = db.session.query(Order.product_title, Order.product_img, func.count(Order.id).label('cnt'), func.sum(Order.total_amount).label('amt'))\
        .group_by(Order.product_title, Order.product_img).order_by(func.count(Order.id).desc()).limit(5).all()
    hot_data = [{'title': t, 'img': img, 'count': int(c), 'amount': round(float(a), 2)} for t, img, c, a in hot]

    # 浼氬憳绛夌骇鍒嗗竷
    level_rows = db.session.query(Member.level, func.count(Member.id)).group_by(Member.level).all()
    level_data = [{'name': ['', '普通会员', '黄金VIP', '钻石VIP'][l] if l <= 3 else f'等级{l}', 'value': int(c)} for l, c in level_rows]
    # 璇勪环鍧囧垎
    avg_rating = float(db.session.query(func.avg(Comment.rating)).scalar() or 0)

    def pct(a, b):
        if b == 0: return None
        return round((a - b) / b * 100, 1)

    return jsonify({'code': 200, 'data': {
        'total_sales': total_sales, 'total_orders': total_orders,
        'total_products': total_products, 'total_members': total_members,
        'today_sales': today_sales, 'yest_sales': yest_sales,
        'today_orders': today_orders, 'yest_orders': yest_orders,
        'sales_pct': pct(today_sales, yest_sales),
        'orders_pct': pct(today_orders, yest_orders),
        'aov': round(total_sales / total_orders, 2) if total_orders else 0,
        'pending_ship': pending_ship, 'avg_rating': round(avg_rating, 1),
        'trend_dates': trend_dates, 'trend_sales': trend_sales, 'trend_orders': trend_orders,
        'category_data': category_data, 'status_data': status_data,
        'hot_data': hot_data, 'low_stock': low_stock_data, 'level_data': level_data,
        'chart': [{'name': c or '鍏朵粬', 'value': round(float(a), 2)} for c, a, n in cat_stats if c]
    }})


@app.route('/api/mobile/recharge', methods=['POST'])
def recharge_balance():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '璇峰厛鐧诲綍'})
    try:
        amount = float(request.json.get('amount', 0))
    except:
        return jsonify({'code': 400, 'msg': '閲戦鏍煎紡閿欒'})
    if amount <= 0: return jsonify({'code': 400, 'msg': '閲戦蹇呴』澶т簬0'})
    u = Member.query.get(user_id)
    u.balance = float(u.balance) + amount
    db.session.commit()
    return jsonify({'code': 200, 'msg': '充值成功', 'balance': float(u.balance)})


@app.route('/api/mobile/orders/<int:id>/logistics', methods=['GET'])
def get_order_logistics(id):
    o = Order.query.get(id)
    if not o:
        return jsonify({'code': 404})
    traces = []
    base_time = o.created_at or datetime.datetime.now()
    tracking_no = o.tracking_no or '待分配'

    def build_trace(time_point, desc):
        return {'time': time_point.strftime('%Y-%m-%d %H:%M:%S'), 'desc': desc}

    traces.append(build_trace(base_time, f'订单已提交，系统正在处理。订单号：{o.order_no}'))
    traces.append(build_trace(base_time + timedelta(minutes=8), '支付成功，订单进入商家备货队列'))
    traces.append(build_trace(base_time + timedelta(minutes=25), '仓库已接单，正在进行商品分拣'))
    if o.status >= 2:
        ship_time = o.shipped_at or (base_time + timedelta(hours=2))
        traces.append(build_trace(ship_time - timedelta(minutes=20), '商品复核完成，包裹已完成出库扫描'))
        traces.append(build_trace(ship_time, f'商家已发货，快递单号：{tracking_no}'))
        traces.append(build_trace(ship_time + timedelta(minutes=40), f'快件已由仓库揽收，运输单号：{tracking_no}'))
        traces.append(build_trace(ship_time + timedelta(hours=6), '快件运输中，已发往目的地分拨中心'))
        traces.append(build_trace(ship_time + timedelta(hours=12), '包裹已到达区域分拨中心，正在安排转运'))
    if o.status >= 3:
        receive_time = (o.shipped_at or base_time) + timedelta(days=1)
        traces.append(build_trace(receive_time - timedelta(hours=6), '包裹已到达派送站点，等待快递员出仓'))
        traces.append(build_trace(receive_time - timedelta(hours=3), '快递员正在派送，请保持电话畅通'))
        traces.append(build_trace(receive_time, '订单已签收，感谢您使用 Smart Mall'))
    return jsonify({'code': 200, 'data': sorted(traces, key=lambda x: x['time'], reverse=True)})





if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # 自动补充新增字段（create_all 不会给已有表加列）
        with db.engine.connect() as conn:
            inspector = inspect(db.engine)
            product_cols = [c['name'] for c in inspector.get_columns('product')]
            if 'stock' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN stock INT DEFAULT 999'))
                conn.commit()
            if 'is_seckill' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN is_seckill BOOLEAN DEFAULT 0'))
                conn.commit()
            if 'seckill_price' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN seckill_price NUMERIC(10, 2) NULL'))
                conn.commit()
            if 'seckill_stock' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN seckill_stock INT DEFAULT 0'))
                conn.commit()
            if 'seckill_limit_per_user' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN seckill_limit_per_user INT DEFAULT 1'))
                conn.commit()
            if 'seckill_start_at' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN seckill_start_at DATETIME NULL'))
                conn.commit()
            if 'seckill_end_at' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN seckill_end_at DATETIME NULL'))
                conn.commit()
            order_cols = [c['name'] for c in inspector.get_columns('orders')]
            if 'product_id' not in order_cols:
                conn.execute(text('ALTER TABLE orders ADD COLUMN product_id INT NULL'))
                conn.commit()
            if 'tracking_no' not in order_cols:
                conn.execute(text('ALTER TABLE orders ADD COLUMN tracking_no VARCHAR(50) NULL'))
                conn.commit()
            if 'shipped_at' not in order_cols:
                conn.execute(text('ALTER TABLE orders ADD COLUMN shipped_at DATETIME NULL'))
                conn.commit()
            if 'is_seckill_order' not in order_cols:
                conn.execute(text('ALTER TABLE orders ADD COLUMN is_seckill_order BOOLEAN DEFAULT 0'))
                conn.commit()
            member_cols = [c['name'] for c in inspector.get_columns('member')]
            if 'hero_text' not in member_cols:
                conn.execute(text("ALTER TABLE member ADD COLUMN hero_text VARCHAR(100) DEFAULT '鸟为什么会飞'"))
                conn.commit()
            address_cols = [c['name'] for c in inspector.get_columns('address')]
            if 'is_default' not in address_cols:
                conn.execute(text('ALTER TABLE address ADD COLUMN is_default BOOLEAN DEFAULT 0'))
                conn.commit()

        # 初始化默认管理员账号（仅当管理员表为空时）
        if Admin.query.count() == 0:
            default_admin = Admin(
                username='admin',
                password='123456',
                nickname='超级管理员',
                avatar='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
            )
            db.session.add(default_admin)

        if not SystemConfig.query.filter_by(key='group_buy_people').first():
            db.session.add(SystemConfig(key='group_buy_people', value='2', desc='鎷煎洟鎴愬洟浜烘暟'))
            db.session.add(SystemConfig(key='seckill_time_limit', value='5', desc='绉掓潃闄愭椂(鍒嗛挓)'))
            db.session.add(SystemConfig(key='group_buy_discount', value='0.8', desc='鎷煎洟鎶樻墸'))
        if SystemCoupon.query.count() == 0:
            db.session.add(SystemCoupon(name='鏂颁汉绀煎埜', amount=10, min_spend=0, limit_level=1, stock=999))
            db.session.add(SystemCoupon(name='鏁扮爜绁炲埜', amount=100, min_spend=0, limit_level=1, stock=50))
            db.session.add(SystemCoupon(name='榛勯噾涓撳睘', amount=50, min_spend=300, limit_level=2, stock=20))
        db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)
