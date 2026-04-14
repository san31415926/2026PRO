import os

from flask import Flask, make_response, request

from bootstrap import initialize_app_data
from extensions import db
from models import (
    Admin,
    Address,
    Banner,
    Cart,
    Comment,
    Favorite,
    GroupTeam,
    Member,
    Order,
    Product,
    SystemConfig,
    SystemCoupon,
    UserCoupon,
)
from routes.account_routes import register_account_routes
from routes.admin_routes import register_admin_routes
from routes.coupon_routes import register_coupon_routes
from routes.member_routes import register_member_routes
from routes.order_routes import register_order_routes
from routes.product_routes import register_product_routes

# --- 1. 应用配置 ---
app = Flask(__name__)
app.secret_key = 'panweiyu_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'mysql+pymysql://root:panweiyu123@localhost/smart_mall'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

db.init_app(app)
register_account_routes(app, UPLOAD_FOLDER)
register_admin_routes(app)
register_coupon_routes(app)
register_member_routes(app)
register_order_routes(app)
register_product_routes(app)


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


if __name__ == '__main__':
    with app.app_context():
        initialize_app_data()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
