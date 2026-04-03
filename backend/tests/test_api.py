"""
SmartMall 后端单元测试
运行方式：
    cd backend
    venv/Scripts/python -m pytest tests/ -v
"""
import pytest
import sys
import os
import datetime

# 必须在 import app 之前设置，否则 SQLAlchemy 已绑定 MySQL URI
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app as flask_app, db, Member, Product, SystemCoupon, UserCoupon, Address, Order, Admin, SystemConfig


# ─────────────────────────── fixtures ───────────────────────────

@pytest.fixture(scope='function')
def app():
    """每个测试函数使用独立的内存数据库"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key',
    })
    # 强制 SQLAlchemy 用新配置重建引擎（丢弃 MySQL 连接池）
    with flask_app.app_context():
        db.create_all()
        _seed()
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _seed():
    """插入基础测试数据"""
    # 管理员
    db.session.add(Admin(username='admin', password='123456', nickname='管理员'))
    # 普通用户
    u1 = Member(username='user1', password='123456', nickname='测试用户',
                balance=10000.00, points=500, level=1)
    # 黄金VIP 用户
    u2 = Member(username='vip_user', password='123456', nickname='VIP用户',
                balance=10000.00, points=1000, level=2)
    # 商品
    p1 = Product(title='iPhone 15', price=5999.00, cover_img='http://img/1.jpg',
                 category='手机,热卖', description='苹果旗舰手机', is_on_sale=True, stock=100)
    p2 = Product(title='限量秒杀耳机', price=299.00, cover_img='http://img/2.jpg',
                 category='数码,秒杀', description='秒杀专区', is_on_sale=True, stock=5,
                 is_seckill=True, seckill_price=199.00, seckill_stock=5, seckill_limit_per_user=1,
                 seckill_start_at=datetime.datetime.now() - datetime.timedelta(hours=1),
                 seckill_end_at=datetime.datetime.now() + datetime.timedelta(hours=1))
    p3 = Product(title='售罄商品', price=99.00, cover_img='http://img/3.jpg',
                 category='数码', description='库存为0', is_on_sale=True, stock=0)
    p4 = Product(title='拼团手机', price=2999.00, cover_img='http://img/4.jpg',
                 category='手机,拼团', description='拼团商品', is_on_sale=True, stock=50)
    # 优惠券模板
    c1 = SystemCoupon(name='通用满减券', amount=50.00, min_spend=200.00, limit_level=1, stock=100)
    c2 = SystemCoupon(name='VIP专享券', amount=200.00, min_spend=500.00, limit_level=2, stock=20)
    c3 = SystemCoupon(name='已抢光券', amount=10.00, min_spend=0.00, limit_level=1, stock=0)
    # 系统配置
    db.session.add(SystemConfig(key='group_buy_people', value='2'))
    db.session.add(SystemConfig(key='group_buy_discount', value='0.8'))
    db.session.add(SystemConfig(key='seckill_time_limit', value='5'))

    db.session.add_all([u1, u2, p1, p2, p3, p4, c1, c2, c3])
    db.session.commit()


def login(client, username='user1', password='123456'):
    """登录辅助函数，返回响应"""
    return client.post('/api/mobile/login',
                       json={'username': username, 'password': password})


def get_product_id(app, title):
    with app.app_context():
        return Product.query.filter_by(title=title).first().id


def get_member(app, username):
    with app.app_context():
        return Member.query.filter_by(username=username).first()


def get_coupon_id(app, name):
    with app.app_context():
        return SystemCoupon.query.filter_by(name=name).first().id


# ─────────────────────────── 1. 用户注册 / 登录 ───────────────────────────

class TestAuth:
    def test_register_success(self, client):
        """正常注册"""
        r = client.post('/api/mobile/register',
                        json={'username': 'newuser', 'password': 'abc123'})
        assert r.json['code'] == 200

    def test_register_duplicate(self, client):
        """重复用户名注册失败"""
        client.post('/api/mobile/register', json={'username': 'dup', 'password': '123'})
        r = client.post('/api/mobile/register', json={'username': 'dup', 'password': '456'})
        assert r.json['code'] == 400

    def test_login_success(self, client):
        """正确账密登录"""
        r = login(client)
        assert r.json['code'] == 200
        assert r.json['data']['balance'] == 10000.0
        assert r.json['data']['points'] == 500

    def test_login_wrong_password(self, client):
        """错误密码登录失败"""
        r = client.post('/api/mobile/login',
                        json={'username': 'user1', 'password': 'wrong'})
        assert r.json['code'] == 401

    def test_new_user_initial_data(self, client):
        """新注册用户初始余额 10000，积分 500"""
        client.post('/api/mobile/register',
                    json={'username': 'fresh', 'password': '123456'})
        r = client.post('/api/mobile/login',
                        json={'username': 'fresh', 'password': '123456'})
        assert r.json['data']['balance'] == 10000.0
        assert r.json['data']['points'] == 500


# ─────────────────────────── 2. 商品接口 ───────────────────────────

    def test_new_user_receives_newcomer_coupon(self, app, client):
        r = client.post('/api/mobile/register',
                        json={'username': 'coupon_fresh', 'password': '123456'})
        assert r.json['code'] == 200
        assert r.json['newcomer_coupon_received'] is True
        login(client, 'coupon_fresh')
        my_coupon_res = client.get('/api/mobile/coupon/my')
        assert any('新人' in item['name'] for item in my_coupon_res.json['data'])
        with app.app_context():
            newcomer_coupon = SystemCoupon.query.filter(SystemCoupon.name.like('%新人%')).first()
            assert newcomer_coupon.stock == 998


class TestProducts:
    def test_get_products(self, client):
        """获取商品列表"""
        r = client.get('/api/products')
        assert r.json['code'] == 200
        assert len(r.json['data']) >= 4

    def test_product_has_stock_field(self, client):
        """商品列表包含库存字段"""
        r = client.get('/api/products')
        product = r.json['data'][0]
        assert 'stock' in product

    def test_admin_create_product(self, client):
        """管理员新增商品"""
        client.post('/api/admin/login', json={'username': 'admin', 'password': '123456'})
        r = client.post('/api/products', json={
            'title': '新品平板', 'price': 3999.0,
            'category': '数码', 'description': '测试商品', 'stock': 200
        })
        assert r.json['code'] == 200

    def test_admin_toggle_status(self, app, client):
        """管理员上下架商品"""
        pid = get_product_id(app, 'iPhone 15')
        client.post('/api/admin/login', json={'username': 'admin', 'password': '123456'})
        r = client.post(f'/api/products/{pid}/status')
        assert r.json['code'] == 200
        # 再次切换回来
        client.post(f'/api/products/{pid}/status')
        products = client.get('/api/products').json['data']
        iphone = next(p for p in products if p['title'] == 'iPhone 15')
        assert iphone['is_on_sale'] is True

    def test_product_has_seckill_fields(self, client):
        r = client.get('/api/products')
        seckill_item = next(p for p in r.json['data'] if p['title'] == '限量秒杀耳机')
        assert seckill_item['is_seckill'] is True
        assert seckill_item['seckill_status'] == 'active'
        assert seckill_item['seckill_price'] == 199.0


# ─────────────────────────── 3. 购物车 ───────────────────────────

class TestCart:
    def test_add_to_cart(self, app, client):
        """添加商品到购物车"""
        login(client)
        pid = get_product_id(app, 'iPhone 15')
        r = client.post('/api/mobile/cart/add', json={'product_id': pid})
        assert r.json['code'] == 200

    def test_cart_list(self, app, client):
        """购物车列表包含刚加的商品"""
        login(client)
        pid = get_product_id(app, 'iPhone 15')
        client.post('/api/mobile/cart/add', json={'product_id': pid})
        r = client.get('/api/mobile/cart/list')
        assert r.json['code'] == 200
        assert len(r.json['data']) == 1
        assert r.json['data'][0]['title'] == 'iPhone 15'

    def test_add_same_product_increments_quantity(self, app, client):
        """同一商品加购两次，数量变为 2"""
        login(client)
        pid = get_product_id(app, 'iPhone 15')
        client.post('/api/mobile/cart/add', json={'product_id': pid})
        client.post('/api/mobile/cart/add', json={'product_id': pid})
        r = client.get('/api/mobile/cart/list')
        assert r.json['data'][0]['num'] == 2

    def test_seckill_product_cannot_add_to_cart(self, app, client):
        login(client)
        pid = get_product_id(app, '限量秒杀耳机')
        r = client.post('/api/mobile/cart/add', json={'product_id': pid})
        assert r.json['code'] == 400

    def test_delete_cart_item(self, app, client):
        """将购物车数量设为 0 等于删除"""
        login(client)
        pid = get_product_id(app, 'iPhone 15')
        client.post('/api/mobile/cart/add', json={'product_id': pid})
        cart = client.get('/api/mobile/cart/list').json['data']
        client.post('/api/mobile/cart/update', json={'id': cart[0]['id'], 'num': 0})
        r = client.get('/api/mobile/cart/list')
        assert r.json['data'] == []

    def test_cart_requires_login(self, client):
        """未登录无法查看购物车（返回空）"""
        r = client.get('/api/mobile/cart/list')
        assert r.json['code'] == 200
        assert r.json['data'] == []


# ─────────────────────────── 4. 下单核心逻辑 ───────────────────────────

class TestOrder:
    def _prepare_address(self, client):
        """创建地址并返回 id"""
        client.post('/api/mobile/address',
                    json={'name': '张三', 'phone': '13800000000', 'detail': '北京市海淀区'})
        return client.get('/api/mobile/address').json['data'][0]['id']

    def test_create_order_normal(self, app, client):
        """普通用户下单，全价购买"""
        login(client)
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, 'iPhone 15')
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id})
        assert r.json['code'] == 200
        # 余额应扣减 5999
        assert abs(r.json['balance'] - (10000 - 5999)) < 0.01

    def test_create_order_vip_discount(self, app, client):
        """黄金VIP（9折）下单价格正确"""
        login(client, 'vip_user')
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, 'iPhone 15')
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id})
        assert r.json['code'] == 200
        expected = 10000 - 5999 * 0.9
        assert abs(r.json['balance'] - expected) < 0.01

    def test_create_order_deducts_stock(self, app, client):
        """下单后库存减 1"""
        login(client)
        pid = get_product_id(app, 'iPhone 15')
        addr_id = self._prepare_address(client)
        client.post('/api/mobile/order', json={'product_id': pid, 'address_id': addr_id})
        with app.app_context():
            p = Product.query.filter_by(title='iPhone 15').first()
            assert p.stock == 99

    def test_order_sold_out_blocked(self, app, client):
        """库存为 0 的商品无法下单"""
        login(client)
        pid = get_product_id(app, '售罄商品')
        addr_id = self._prepare_address(client)
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id})
        assert r.json['code'] == 400
        assert '售罄' in r.json['msg']

    def test_seckill_order_uses_seckill_price(self, app, client):
        login(client)
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, '限量秒杀耳机')
        r = client.post('/api/mobile/order', json={'product_id': pid, 'address_id': addr_id})
        assert r.json['code'] == 200
        assert abs(r.json['balance'] - (10000 - 199)) < 0.01

    def test_seckill_order_deducts_seckill_stock(self, app, client):
        login(client)
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, '限量秒杀耳机')
        client.post('/api/mobile/order', json={'product_id': pid, 'address_id': addr_id})
        with app.app_context():
            p = Product.query.filter_by(title='限量秒杀耳机').first()
            assert p.seckill_stock == 4

    def test_seckill_order_blocks_coupon_and_points(self, app, client):
        login(client)
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, '限量秒杀耳机')
        coupon_id = get_coupon_id(app, '通用满减券')
        client.post('/api/mobile/coupon/get', json={'id': coupon_id})
        my_coupon_id = client.get('/api/mobile/coupon/my').json['data'][0]['id']
        r = client.post('/api/mobile/order', json={'product_id': pid, 'address_id': addr_id, 'coupon_id': my_coupon_id, 'use_points': True})
        assert r.json['code'] == 400
        assert '秒杀商品不支持优惠券和积分' in r.json['msg']

    def test_seckill_order_limit_per_user(self, app, client):
        login(client)
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, '限量秒杀耳机')
        first = client.post('/api/mobile/order', json={'product_id': pid, 'address_id': addr_id})
        second = client.post('/api/mobile/order', json={'product_id': pid, 'address_id': addr_id})
        assert first.json['code'] == 200
        assert second.json['code'] == 400
        assert '限购' in second.json['msg']

    def test_order_requires_address(self, app, client):
        """未传地址 id 时拒绝下单"""
        login(client)
        pid = get_product_id(app, 'iPhone 15')
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': 99999})
        assert r.json['code'] == 400

    def test_order_use_points(self, app, client):
        """使用积分抵扣，余额消耗更少"""
        login(client)
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, 'iPhone 15')
        # 不使用积分
        r1 = client.post('/api/mobile/order',
                         json={'product_id': pid, 'address_id': addr_id,
                               'use_points': False})
        balance_no_points = r1.json['balance']

        # 重新登录（重置 session），再创建新用户测试使用积分
        client.post('/api/mobile/register',
                    json={'username': 'pointuser', 'password': '123456'})
        login(client, 'pointuser')
        addr_id2 = self._prepare_address(client)
        r2 = client.post('/api/mobile/order',
                         json={'product_id': pid, 'address_id': addr_id2,
                               'use_points': True})
        balance_with_points = r2.json['balance']
        # 使用积分后余额应该更高（花费更少）
        assert balance_with_points >= balance_no_points

    def test_order_insufficient_balance(self, app, client):
        """余额不足时拒绝下单"""
        # 注册一个余额为 0 的用户
        with app.app_context():
            db.session.add(Member(username='broke', password='123456',
                                  nickname='穷用户', balance=0, points=0, level=1))
            db.session.commit()
        login(client, 'broke')
        addr_id = self._prepare_address(client)
        pid = get_product_id(app, 'iPhone 15')
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id})
        assert r.json['code'] == 400
        assert '余额' in r.json['msg']


# ─────────────────────────── 5. 订单取消 ───────────────────────────

class TestCancelOrder:
    def _place_order(self, app, client):
        """下单辅助，返回 order_id"""
        login(client)
        client.post('/api/mobile/address',
                    json={'name': '李四', 'phone': '13900000000', 'detail': '上海'})
        addr_id = client.get('/api/mobile/address').json['data'][0]['id']
        pid = get_product_id(app, 'iPhone 15')
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id})
        return r.json['order_id']

    def test_cancel_order_refunds_balance(self, app, client):
        """取消待发货订单后余额退回"""
        oid = self._place_order(app, client)
        balance_before = client.get('/api/mobile/cart/list')  # 用任意接口拿不到 balance，直接查 DB
        with app.app_context():
            u = Member.query.filter_by(username='user1').first()
            balance_after_order = float(u.balance)

        r = client.post(f'/api/mobile/orders/{oid}/cancel')
        assert r.json['code'] == 200
        assert abs(r.json['balance'] - (balance_after_order + 5999)) < 0.01

    def test_cancel_order_restores_stock(self, app, client):
        """取消订单后库存恢复"""
        oid = self._place_order(app, client)
        with app.app_context():
            stock_after_order = Product.query.filter_by(title='iPhone 15').first().stock
        client.post(f'/api/mobile/orders/{oid}/cancel')
        with app.app_context():
            stock_after_cancel = Product.query.filter_by(title='iPhone 15').first().stock
        assert stock_after_cancel == stock_after_order + 1

    def test_cannot_cancel_shipped_order(self, app, client):
        """已发货订单不能取消"""
        oid = self._place_order(app, client)
        # 模拟管理员发货
        with app.app_context():
            o = Order.query.get(oid)
            o.status = 2
            db.session.commit()
        r = client.post(f'/api/mobile/orders/{oid}/cancel')
        assert r.json['code'] == 400

    def test_cannot_cancel_others_order(self, app, client):
        """用户不能取消别人的订单"""
        oid = self._place_order(app, client)
        # 切换到其他用户
        login(client, 'vip_user')
        r = client.post(f'/api/mobile/orders/{oid}/cancel')
        assert r.json['code'] == 400


# ─────────────────────────── 6. 优惠券 ───────────────────────────

class TestCoupon:
    def test_get_coupon_success(self, app, client):
        """普通用户领取通用券成功"""
        login(client)
        cid = get_coupon_id(app, '通用满减券')
        r = client.post('/api/mobile/coupon/get', json={'id': cid})
        assert r.json['code'] == 200

    def test_get_coupon_deducts_stock(self, app, client):
        """领券后库存 -1"""
        login(client)
        cid = get_coupon_id(app, '通用满减券')
        client.post('/api/mobile/coupon/get', json={'id': cid})
        with app.app_context():
            c = SystemCoupon.query.filter_by(name='通用满减券').first()
            assert c.stock == 99

    def test_cannot_get_coupon_twice(self, app, client):
        """同一优惠券不能重复领取"""
        login(client)
        cid = get_coupon_id(app, '通用满减券')
        client.post('/api/mobile/coupon/get', json={'id': cid})
        r = client.post('/api/mobile/coupon/get', json={'id': cid})
        assert r.json['code'] == 400
        assert '已领取' in r.json['msg']

    def test_vip_coupon_blocked_for_normal_user(self, app, client):
        """普通用户无法领取 VIP 专享券"""
        login(client)  # 普通用户
        cid = get_coupon_id(app, 'VIP专享券')
        r = client.post('/api/mobile/coupon/get', json={'id': cid})
        assert r.json['code'] == 400
        assert 'VIP' in r.json['msg']

    def test_vip_can_get_vip_coupon(self, app, client):
        """黄金VIP 可以领取 VIP 专享券"""
        login(client, 'vip_user')
        cid = get_coupon_id(app, 'VIP专享券')
        r = client.post('/api/mobile/coupon/get', json={'id': cid})
        assert r.json['code'] == 200

    def test_sold_out_coupon_blocked(self, app, client):
        """库存为 0 的券无法领取"""
        login(client)
        cid = get_coupon_id(app, '已抢光券')
        r = client.post('/api/mobile/coupon/get', json={'id': cid})
        assert r.json['code'] == 400

    def test_coupon_applied_at_checkout(self, app, client):
        """下单时使用优惠券，金额正确扣减"""
        login(client)
        cid = get_coupon_id(app, '通用满减券')
        client.post('/api/mobile/coupon/get', json={'id': cid})
        # 拿到用户券 id
        my_coupons = client.get('/api/mobile/coupon/my').json['data']
        uc_id = my_coupons[0]['id']
        # 下单
        client.post('/api/mobile/address',
                    json={'name': '王五', 'phone': '13700000000', 'detail': '广州'})
        addr_id = client.get('/api/mobile/address').json['data'][0]['id']
        pid = get_product_id(app, 'iPhone 15')
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id,
                              'coupon_id': uc_id})
        assert r.json['code'] == 200
        # 余额 = 10000 - (5999 - 50) = 4051
        assert abs(r.json['balance'] - (10000 - 5999 + 50)) < 0.01

    def test_coupon_not_reusable_after_use(self, app, client):
        """优惠券使用后不再出现在我的券列表"""
        login(client)
        cid = get_coupon_id(app, '通用满减券')
        client.post('/api/mobile/coupon/get', json={'id': cid})
        my_coupons = client.get('/api/mobile/coupon/my').json['data']
        uc_id = my_coupons[0]['id']
        client.post('/api/mobile/address',
                    json={'name': '赵六', 'phone': '13600000000', 'detail': '深圳'})
        addr_id = client.get('/api/mobile/address').json['data'][0]['id']
        pid = get_product_id(app, 'iPhone 15')
        client.post('/api/mobile/order',
                    json={'product_id': pid, 'address_id': addr_id, 'coupon_id': uc_id})
        # 再次查看我的券，应为空
        r = client.get('/api/mobile/coupon/my')
        assert r.json['data'] == []


# ─────────────────────────── 7. 库存边界 ───────────────────────────

class TestStock:
    def test_last_item_can_be_bought(self, app, client):
        """库存为 1 时刚好可以购买"""
        with app.app_context():
            Product.query.filter_by(title='限量秒杀耳机').update({'seckill_stock': 1})
            db.session.commit()
        login(client)
        pid = get_product_id(app, '限量秒杀耳机')
        client.post('/api/mobile/address',
                    json={'name': '测试', 'phone': '13500000000', 'detail': '成都'})
        addr_id = client.get('/api/mobile/address').json['data'][0]['id']
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id})
        assert r.json['code'] == 200
        with app.app_context():
            assert Product.query.filter_by(title='限量秒杀耳机').first().seckill_stock == 0

    def test_zero_stock_cannot_be_bought(self, app, client):
        """库存变为 0 后无法再购买"""
        with app.app_context():
            Product.query.filter_by(title='限量秒杀耳机').update({'seckill_stock': 0})
            db.session.commit()
        login(client)
        pid = get_product_id(app, '限量秒杀耳机')
        client.post('/api/mobile/address',
                    json={'name': '测试', 'phone': '13500000000', 'detail': '成都'})
        addr_id = client.get('/api/mobile/address').json['data'][0]['id']
        r = client.post('/api/mobile/order',
                        json={'product_id': pid, 'address_id': addr_id})
        assert r.json['code'] == 400


# ─────────────────────────── 8. 地址管理 ───────────────────────────

class TestAddress:
    def test_add_address(self, client):
        """登录后可添加地址"""
        login(client)
        r = client.post('/api/mobile/address',
                        json={'name': '收件人', 'phone': '13312345678', 'detail': '北京朝阳区'})
        assert r.json['code'] == 200

    def test_first_address_auto_becomes_default(self, client):
        login(client)
        client.post('/api/mobile/address',
                    json={'name': '张三', 'phone': '13312345678', 'detail': '北京朝阳区'})
        r = client.get('/api/mobile/address')
        assert r.json['code'] == 200
        assert len(r.json['data']) == 1
        assert r.json['data'][0]['is_default'] is True

    def test_add_default_address_switches_previous_default(self, client):
        login(client)
        client.post('/api/mobile/address',
                    json={'name': '张三', 'phone': '13312345678', 'detail': '北京朝阳区'})
        client.post('/api/mobile/address',
                    json={'name': '李四', 'phone': '18800000000', 'detail': '上海浦东新区', 'is_default': True})
        r = client.get('/api/mobile/address')
        assert r.json['code'] == 200
        assert r.json['data'][0]['name'] == '李四'
        assert r.json['data'][0]['is_default'] is True
        assert sum(1 for item in r.json['data'] if item['is_default']) == 1

    def test_set_default_address_endpoint(self, client):
        login(client)
        client.post('/api/mobile/address',
                    json={'name': '张三', 'phone': '13312345678', 'detail': '北京朝阳区'})
        client.post('/api/mobile/address',
                    json={'name': '李四', 'phone': '18800000000', 'detail': '上海浦东新区'})
        addr_list = client.get('/api/mobile/address').json['data']
        target_id = next(item['id'] for item in addr_list if item['name'] == '李四')
        set_res = client.post(f'/api/mobile/address/{target_id}/default')
        assert set_res.json['code'] == 200
        refreshed = client.get('/api/mobile/address').json['data']
        target_addr = next(item for item in refreshed if item['id'] == target_id)
        assert target_addr['is_default'] is True
        assert sum(1 for item in refreshed if item['is_default']) == 1

    def test_address_belongs_to_user(self, client):
        """不同用户地址互不可见"""
        login(client, 'user1')
        client.post('/api/mobile/address',
                    json={'name': 'user1地址', 'phone': '111', 'detail': 'A城市'})
        login(client, 'vip_user')
        r = client.get('/api/mobile/address')
        for addr in r.json['data']:
            assert addr['name'] != 'user1地址'


# ─────────────────────────── 9. 管理员接口 ───────────────────────────

class TestAdmin:
    def test_admin_login_success(self, client):
        """管理员正常登录"""
        r = client.post('/api/admin/login',
                        json={'username': 'admin', 'password': '123456'})
        assert r.json['code'] == 200

    def test_admin_login_wrong_password(self, client):
        """管理员密码错误"""
        r = client.post('/api/admin/login',
                        json={'username': 'admin', 'password': 'wrong'})
        assert r.json['code'] == 400

    def test_admin_get_members(self, client):
        """管理员可获取会员列表"""
        client.post('/api/admin/login', json={'username': 'admin', 'password': '123456'})
        r = client.get('/api/admin/members')
        assert r.json['code'] == 200
        assert len(r.json['data']) >= 2

    def test_admin_ship_order(self, app, client):
        """管理员发货"""
        # 用户下单
        login(client, 'user1')
        client.post('/api/mobile/address',
                    json={'name': '收', 'phone': '123', 'detail': '地址'})
        addr_id = client.get('/api/mobile/address').json['data'][0]['id']
        pid = get_product_id(app, 'iPhone 15')
        oid = client.post('/api/mobile/order',
                          json={'product_id': pid, 'address_id': addr_id}).json['order_id']
        # 管理员登录并发货
        client.post('/api/admin/login', json={'username': 'admin', 'password': '123456'})
        r = client.post(f'/api/admin/orders/{oid}/ship', json={'tracking_no': 'SF1234567890'})
        assert r.json['code'] == 200
        with app.app_context():
            assert Order.query.get(oid).status == 2
            assert Order.query.get(oid).tracking_no == 'SF1234567890'

    def test_order_logistics_contains_tracking_no(self, app, client):
        login(client, 'user1')
        client.post('/api/mobile/address',
                    json={'name': '收货人', 'phone': '123', 'detail': '地址'})
        addr_id = client.get('/api/mobile/address').json['data'][0]['id']
        pid = get_product_id(app, 'iPhone 15')
        oid = client.post('/api/mobile/order',
                          json={'product_id': pid, 'address_id': addr_id}).json['order_id']
        client.post('/api/admin/login', json={'username': 'admin', 'password': '123456'})
        client.post(f'/api/admin/orders/{oid}/ship', json={'tracking_no': 'YT0001'})
        r = client.get(f'/api/mobile/orders/{oid}/logistics')
        assert r.json['code'] == 200
        assert any('YT0001' in item['desc'] for item in r.json['data'])
        assert all('time' in item and 'desc' in item for item in r.json['data'])

    def test_admin_recharge_member(self, app, client):
        """管理员给会员充值"""
        client.post('/api/admin/login', json={'username': 'admin', 'password': '123456'})
        with app.app_context():
            uid = Member.query.filter_by(username='user1').first().id
        r = client.post('/api/admin/member/recharge',
                        json={'user_id': uid, 'amount': 500})
        assert r.json['code'] == 200
        with app.app_context():
            u = Member.query.filter_by(username='user1').first()
            assert float(u.balance) == 10500.0
