import datetime

from sqlalchemy import and_, or_


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
    return '拼团' in (product.category or '')


def is_seckill_product(product):
    return bool(getattr(product, 'is_seckill', False) or ('秒杀' in (product.category or '')))


def has_explicit_seckill_config(product):
    return any([
        product.seckill_price is not None,
        product.seckill_start_at is not None,
        product.seckill_end_at is not None,
        int(product.seckill_stock or 0) > 0,
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
    from models import Order

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
