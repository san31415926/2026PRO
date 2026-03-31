from app import app, db, Banner, Product, Member


# 使用 Picsum 提供的稳定随机图
def get_random_img(id):
    return f"https://picsum.photos/seed/{id}/400/400"


def get_banner_img(id):
    return f"https://picsum.photos/seed/banner{id}/800/400"


with app.app_context():
    print("正在初始化数据...")

    # 1. 轮播图
    if Banner.query.count() == 0:
        db.session.add(Banner(img=get_banner_img(1), note="数码大促"))
        db.session.add(Banner(img=get_banner_img(2), note="手机狂欢"))
        print("✅ 轮播图已添加")

    # 2. 商品
    if Product.query.count() == 0:
        products = [
            Product(title="iPhone 15 Pro", price=8999, category="手机", cover_img=get_random_img(101)),
            Product(title="MacBook Air", price=9999, category="电脑", cover_img=get_random_img(102)),
            Product(title="Sony 耳机", price=1299, category="数码", cover_img=get_random_img(103)),
            Product(title="小米手环", price=299, category="秒杀", cover_img=get_random_img(104)),
            Product(title="iPad Air", price=4599, category="平板", cover_img=get_random_img(105)),
        ]
        db.session.add_all(products)
        print("✅ 商品已添加")

    db.session.commit()
    print("🎉 初始化完成！")