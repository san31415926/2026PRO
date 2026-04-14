from sqlalchemy import inspect, text

from extensions import db
from models import Admin, SystemConfig, SystemCoupon


def ensure_schema_updates():
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

        if 'status' not in member_cols:
            conn.execute(text('ALTER TABLE member ADD COLUMN status INT DEFAULT 1'))
            conn.commit()
            conn.execute(text('UPDATE member SET status = 1 WHERE status IS NULL'))
            conn.commit()

        address_cols = [c['name'] for c in inspector.get_columns('address')]
        if 'is_default' not in address_cols:
            conn.execute(text('ALTER TABLE address ADD COLUMN is_default BOOLEAN DEFAULT 0'))
            conn.commit()


def seed_default_data():
    if Admin.query.count() == 0:
        db.session.add(Admin(
            username='admin',
            password='123456',
            nickname='超级管理员',
            avatar='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
        ))

    if not SystemConfig.query.filter_by(key='group_buy_people').first():
        db.session.add(SystemConfig(key='group_buy_people', value='2', desc='拼团成团人数'))
        db.session.add(SystemConfig(key='seckill_time_limit', value='5', desc='秒杀限时(分钟)'))
        db.session.add(SystemConfig(key='group_buy_discount', value='0.8', desc='拼团折扣'))

    if SystemCoupon.query.count() == 0:
        db.session.add(SystemCoupon(name='新人礼券', amount=10, min_spend=0, limit_level=1, stock=999))
        db.session.add(SystemCoupon(name='数码神券', amount=100, min_spend=0, limit_level=1, stock=50))
        db.session.add(SystemCoupon(name='黄金专属', amount=50, min_spend=300, limit_level=2, stock=20))

    db.session.commit()


def initialize_app_data():
    db.create_all()
    ensure_schema_updates()
    seed_default_data()
