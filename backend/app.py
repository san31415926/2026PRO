import os
import random
import string
import io
import datetime
import uuid
from datetime import timedelta
from flask import Flask, jsonify, request, session, send_file, send_from_directory, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- 1. 初始化配置 ---
app = Flask(__name__)
app.secret_key = 'panweiyu_secret_key'

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:panweiyu123@localhost/smart_mall'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 图片上传文件夹配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)


# --- 2. 跨域配置 ---
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


# --- 3. 数据库模型 ---
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


class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    detail = db.Column(db.String(200))


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


# --- 4. 接口逻辑 ---

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
    if not user_id: return jsonify({'code': 401, 'msg': '请先登录'})
    user = Member.query.get(user_id)
    data = request.json
    new_nickname = data.get('nickname')
    new_avatar = data.get('avatar')
    if new_nickname:
        user.nickname = new_nickname
    if new_avatar:
        user.avatar = new_avatar
    if new_nickname or new_avatar:
        db.session.commit()
        return jsonify({'code': 200, 'msg': '修改成功', 'nickname': user.nickname, 'avatar': user.avatar})
    return jsonify({'code': 400, 'msg': '无修改内容'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'code': 400, 'msg': '无文件'})
    file = request.files['file']
    if file.filename == '': return jsonify({'code': 400, 'msg': '文件名为空'})
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

    # 去数据库里查询管理员
    admin = Admin.query.filter_by(username=username, password=password).first()
    if not admin:
        return jsonify({'code': 400, 'msg': '账号或密码错误！请检查'})

    session['admin_id'] = admin.id
    return jsonify({'code': 200, 'data': {'id': admin.id, 'nickname': admin.nickname, 'avatar': admin.avatar}})


@app.route('/api/admin/register', methods=['POST'])
def admin_register():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username:
        return jsonify({'code': 400, 'msg': '账号不能为空'})
    if len(username) < 3:
        return jsonify({'code': 400, 'msg': '账号至少3位'})
    if not password:
        return jsonify({'code': 400, 'msg': '密码不能为空'})
    if len(password) < 6:
        return jsonify({'code': 400, 'msg': '密码至少6位'})

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

    return jsonify({'code': 200, 'msg': '注册成功'})


# --- 商品接口 (修改：增加 description 字段) ---
@app.route('/api/products', methods=['GET', 'POST'])
def handle_products():
    if request.method == 'GET':
        products = Product.query.order_by(Product.id.desc()).all()
        # GET 返回 description
        return jsonify({'code': 200, 'data': [
            {'id': p.id, 'title': p.title, 'price': float(p.price), 'img': p.cover_img, 'category': p.category,
             'description': p.description, 'is_on_sale': p.is_on_sale, 'stock': p.stock if p.stock is not None else 999} for p in products]})
    try:
        data = request.json
        # POST 接收 description
        new_p = Product(
            title=data.get('title', '未命名'),
            price=float(data.get('price', 0)),
            cover_img=data.get('img', ''),
            category=data.get('category', '其他'),
            description=data.get('description', ''),
            is_on_sale=True,
            stock=int(data.get('stock', 999))
        )
        db.session.add(new_p)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '发布成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': '发布失败'})


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


# --- 轮播图接口 ---
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


# --- 用户认证接口 ---
@app.route('/api/mobile/register', methods=['POST'])
def mobile_register():
    if Member.query.filter_by(username=request.json['username']).first(): return jsonify({'code': 400, 'msg': '已存在'})
    db.session.add(Member(username=request.json['username'], password=request.json['password'],
                          nickname=f"用户{random.randint(100, 999)}", balance=10000.00, points=500))
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/login', methods=['POST'])
def mobile_login():
    u = Member.query.filter_by(username=request.json['username'], password=request.json['password']).first()
    if not u: return jsonify({'code': 401, 'msg': '错误'})
    session['user_id'] = u.id
    return jsonify({'code': 200,
                    'data': {'id': u.id, 'nickname': u.nickname, 'level': u.level, 'balance': float(u.balance),
                             'points': u.points, 'avatar': u.avatar}})


@app.route('/api/mobile/signin', methods=['POST'])
def user_signin():
    u = Member.query.get(session.get('user_id'))
    u.points += 100
    db.session.commit()
    return jsonify({'code': 200, 'msg': f'签到+100', 'points': u.points})


# --- 优惠券接口 ---
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
    return jsonify({'code': 200, 'msg': '添加成功'})


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
         'limit_level': c.limit_level, 'desc': f"满{float(c.min_spend)}可用" if c.min_spend > 0 else "无门槛"} for c in
        coupons]})


@app.route('/api/mobile/coupon/get', methods=['POST'])
def get_coupon():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '请先登录'})
    sys_coupon_id = request.json.get('id')
    sys_coupon = SystemCoupon.query.get(sys_coupon_id)
    if not sys_coupon: return jsonify({'code': 400, 'msg': '优惠券不存在'})
    if sys_coupon.stock <= 0: return jsonify({'code': 400, 'msg': '手慢了，已抢光'})
    user = Member.query.get(user_id)
    if user.level < sys_coupon.limit_level:
        level_names = {1: '普通会员', 2: '黄金VIP', 3: '钻石VIP'}
        return jsonify({'code': 400, 'msg': f'仅限 {level_names.get(sys_coupon.limit_level)} 领取'})
    if UserCoupon.query.filter_by(user_id=user_id, sys_coupon_id=sys_coupon.id).first():
        return jsonify({'code': 400, 'msg': '您已领取过该券'})
    sys_coupon.stock -= 1
    db.session.add(
        UserCoupon(user_id=user_id, sys_coupon_id=sys_coupon.id, name=sys_coupon.name, amount=sys_coupon.amount,
                   min_spend=sys_coupon.min_spend, status=0))
    db.session.commit()
    return jsonify({'code': 200, 'msg': '领取成功'})


@app.route('/api/mobile/coupon/my', methods=['GET'])
def my_coupons():
    cs = UserCoupon.query.filter_by(user_id=session.get('user_id'), status=0).all()
    return jsonify({'code': 200,
                    'data': [{'id': c.id, 'name': c.name, 'amount': float(c.amount), 'min_spend': float(c.min_spend)}
                             for c in cs]})


@app.route('/api/mobile/vip/upgrade', methods=['POST'])
def upgrade_vip():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '请先登录'})
    target_level = request.json.get('level')
    user = Member.query.get(user_id)
    if user.level >= target_level: return jsonify({'code': 400, 'msg': '您已是该等级或更高等级'})
    user.level = target_level
    db.session.commit()
    return jsonify({'code': 200, 'msg': '升级成功', 'level': user.level})


@app.route('/api/mobile/address', methods=['GET', 'POST'])
def handle_address():
    if request.method == 'GET':
        addrs = Address.query.filter_by(user_id=session.get('user_id')).all()
        return jsonify(
            {'code': 200, 'data': [{'id': a.id, 'name': a.name, 'phone': a.phone, 'detail': a.detail} for a in addrs]})
    db.session.add(Address(user_id=session.get('user_id'), name=request.json['name'], phone=request.json['phone'],
                           detail=request.json['detail']))
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/order', methods=['POST'])
def create_order():
    user_id = session.get('user_id')
    data = request.json
    p = Product.query.get(data.get('product_id'))
    u = Member.query.get(user_id)
    addr = Address.query.get(data.get('address_id'))
    if not addr: return jsonify({'code': 400, 'msg': '请选择地址'})
    if p.stock is not None and p.stock <= 0: return jsonify({'code': 400, 'msg': '该商品已售罄'})

    is_group_item = ('拼团' in p.category) if p.category else False
    is_seckill_item = ('秒杀' in p.category) if p.category else False

    group_action = data.get('group_action')

    discount_cfg = SystemConfig.query.filter_by(key='group_buy_discount').first()
    group_discount = float(discount_cfg.value) if discount_cfg else 0.8

    if is_seckill_item:
        member_discount = 0.9 if u.level == 2 else (0.8 if u.level == 3 else 1)
        base = float(p.price) * member_discount
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
            if team.product_id != p.id: return jsonify({'code': 400, 'msg': '拼团码商品不匹配'})
            team.current_num += 1
            team.status = 1
            team_id = team.id
            order_status = 1
            leader_order = Order.query.filter_by(group_team_id=team.id, status=5).first()
            if leader_order: leader_order.status = 1

    if p.stock is not None:
        p.stock -= 1
    o = Order(order_no=f"ORD{random.randint(1000, 9999)}", user_id=u.id, product_title=p.title, product_img=p.cover_img,
              total_amount=final, status=order_status, address_snapshot=f"{addr.name} {addr.detail}",
              category=p.category, group_team_id=team_id, product_id=p.id)
    db.session.add(o)
    db.session.commit()

    ret_data = {'code': 200, 'msg': '成功', 'balance': float(u.balance), 'points': u.points, 'order_id': o.id}
    if is_group_item and group_action == 'create':
        team = GroupTeam.query.get(team_id)
        ret_data['group_code'] = team.code

    return jsonify(ret_data)


@app.route('/api/mobile/cart/add', methods=['POST'])
def add_cart():
    u = session.get('user_id')
    p = request.json.get('product_id')
    c = Cart.query.filter_by(user_id=u, product_id=p).first()
    if c:
        c.num += 1
    else:
        db.session.add(Cart(user_id=u, product_id=p, num=1))
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/cart/list', methods=['GET'])
def get_cart_list():
    res = db.session.query(Cart, Product).join(Product, Cart.product_id == Product.id).filter(
        Cart.user_id == session.get('user_id')).all()
    # GET 返回 category 和 description
    return jsonify({'code': 200, 'data': [
        {'id': c.id, 'product_id': p.id, 'title': p.title, 'price': float(p.price), 'img': p.cover_img, 'num': c.num,
         'category': p.category, 'description': p.description} for c, p in res]})


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
    if not addr: return jsonify({'code': 400, 'msg': '请选择地址'})

    user = Member.query.get(user_id)
    coupon_id = data.get('coupon_id')
    use_points = data.get('use_points')

    total = 0
    items = []
    for cid in data.get('cart_ids'):
        c = Cart.query.get(cid)
        if c:
            p = Product.query.get(c.product_id)
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
                return jsonify({'code': 400, 'msg': '未满优惠券'})

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

    if user.balance < final: return jsonify({'code': 400, 'msg': '余额不足'})
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
    return jsonify({'code': 200, 'msg': '成功', 'balance': float(user.balance), 'points': user.points})


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
                                          'group_code': team_code}})


@app.route('/api/admin/orders', methods=['GET'])
def admin_get_orders():
    res = db.session.query(Order, Member).join(Member, Order.user_id == Member.id).order_by(Order.id.desc()).all()
    return jsonify({'code': 200, 'data': [
        {'id': o.id, 'no': o.order_no, 'user': m.nickname, 'title': o.product_title, 'img': o.product_img,
         'amount': float(o.total_amount), 'status': o.status, 'date': str(o.created_at)} for o, m in res]})


@app.route('/api/admin/orders/<int:id>/ship', methods=['POST'])
def ship_order(id):
    o = Order.query.get(id)
    o.status = 2
    db.session.commit()
    return jsonify({'code': 200})


@app.route('/api/mobile/orders/<int:id>/cancel', methods=['POST'])
def cancel_order(id):
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '请先登录'})
    o = Order.query.get(id)
    if not o or o.user_id != user_id: return jsonify({'code': 400, 'msg': '订单不存在'})
    if o.status != 1: return jsonify({'code': 400, 'msg': '该订单无法取消'})
    u = Member.query.get(user_id)
    u.balance = float(u.balance) + float(o.total_amount)
    if o.product_id:
        p = Product.query.get(o.product_id)
        if p and p.stock is not None:
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
    if not user_id: return jsonify({'code': 401, 'msg': '请先登录'})
    product_id = request.json.get('product_id')
    f = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
    action = ''
    if f:
        db.session.delete(f)
        action = 'remove'
        msg = '已取消'
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
    return jsonify({'code': 200, 'data': [
        {'id': p.id, 'title': p.title, 'price': float(p.price), 'img': p.cover_img, 'category': p.category,
         'description': p.description} for f, p in res]})


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

    # 基础 KPI
    total_sales = float(db.session.query(func.sum(Order.total_amount)).scalar() or 0)
    total_orders = Order.query.count()
    total_products = Product.query.filter_by(is_on_sale=True).count()
    total_members = Member.query.count()

    # 今日 vs 昨日
    today_sales = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == today).scalar() or 0)
    yest_sales  = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == yesterday).scalar() or 0)
    today_orders = Order.query.filter(func.date(Order.created_at) == today).count()
    yest_orders  = Order.query.filter(func.date(Order.created_at) == yesterday).count()
    today_members = Member.query.filter(func.date(Member.id > 0)).count()  # 占位，下面用注册日期
    new_members_today = 0  # Member 无注册时间字段，以0代替

    # 近 7 天每日数据
    trend_sales, trend_orders, trend_dates = [], [], []
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        s = float(db.session.query(func.sum(Order.total_amount)).filter(func.date(Order.created_at) == d).scalar() or 0)
        c = Order.query.filter(func.date(Order.created_at) == d).count()
        trend_sales.append(round(s, 2))
        trend_orders.append(c)
        trend_dates.append(f'{d.month}/{d.day}')

    # 分类销售额 Top 8
    cat_stats = db.session.query(Order.category, func.sum(Order.total_amount), func.count(Order.id))\
        .group_by(Order.category).order_by(func.sum(Order.total_amount).desc()).limit(8).all()
    category_data = [{'name': c or '其他', 'sales': round(float(a), 2), 'orders': int(n)} for c, a, n in cat_stats if c]

    # 订单状态分布
    status_map = {0: '已取消', 1: '待发货', 2: '运输中', 3: '待评价', 4: '已完成', 5: '拼团中'}
    status_rows = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    status_data = [{'name': status_map.get(s, f'状态{s}'), 'value': int(c)} for s, c in status_rows]

    # 待发货订单数
    pending_ship = Order.query.filter_by(status=1).count()

    # 低库存商品 (库存 < 10)
    low_stock = Product.query.filter(Product.stock < 10, Product.is_on_sale == True).order_by(Product.stock.asc()).limit(5).all()
    low_stock_data = [{'id': p.id, 'title': p.title, 'stock': p.stock, 'img': p.cover_img} for p in low_stock]

    # 热销商品 Top 5
    hot = db.session.query(Order.product_title, Order.product_img, func.count(Order.id).label('cnt'), func.sum(Order.total_amount).label('amt'))\
        .group_by(Order.product_title, Order.product_img).order_by(func.count(Order.id).desc()).limit(5).all()
    hot_data = [{'title': t, 'img': img, 'count': int(c), 'amount': round(float(a), 2)} for t, img, c, a in hot]

    # 会员等级分布
    level_rows = db.session.query(Member.level, func.count(Member.id)).group_by(Member.level).all()
    level_data = [{'name': ['', '普通会员', '黄金VIP', '钻石VIP'][l] if l <= 3 else f'等级{l}', 'value': int(c)} for l, c in level_rows]

    # 评价均分
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
        'chart': [{'name': c or '其他', 'value': round(float(a), 2)} for c, a, n in cat_stats if c]
    }})


@app.route('/api/mobile/recharge', methods=['POST'])
def recharge_balance():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'code': 401, 'msg': '请先登录'})
    try:
        amount = float(request.json.get('amount', 0))
    except:
        return jsonify({'code': 400, 'msg': '金额格式错误'})
    if amount <= 0: return jsonify({'code': 400, 'msg': '金额必须大于0'})
    u = Member.query.get(user_id)
    u.balance = float(u.balance) + amount
    db.session.commit()
    return jsonify({'code': 200, 'msg': '充值成功', 'balance': float(u.balance)})


@app.route('/api/mobile/orders/<int:id>/logistics', methods=['GET'])
def get_order_logistics(id):
    o = Order.query.get(id)
    if not o: return jsonify({'code': 404})
    traces = []
    base_time = o.created_at
    traces.append({'text': '您已提交订单，等待系统确认', 'desc': str(base_time), 'active': False})
    if o.status >= 2:
        ship_time = base_time + timedelta(hours=2)
        traces.append({'text': '商家已发货，包裹正在等待揽收', 'desc': str(ship_time), 'active': False})
        traces.append(
            {'text': '【深圳市】顺丰速运 已收取快件', 'desc': str(ship_time + timedelta(minutes=30)), 'active': False})
        traces.append({'text': '【深圳市】快件离开深圳集散中心，发往目的地', 'desc': str(ship_time + timedelta(hours=4)),
                       'active': True})
    if o.status == 3 or o.status == 4:
        finish_time = base_time + timedelta(days=1)
        traces[-1]['active'] = False
        traces.append({'text': '【您的城市】快递员正在派件，请保持电话畅通', 'desc': str(finish_time - timedelta(hours=2)),
                       'active': False})
        traces.append({'text': '已签收，感谢使用 Smart Mall 购物', 'desc': str(finish_time), 'active': True})
    return jsonify({'code': 200, 'data': sorted(traces, key=lambda x: x['desc'], reverse=True)})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # 自动补充新增字段（create_all 不会给已有表加列）
        with db.engine.connect() as conn:
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)
            product_cols = [c['name'] for c in inspector.get_columns('product')]
            if 'stock' not in product_cols:
                conn.execute(text('ALTER TABLE product ADD COLUMN stock INT DEFAULT 999'))
                conn.commit()
            order_cols = [c['name'] for c in inspector.get_columns('orders')]
            if 'product_id' not in order_cols:
                conn.execute(text('ALTER TABLE orders ADD COLUMN product_id INT NULL'))
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
            db.session.add(SystemConfig(key='group_buy_people', value='2', desc='拼团成团人数'))
            db.session.add(SystemConfig(key='seckill_time_limit', value='5', desc='秒杀限时(分钟)'))
            db.session.add(SystemConfig(key='group_buy_discount', value='0.8', desc='拼团折扣'))
        if SystemCoupon.query.count() == 0:
            db.session.add(SystemCoupon(name='新人礼券', amount=10, min_spend=0, limit_level=1, stock=999))
            db.session.add(SystemCoupon(name='数码神券', amount=100, min_spend=0, limit_level=1, stock=50))
            db.session.add(SystemCoupon(name='黄金专属', amount=50, min_spend=300, limit_level=2, stock=20))
        db.session.commit()
    app.run(host='0.0.0.0', port=5000, debug=True)