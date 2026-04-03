import os
import random
import uuid

from flask import jsonify, request, send_from_directory, session

from extensions import db
from models import Admin, Member, SystemConfig, SystemCoupon, UserCoupon


def register_account_routes(app, upload_folder):
    @app.route('/api/common/config', methods=['GET'])
    def get_system_config():
        defaults = {'group_buy_people': '2', 'seckill_time_limit': '5', 'group_buy_discount': '0.8'}
        try:
            configs = SystemConfig.query.all()
            result = defaults.copy()
            for config in configs:
                result[config.key] = config.value
            return jsonify({'code': 200, 'data': result})
        except Exception:
            return jsonify({'code': 200, 'data': defaults})

    @app.route('/api/admin/config', methods=['POST'])
    def update_system_config():
        data = request.json
        for key, value in data.items():
            config = SystemConfig.query.filter_by(key=key).first()
            if not config:
                db.session.add(SystemConfig(key=key, value=str(value)))
            else:
                config.value = str(value)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '配置已更新'})

    @app.route('/api/mobile/profile/update', methods=['POST'])
    def update_profile():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
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
            return jsonify({
                'code': 200,
                'msg': '修改成功',
                'nickname': user.nickname,
                'avatar': user.avatar,
                'hero_text': user.hero_text,
            })
        return jsonify({'code': 400, 'msg': '没有可更新的内容'})

    @app.route('/api/mobile/profile/password', methods=['POST'])
    def update_password():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        user = Member.query.get(user_id)
        data = request.json or {}
        old_password = (data.get('old_password') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        if not old_password or not new_password:
            return jsonify({'code': 400, 'msg': '请填写完整密码信息'})
        if user.password != old_password:
            return jsonify({'code': 400, 'msg': '原密码不正确'})
        if len(new_password) < 6:
            return jsonify({'code': 400, 'msg': '新密码至少 6 位'})
        if new_password == old_password:
            return jsonify({'code': 400, 'msg': '新密码不能与原密码相同'})
        user.password = new_password
        db.session.commit()
        return jsonify({'code': 200, 'msg': '密码修改成功'})

    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'code': 400, 'msg': '未检测到文件'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'code': 400, 'msg': '文件名不能为空'})
        try:
            ext = 'jpg'
            if '.' in file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f'{uuid.uuid4().hex}.{ext}'
            file.save(os.path.join(upload_folder, filename))
            return jsonify({'code': 200, 'url': f'http://localhost:5000/uploads/{filename}'})
        except Exception:
            return jsonify({'code': 500})

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(upload_folder, filename)

    @app.route('/api/admin/login', methods=['POST'])
    def admin_login():
        data = request.json or {}
        username = data.get('username')
        password = data.get('password')
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
            return jsonify({'code': 400, 'msg': '账号不能为空'})
        if len(username) < 3:
            return jsonify({'code': 400, 'msg': '账号至少 3 位'})
        if not password:
            return jsonify({'code': 400, 'msg': '密码不能为空'})
        if len(password) < 6:
            return jsonify({'code': 400, 'msg': '密码至少 6 位'})
        exist = Admin.query.filter_by(username=username).first()
        if exist:
            return jsonify({'code': 400, 'msg': '账号已存在'})
        new_admin = Admin(
            username=username,
            password=password,
            nickname=f'{username}管理员',
            avatar='https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '注册成功'})

    @app.route('/api/mobile/register', methods=['POST'])
    def mobile_register():
        if Member.query.filter_by(username=request.json['username']).first():
            return jsonify({'code': 400, 'msg': '账号已存在'})
        user = Member(
            username=request.json['username'],
            password=request.json['password'],
            nickname=f'用户{random.randint(100, 999)}',
            balance=10000.00,
            points=500,
            hero_text='鸟为什么会飞',
        )
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
                status=0,
            ))
            granted_coupon_name = newcomer_coupon.name

        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '注册成功',
            'newcomer_coupon_received': bool(granted_coupon_name),
            'newcomer_coupon_name': granted_coupon_name,
        })

    @app.route('/api/mobile/login', methods=['POST'])
    def mobile_login():
        user = Member.query.filter_by(
            username=request.json['username'],
            password=request.json['password'],
        ).first()
        if not user:
            return jsonify({'code': 401, 'msg': '错误'})
        session['user_id'] = user.id
        return jsonify({
            'code': 200,
            'data': {
                'id': user.id,
                'nickname': user.nickname,
                'level': user.level,
                'balance': float(user.balance),
                'points': user.points,
                'avatar': user.avatar,
                'hero_text': user.hero_text or '鸟为什么会飞',
            },
        })

    @app.route('/api/mobile/signin', methods=['POST'])
    def user_signin():
        user = Member.query.get(session.get('user_id'))
        user.points += 100
        db.session.commit()
        return jsonify({'code': 200, 'msg': '签到+100', 'points': user.points})

    @app.route('/api/mobile/vip/upgrade', methods=['POST'])
    def upgrade_vip():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        target_level = request.json.get('level')
        user = Member.query.get(user_id)
        if user.level >= target_level:
            return jsonify({'code': 400, 'msg': '您已是该等级或更高等级'})
        user.level = target_level
        db.session.commit()
        return jsonify({'code': 200, 'msg': '升级成功', 'level': user.level})

    @app.route('/api/mobile/recharge', methods=['POST'])
    def recharge_balance():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'msg': '请先登录'})
        try:
            amount = float(request.json.get('amount', 0))
        except Exception:
            return jsonify({'code': 400, 'msg': '金额格式错误'})
        if amount <= 0:
            return jsonify({'code': 400, 'msg': '金额必须大于0'})
        user = Member.query.get(user_id)
        user.balance = float(user.balance) + amount
        db.session.commit()
        return jsonify({'code': 200, 'msg': '充值成功', 'balance': float(user.balance)})
