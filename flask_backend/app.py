from flask import Flask, jsonify, send_file, request, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os
from urllib.parse import unquote
import bcrypt
import jwt
import datetime

# ===================== 导入外部数据源 =====================
# 警告：此代码依赖外部 product_data.py 文件提供 raw_products 列表
from product_data import raw_products
# ========================================================

# ===================== 全局配置 =====================
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yougou.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'yougou_2025_secret_key'
app.config['JWT_EXPIRY_HOURS'] = 24
db = SQLAlchemy(app)

# 根据您提供的原始代码路径结构进行设置
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FRONTEND_ROOT = os.path.join(PROJECT_ROOT, 'frontend')

# ===================== 数据库模型 =====================
class Banner(db.Model):
    __tablename__ = 'banner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), default='/assets/image/banner/banner1.png')
    jump_url = db.Column(db.String(255), default='/pages/product/list.html')

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), default='fa-mobile')
    is_show = db.Column(db.Integer, default=1)
    parent_id = db.Column(db.Integer, default=0)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, default=0.0)
    main_image = db.Column(db.String(255), default='/assets/image/product1.png') # 对应 raw_products 中的 'image'
    category_id = db.Column(db.Integer, default=1)
    stock = db.Column(db.Integer, default=100)
    is_recommend = db.Column(db.Integer, default=1) # 1: 推荐, 0: 不推荐
    is_sale = db.Column(db.Integer, default=1)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), default='')

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, default=0.0)
    status = db.Column(db.Integer, default=0)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default=1)
    product_id = db.Column(db.Integer, default=1)
    quantity = db.Column(db.Integer, default=1)

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)

# ===================== 工具函数 =====================
def encrypt_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(plain_pwd, hashed_pwd):
    return bcrypt.checkpw(plain_pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRY_HOURS'])
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        # 去掉 'Bearer ' 前缀
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]

        if not token:
            return None

        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def login_required(f):
    def wrapper(*args, **kwargs):
        # 优先从 Authorization header 获取
        token = request.headers.get('Authorization')
        # 其次从 query param 获取 (前端 axios 请求通常不会用)
        if not token:
            token = request.args.get('token')

        if not token:
            return jsonify({'code': 401, 'data': {}, 'msg': '请先登录'})

        user_id = verify_token(token)
        if not user_id:
            return jsonify({'code': 401, 'data': {}, 'msg': '登录已过期，请重新登录'})

        g.user_id = user_id
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def get_pagination_data(query, page, size):
    total = query.count()
    total_pages = (total + size - 1) // size
    offset = (page - 1) * size
    items = query.limit(size).offset(offset).all()
    return {
        'list': items,
        'page': page,
        'size': size,
        'total': total,
        'totalPages': total_pages
    }

# ===================== 静态资源托管 =====================
def get_real_file_path(url_path):
    cleaned_path = url_path.replace('', '').lstrip('/')
    real_path = os.path.join(FRONTEND_ROOT, cleaned_path)
    real_path = unquote(real_path)

    if os.path.exists(real_path) and os.path.isfile(real_path):
        return real_path
    elif os.path.isdir(real_path):
        index_path = os.path.join(real_path, 'index.html')
        list_path = os.path.join(real_path, 'list.html')
        if os.path.exists(index_path):
            return index_path
        elif os.path.exists(list_path):
            return list_path
    elif not real_path.endswith('.html'):
        html_path = real_path + '.html'
        if os.path.exists(html_path):
            return html_path
    return None

@app.route('/<path:path>', methods=['GET'])
@app.route('/', methods=['GET'])
def serve_frontend(path=''):
    if path == '':
        file_path = os.path.join(FRONTEND_ROOT, 'public', 'index.html')
    else:
        file_path = get_real_file_path('/' + path)

    if file_path and os.path.exists(file_path):
        return send_file(file_path)
    else:
        # 404 错误页
        return f"""
        <h1>404 页面未找到</h1>
        <p>请求路径：{path}</p>
        <p>后端查找路径：{file_path}</p>
        <p>前端根目录：{FRONTEND_ROOT}</p>
        """, 404

# ===================== 接口实现 =====================

# 1. 轮播图接口
@app.route('/api/banner/list', methods=['GET'])
def get_banners():
    try:
        banners = Banner.query.order_by(Banner.id).all()
        data = [{
            'id': b.id,
            'title': b.title,
            'image_url': b.image_url,
            'jump_url': b.jump_url
        } for b in banners]
        return jsonify({'code': 200, 'data': data, 'msg': '成功'})
    except Exception as e:
        return jsonify({'code': 500, 'data': [], 'msg': f'失败：{str(e)}'})

# 2. 分类接口
@app.route('/api/category/list', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.filter_by(is_show=1).all()
        data = [{
            'id': c.id,
            'name': c.name,
            'icon': c.icon,
            'parent_id': c.parent_id
        } for c in categories]
        return jsonify({'code': 200, 'data': data, 'msg': '成功'})
    except Exception as e:
        return jsonify({'code': 500, 'data': [], 'msg': f'失败：{str(e)}'})

# 3. 商品列表接口 (已修复和增强)
@app.route('/api/product/list', methods=['GET'])
def get_product_list():
    try:
        # 获取筛选参数
        category_id = request.args.get('category_id', 0, type=int)
        keyword = request.args.get('keyword', type=str)
        is_recommend_param = request.args.get('is_recommend', type=int) # 用于首页热门推荐
        promotion_param = request.args.get('promotion', 0, type=int) # 用于特惠活动/秒杀

        # 默认分页参数，热门推荐使用 5 条，全部商品列表使用 10 条
        default_size = 5 if is_recommend_param == 1 else 10
        page = request.args.get('page', 1, type=int)
        # 前端 list.html 传递的参数名可能是 pageSize 或 size
        size = request.args.get('size', default_size, type=int)

        query = Product.query.filter_by(is_sale=1)

        # 1. 热门推荐筛选 (用于首页)
        if is_recommend_param == 1:
            query = query.filter_by(is_recommend=1)
            # 热门推荐强制 size=5 (如果前端没有传size)
            if 'size' not in request.args:
                size = 5

        # 2. 特惠活动筛选 (用于导航栏跳转)
        elif promotion_param == 1:
            # 假设所有 promotion=1 的商品就是 is_recommend=1 的商品
            query = query.filter_by(is_recommend=1)

            # 3. 普通筛选 (分类和关键词搜索)
        else:
            if category_id > 0:
                query = query.filter_by(category_id=category_id)

            if keyword:
                query = query.filter(or_(Product.name.like(f'%{keyword}%')))

        # 排序
        query = query.order_by(Product.id.desc())

        pagination = get_pagination_data(query, page, size)

        data = [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'main_image': p.main_image,
            'stock': p.stock
        } for p in pagination['list']]

        return jsonify({
            'code': 200,
            'data': {
                'list': data,
                'total': pagination['total'],
                'page': pagination['page'],
                'pageSize': pagination['size'],
                'totalPages': pagination['totalPages']
            },
            'msg': '成功'
        })
    except Exception as e:
        # 返回 500 错误，前端将显示加载失败
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 4. 商品详情接口
@app.route('/api/product/detail', methods=['GET'])
def get_product_detail():
    try:
        product_id = request.args.get('id', 0, type=int)
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'code': 404, 'data': {}, 'msg': '商品不存在'})

        data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'main_image': product.main_image,
            'stock': product.stock,
            'category_id': product.category_id
        }
        return jsonify({'code': 200, 'data': data, 'msg': '成功'})
    except Exception as e:
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 5.1 用户注册接口
@app.route('/api/user/register', methods=['POST'])
def user_register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'code': 400, 'data': {}, 'msg': '用户名或密码不能为空'})

        if User.query.filter_by(username=username).first():
            return jsonify({'code': 409, 'data': {}, 'msg': '用户名已存在'})

        new_user = User(
            username=username,
            password=encrypt_password(password),
            phone=''
        )
        db.session.add(new_user)
        db.session.commit()
        token = generate_token(new_user.id)
        return jsonify({
            'code': 200,
            'data': {'username': username, 'token': token},
            'msg': '注册成功，已自动登录'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 5.2 用户登录接口
@app.route('/api/user/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'code': 400, 'data': {}, 'msg': '用户名或密码不能为空'})

        user = User.query.filter_by(username=username).first()
        if not user or not check_password(password, user.password):
            return jsonify({'code': 401, 'data': {}, 'msg': '用户名或密码错误'})

        token = generate_token(user.id)
        return jsonify({
            'code': 200,
            'data': {'token': token, 'username': user.username},
            'msg': '登录成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 5.3 获取用户信息接口
@app.route('/api/user/info', methods=['GET'])
@login_required
def get_user_info():
    try:
        user = User.query.get(g.user_id)
        if not user:
            return jsonify({'code': 404, 'data': {}, 'msg': '用户不存在'})

        data = {
            'id': user.id,
            'username': user.username,
            'phone': user.phone if user.phone else '未设置'
        }

        return jsonify({
            'code': 200,
            'data': data,
            'msg': '获取成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})


# 5.4 更新用户信息接口
@app.route('/api/user/update', methods=['POST'])
@login_required
def update_user_info():
    try:
        data = request.get_json()
        new_password = data.get('password')
        new_phone = data.get('phone')

        user = User.query.get(g.user_id)
        if not user:
            return jsonify({'code': 404, 'data': {}, 'msg': '用户不存在'})

        has_changed = False

        if new_password:
            if len(new_password) < 6:
                return jsonify({'code': 400, 'data': {}, 'msg': '新密码至少6位'})
            user.password = encrypt_password(new_password)
            has_changed = True

        if new_phone is not None:
            if new_phone and (not new_phone.isdigit() or len(new_phone) not in (10, 11)):
                return jsonify({'code': 400, 'data': {}, 'msg': '手机号格式不正确'})
            user.phone = new_phone
            has_changed = True

        if has_changed:
            db.session.commit()
            if new_password:
                new_token = generate_token(user.id)
                return jsonify({
                    'code': 200,
                    'data': {'token': new_token},
                    'msg': '信息修改成功，密码已更新，请重新登录或使用新Token'
                })
            else:
                return jsonify({'code': 200, 'data': {}, 'msg': '信息修改成功'})
        else:
            return jsonify({'code': 200, 'data': {}, 'msg': '没有检测到信息更新'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})


# 6.1 购物车列表接口
@app.route('/api/cart/list', methods=['GET'])
@login_required
def get_cart_list():
    try:
        cart_items = Cart.query.filter_by(user_id=g.user_id).all()
        data = []
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if product:
                data.append({
                    'id': item.id,
                    'product': {
                        'id': product.id,
                        'name': product.name,
                        'price': product.price,
                        'main_image': product.main_image
                    },
                    'quantity': item.quantity
                })
        return jsonify({'code': 200, 'data': data, 'msg': '成功'})
    except Exception as e:
        return jsonify({'code': 500, 'data': [], 'msg': f'失败：{str(e)}'})

# 6.2 加入购物车接口
@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_cart():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            return jsonify({'code': 400, 'data': {}, 'msg': '商品ID不能为空'})

        product = Product.query.get(product_id)
        if not product:
            return jsonify({'code': 404, 'data': {}, 'msg': '商品不存在'})

        cart_item = Cart.query.filter_by(user_id=g.user_id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = Cart(
                user_id=g.user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        db.session.commit()
        return jsonify({'code': 200, 'data': {}, 'msg': '加入购物车成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 6.3 更新购物车数量接口
@app.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart():
    try:
        data = request.get_json()
        cart_id = data.get('id')
        quantity = data.get('quantity', 1)

        if not cart_id:
            return jsonify({'code': 400, 'data': {}, 'msg': '购物车ID不能为空'})

        cart_item = Cart.query.filter_by(id=cart_id, user_id=g.user_id).first()
        if not cart_item:
            return jsonify({'code': 404, 'data': {}, 'msg': '购物车项不存在'})

        cart_item.quantity = max(1, quantity)
        db.session.commit()
        return jsonify({'code': 200, 'data': {}, 'msg': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 7.1 订单列表接口
@app.route('/api/order/list', methods=['GET'])
@login_required
def get_order_list():
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 5, type=int)

        query = Order.query.filter_by(user_id=g.user_id)
        pagination = get_pagination_data(query, page, size)

        data = []
        for order in pagination['list']:
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            items = []
            for item in order_items:
                product = Product.query.get(item.product_id)
                items.append({
                    'id': item.id,
                    'product': {
                        'id': item.product_id,
                        'name': item.product_name,
                        'price': item.product_price,
                        'main_image': product.main_image if product else ''
                    },
                    'quantity': item.quantity
                })

            data.append({
                'id': order.id,
                'total_price': order.total_price,
                'status': order.status,
                'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                'items': items
            })

        return jsonify({
            'code': 200,
            'data': {
                'list': data,
                'page': pagination['page'],
                'pageSize': pagination['size'],
                'total': pagination['total'],
                'totalPages': pagination['totalPages']
            },
            'msg': '成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 7.2 创建订单接口
@app.route('/api/order/create', methods=['POST'])
@login_required
def create_order():
    try:
        data = request.get_json()
        cart_ids = data.get('cart_ids', [])

        if not cart_ids:
            return jsonify({'code': 400, 'data': {}, 'msg': '请选择购物车商品'})

        cart_items = Cart.query.filter(Cart.id.in_(cart_ids), Cart.user_id == g.user_id).all()
        if not cart_items:
            return jsonify({'code': 400, 'data': {}, 'msg': '购物车商品不存在'})

        total_price = 0
        order_items = []
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if not product:
                return jsonify({'code': 404, 'data': {}, 'msg': f'商品ID{item.product_id}不存在'})

            total_price += product.price * item.quantity

            order_items.append({
                'product_id': product.id,
                'product_name': product.name,
                'product_price': product.price,
                'quantity': item.quantity
            })

        order = Order(
            user_id=g.user_id,
            total_price=total_price,
            status=0
        )
        db.session.add(order)
        db.session.flush()

        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                product_name=item['product_name'],
                product_price=item['product_price'],
                quantity=item['quantity']
            )
            db.session.add(order_item)

        Cart.query.filter(Cart.id.in_(cart_ids)).delete(synchronize_session=False)
        db.session.commit()

        return jsonify({
            'code': 200,
            'data': {'order_id': order.id},
            'msg': '订单创建成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 7.3 模拟支付接口
@app.route('/api/order/pay', methods=['POST'])
@login_required
def pay_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')

        if not order_id:
            return jsonify({'code': 400, 'data': {}, 'msg': '订单ID不能为空'})

        order = Order.query.filter_by(id=order_id, user_id=g.user_id, status=0).first()
        if not order:
            return jsonify({'code': 404, 'data': {}, 'msg': '待付款订单不存在'})

        order.status = 1
        db.session.commit()
        return jsonify({'code': 200, 'data': {}, 'msg': '支付成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# ===================== 初始化 + 启动服务 =====================
if __name__ == '__main__':
    if os.path.exists('yougou.db'):
        os.remove('yougou.db')

    with app.app_context():
        db.create_all()

        if not Banner.query.first():
            banners = [
                Banner(title='iPhone 15 新品上市', image_url='/assets/image/banner/banner1.png', jump_url='/pages/product/list.html?category_id=1'),
                Banner(title='MacBook Pro 限时优惠', image_url='/assets/image/banner/banner2.png', jump_url='/pages/product/list.html?category_id=2'),
                Banner(title='华为Mate60 现货抢购', image_url='/assets/image/banner/banner3.png', jump_url='/pages/product/list.html?category_id=1'),
                Banner(title='平板专区 满减活动', image_url='/assets/image/banner/banner4.png', jump_url='/pages/product/list.html?category_id=3')
            ]
            db.session.add_all(banners)

        if not Category.query.first():
            categories = [
                Category(name='手机', icon='fa-mobile', parent_id=0),
                Category(name='电脑', icon='fa-laptop', parent_id=0),
                Category(name='平板', icon='fa-tablet', parent_id=0),
                Category(name='配件', icon='fa-headphones', parent_id=0),
                Category(name='苹果手机', icon='fa-apple', parent_id=1),
                Category(name='安卓手机', icon='fa-android', parent_id=1)
            ]
            db.session.add_all(categories)

        if not Product.query.first():
            products_to_add = []
            for i, raw_p in enumerate(raw_products):
                p_data = raw_p.copy()
                p_data['main_image'] = p_data.pop('image')
                # 默认前 5 个商品设置为热门推荐
                if i < 5:
                    p_data['is_recommend'] = 1
                else:
                    p_data['is_recommend'] = 0

                products_to_add.append(Product(**p_data))

            db.session.add_all(products_to_add)

        if not User.query.first():
            users = [
                User(username='test', password=encrypt_password('123456'), phone='13800138000'),
                User(username='admin', password=encrypt_password('admin123'), phone='13900139000'),
                User(username='user1', password=encrypt_password('123456'), phone='13700137000')
            ]
            db.session.add_all(users)

        if not Cart.query.first():
            carts = [
                Cart(user_id=1, product_id=1, quantity=1),
                Cart(user_id=1, product_id=5, quantity=1),
                Cart(user_id=1, product_id=10, quantity=2),
                Cart(user_id=3, product_id=2, quantity=1)
            ]
            db.session.add_all(carts)

        if not Order.query.first():
            orders = [
                Order(user_id=1, total_price=5999.0, status=0),
                Order(user_id=1, total_price=9999.0, status=1),
                Order(user_id=1, total_price=1999.0*2, status=2),
                Order(user_id=1, total_price=6999.0, status=3)
            ]
            db.session.add_all(orders)
            db.session.flush()

            order_items = [
                OrderItem(order_id=1, product_id=1, product_name='iPhone 15 Pro', product_price=5999.0, quantity=1),
                OrderItem(order_id=2, product_id=5, product_name='MacBook Pro 2025', product_price=9999.0, quantity=1),
                OrderItem(order_id=3, product_id=10, product_name='AirPods Pro 2', product_price=1999.0, quantity=2),
                OrderItem(order_id=4, product_id=2, product_name='华为Mate60 Pro', product_price=6999.0, quantity=1)
            ]
            db.session.add_all(order_items)

        db.session.commit()
        print('✅ 测试数据初始化完成！')
        print('🔑 测试账号1：test / 123456')
        print('🔑 测试账号2：admin / admin123')
        print('🔑 测试账号3：user1 / 123456')

    print('=====================================')
    print('✅ 后端服务启动成功！')
    print('🌐 前端访问：http://localhost:3000')
    print('=====================================')
    app.run(host='0.0.0.0', port=3000, debug=True)