from flask import Flask, jsonify, send_file, request, g
from flask_sqlalchemy import SQLAlchemy
import os
from urllib.parse import unquote
# 新增依赖（需安装：pip install bcrypt pyjwt）
import bcrypt
import jwt
import datetime

# ===================== 全局配置（保留原有 + 新增JWT配置） =====================
app = Flask(__name__)
# 核心配置：解决中文乱码、缓存、跨域（原有）
app.config['JSON_AS_ASCII'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用缓存（组件/页面实时更新）
app.config['JSON_SORT_KEYS'] = False  # 保持接口返回字段顺序
# SQLite数据库配置（原有）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yougou.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 新增：JWT密钥（用于token生成/验证）
app.config['SECRET_KEY'] = 'yougou_2025_secret_key'  # 生产环境请修改为随机字符串
app.config['JWT_EXPIRY_HOURS'] = 24  # token有效期24小时
db = SQLAlchemy(app)

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
FRONTEND_ROOT = os.path.join(PROJECT_ROOT, 'frontend')

# 调试打印（确认路径正确）
print(f"项目总目录：{PROJECT_ROOT}")
print(f"前端目录：{FRONTEND_ROOT}")

# ===================== 数据库模型（保留原有，无修改） =====================
# 轮播图表
class Banner(db.Model):
    __tablename__ = 'banner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), default='/assets/image/banner/banner1.png')
    jump_url = db.Column(db.String(255), default='/pages/product/list.html')

# 商品分类表
class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), default='fa-mobile')
    is_show = db.Column(db.Integer, default=1)
    parent_id = db.Column(db.Integer, default=0)

# 商品表
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, default=0.0)
    main_image = db.Column(db.String(255), default='/assets/image/product1.png')
    category_id = db.Column(db.Integer, default=1)
    stock = db.Column(db.Integer, default=100)
    is_recommend = db.Column(db.Integer, default=1)
    is_sale = db.Column(db.Integer, default=1)

# 预留：用户/订单/购物车表（保留原有，无修改）
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
    status = db.Column(db.Integer, default=0)  # 0:待付款 1:待发货 2:待收货 3:已完成

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, default=1)
    product_id = db.Column(db.Integer, default=1)
    quantity = db.Column(db.Integer, default=1)

# 新增：订单项表（订单列表页需要）
class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)

# ===================== 新增：工具函数（不影响原有逻辑） =====================
# 密码加密（适配User模型的password字段）
def encrypt_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# 密码校验
def check_password(plain_pwd, hashed_pwd):
    return bcrypt.checkpw(plain_pwd.encode('utf-8'), hashed_pwd.encode('utf-8'))

# 生成JWT Token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=app.config['JWT_EXPIRY_HOURS'])
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# 验证Token
def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

# 登录验证装饰器（保护需要登录的接口）
def login_required(f):
    def wrapper(*args, **kwargs):
        # 从请求头/参数获取token
        token = request.headers.get('Authorization') or request.args.get('token')
        if not token:
            return jsonify({'code': 401, 'data': {}, 'msg': '请先登录'})
        # 验证token
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'code': 401, 'data': {}, 'msg': '登录已过期，请重新登录'})
        # 存储用户ID到g对象，后续接口可直接使用
        g.user_id = user_id
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# 完善分页逻辑（适配前端分页组件）
def get_pagination_data(query, page, size):
    total = query.count()
    total_pages = (total + size - 1) // size  # 新增：总页数（分页组件需要）
    offset = (page - 1) * size
    items = query.limit(size).offset(offset).all()
    return {
        'list': items,
        'page': page,
        'size': size,
        'total': total,
        'totalPages': total_pages  # 补充分页组件需要的字段
    }

# ===================== 核心：静态资源托管（完全保留原有，无修改） =====================
def get_real_file_path(url_path):
    """
    修复所有路径问题：
    1. 支持 /components/layout/header.html 访问
    2. 支持 /pages/product/list.html 访问
    3. 支持 /assets/css/global.css 访问
    4. 兼容  前缀请求
    """
    # 步骤1：清理URL前缀（移除）
    cleaned_path = url_path.replace('', '').lstrip('/')
    # 步骤2：拼接前端根目录的绝对路径
    real_path = os.path.join(FRONTEND_ROOT, cleaned_path)
    # 步骤3：解码URL（处理中文/特殊字符）
    real_path = unquote(real_path)

    # 情况1：路径是文件（直接返回）
    if os.path.exists(real_path) and os.path.isfile(real_path):
        return real_path
    # 情况2：路径是目录（优先返回index.html，其次list.html）
    elif os.path.isdir(real_path):
        index_path = os.path.join(real_path, 'index.html')
        list_path = os.path.join(real_path, 'list.html')
        if os.path.exists(index_path):
            return index_path
        elif os.path.exists(list_path):
            return list_path
    # 情况3：路径无.html后缀（补充后尝试）
    elif not real_path.endswith('.html'):
        html_path = real_path + '.html'
        if os.path.exists(html_path):
            return html_path
    # 所有情况不匹配 → 返回None
    return None

# 通配所有GET请求（托管前端所有静态资源）
@app.route('/<path:path>', methods=['GET'])
@app.route('/', methods=['GET'])
def serve_frontend(path=''):
    # 根路径 → 直接返回public/index.html
    if path == '':
        file_path = os.path.join(FRONTEND_ROOT, 'public', 'index.html')
    else:
        file_path = get_real_file_path('/' + path)

    # 验证文件是否存在
    if file_path and os.path.exists(file_path):
        # 自动识别文件类型，确保CSS/JS/图片/HTML都能正常返回
        return send_file(file_path)
    else:
        # 调试提示：显示实际查找路径，方便排查
        return f"""
        <h1>404 页面未找到</h1>
        <p>请求路径：{path}</p>
        <p>后端查找路径：{file_path}</p>
        <p>前端根目录：{FRONTEND_ROOT}</p>
        """, 404

# ===================== 接口实现（保留原有 + 扩展） =====================
# 1. 轮播图接口（原有，无修改）
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

# 2. 分类接口（原有，无修改）
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

# 3. 商品列表接口（原有逻辑不变，仅补充分页totalPages字段）
@app.route('/api/product/list', methods=['GET'])
def get_product_list():
    try:
        category_id = request.args.get('category_id', 0, type=int)
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)

        # 构建查询条件（原有）
        query = Product.query.filter_by(is_sale=1)
        if category_id > 0:
            query = query.filter_by(category_id=category_id)

        # 分页查询（优化：使用新增的分页函数，补充totalPages）
        pagination = get_pagination_data(query, page, size)

        # 格式化数据（原有）
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
                'pageSize': pagination['size'],  # 适配前端分页组件的key
                'totalPages': pagination['totalPages']  # 新增：分页组件需要
            },
            'msg': '成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 4. 商品详情接口（原有，无修改）
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

# 5. 扩展：用户登录接口（完善原有预留接口，适配登录页）
@app.route('/api/user/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 参数校验
        if not username or not password:
            return jsonify({'code': 400, 'data': {}, 'msg': '用户名或密码不能为空'})

        # 查询用户（基于原有User模型）
        user = User.query.filter_by(username=username).first()
        if not user or not check_password(password, user.password):
            return jsonify({'code': 401, 'data': {}, 'msg': '用户名或密码错误'})

        # 生成token（适配前端存储token的逻辑）
        token = generate_token(user.id)
        return jsonify({
            'code': 200,
            'data': {'token': token, 'username': user.username},
            'msg': '登录成功'
        })
    except Exception as e:
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 6. 扩展：购物车接口（适配购物车页面）
# 6.1 购物车列表（需登录）
@app.route('/api/cart/list', methods=['GET'])
@login_required
def get_cart_list():
    try:
        # 查询当前用户的购物车
        cart_items = Cart.query.filter_by(user_id=g.user_id).all()
        data = []
        for item in cart_items:
            # 关联商品信息
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

# 6.2 新增/完善：加入购物车（需登录，完善原有预留接口）
@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_cart():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        # 参数校验
        if not product_id:
            return jsonify({'code': 400, 'data': {}, 'msg': '商品ID不能为空'})
        # 检查商品是否存在
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'code': 404, 'data': {}, 'msg': '商品不存在'})

        # 检查是否已在购物车
        cart_item = Cart.query.filter_by(user_id=g.user_id, product_id=product_id).first()
        if cart_item:
            # 已存在则更新数量
            cart_item.quantity += quantity
        else:
            # 不存在则新增
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

# 6.3 新增：更新购物车数量（购物车页面需要）
@app.route('/api/cart/update', methods=['POST'])
@login_required
def update_cart():
    try:
        data = request.get_json()
        cart_id = data.get('id')
        quantity = data.get('quantity', 1)

        if not cart_id:
            return jsonify({'code': 400, 'data': {}, 'msg': '购物车ID不能为空'})

        # 仅允许修改当前用户的购物车
        cart_item = Cart.query.filter_by(id=cart_id, user_id=g.user_id).first()
        if not cart_item:
            return jsonify({'code': 404, 'data': {}, 'msg': '购物车项不存在'})

        # 数量至少为1
        cart_item.quantity = max(1, quantity)
        db.session.commit()
        return jsonify({'code': 200, 'data': {}, 'msg': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# 7. 扩展：订单接口（适配订单列表页）
# 7.1 订单列表（带分页，需登录）
@app.route('/api/order/list', methods=['GET'])
@login_required
def get_order_list():
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 5, type=int)

        # 查询当前用户的订单
        query = Order.query.filter_by(user_id=g.user_id)
        pagination = get_pagination_data(query, page, size)

        # 格式化订单数据（关联订单项）
        data = []
        for order in pagination['list']:
            # 查询订单项
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
            # 订单数据
            data.append({
                'id': order.id,
                'total_price': order.total_price,
                'status': order.status,
                'create_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),  # 简化：实际应存订单创建时间
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

# 7.2 新增：创建订单（订单列表页前置接口）
@app.route('/api/order/create', methods=['POST'])
@login_required
def create_order():
    try:
        data = request.get_json()
        cart_ids = data.get('cart_ids', [])

        if not cart_ids:
            return jsonify({'code': 400, 'data': {}, 'msg': '请选择购物车商品'})

        # 查询选中的购物车项（仅当前用户）
        cart_items = Cart.query.filter(Cart.id.in_(cart_ids), Cart.user_id == g.user_id).all()
        if not cart_items:
            return jsonify({'code': 400, 'data': {}, 'msg': '购物车商品不存在'})

        # 计算总价
        total_price = 0
        order_items = []
        for item in cart_items:
            product = Product.query.get(item.product_id)
            if not product:
                return jsonify({'code': 404, 'data': {}, 'msg': f'商品ID{item.product_id}不存在'})
            # 累加总价
            total_price += product.price * item.quantity
            # 构建订单项
            order_items.append({
                'product_id': product.id,
                'product_name': product.name,
                'product_price': product.price,
                'quantity': item.quantity
            })

        # 创建订单
        order = Order(
            user_id=g.user_id,
            total_price=total_price,
            status=0  # 待付款
        )
        db.session.add(order)
        db.session.flush()  # 获取订单ID

        # 创建订单项
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                product_name=item['product_name'],
                product_price=item['product_price'],
                quantity=item['quantity']
            )
            db.session.add(order_item)

        # 删除已下单的购物车项
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

# 7.3 新增：模拟支付（订单列表页需要）
@app.route('/api/order/pay', methods=['POST'])
@login_required
def pay_order():
    try:
        data = request.get_json()
        order_id = data.get('order_id')

        if not order_id:
            return jsonify({'code': 400, 'data': {}, 'msg': '订单ID不能为空'})

        # 仅允许支付当前用户的待付款订单
        order = Order.query.filter_by(id=order_id, user_id=g.user_id, status=0).first()
        if not order:
            return jsonify({'code': 404, 'data': {}, 'msg': '待付款订单不存在'})

        # 模拟支付成功，更新状态为待发货
        order.status = 1
        db.session.commit()
        return jsonify({'code': 200, 'data': {}, 'msg': '支付成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'data': {}, 'msg': f'失败：{str(e)}'})

# ===================== 初始化 + 启动服务（保留原有 + 新增测试用户） =====================
# ===================== 初始化 + 启动服务（替换原有初始化逻辑） =====================
if __name__ == '__main__':
    # 1. 删除旧数据库（清空原有数据，可选）
    if os.path.exists('yougou.db'):
        os.remove('yougou.db')

    # 2. 初始化数据库 + 插入丰富的测试数据
    with app.app_context():
        db.create_all()

        # ========== 1. 轮播图测试数据 ==========
        if not Banner.query.first():
            banners = [
                Banner(title='iPhone 15 新品上市', image_url='/assets/image/banner/banner1.png', jump_url='/pages/product/list.html?category_id=1'),
                Banner(title='MacBook Pro 限时优惠', image_url='/assets/image/banner/banner2.png', jump_url='/pages/product/list.html?category_id=2'),
                Banner(title='华为Mate60 现货抢购', image_url='/assets/image/banner/banner3.png', jump_url='/pages/product/list.html?category_id=1'),
                Banner(title='平板专区 满减活动', image_url='/assets/image/banner/banner4.png', jump_url='/pages/product/list.html?category_id=3')
            ]
            db.session.add_all(banners)

        # ========== 2. 商品分类测试数据 ==========
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

        # ========== 3. 商品测试数据 ==========
        if not Product.query.first():
            products = [
                # 手机类（category_id=1）
                Product(name='iPhone 15 Pro', price=5999.0, main_image='/assets/image/product/iphone15.png', category_id=1, stock=50, is_recommend=1),
                Product(name='华为Mate60 Pro', price=6999.0, main_image='/assets/image/product/huawei_mate60.png', category_id=1, stock=30, is_recommend=1),
                Product(name='小米14 Ultra', price=4999.0, main_image='/assets/image/product/mi14.png', category_id=1, stock=80, is_recommend=1),
                Product(name='vivo X100 Pro', price=4599.0, main_image='/assets/image/product/vivo_x100.png', category_id=1, stock=60, is_recommend=0),
                # 电脑类（category_id=2）
                Product(name='MacBook Pro 2025', price=9999.0, main_image='/assets/image/product/macbook.png', category_id=2, stock=20, is_recommend=1),
                Product(name='联想拯救者Y9000P', price=8999.0, main_image='/assets/image/product/lenovo_y9000p.png', category_id=2, stock=15, is_recommend=1),
                Product(name='戴尔XPS 13', price=7999.0, main_image='/assets/image/product/dell_xps.png', category_id=2, stock=25, is_recommend=0),
                # 平板类（category_id=3）
                Product(name='iPad Pro 2025', price=7999.0, main_image='/assets/image/product/ipad_pro.png', category_id=3, stock=18, is_recommend=1),
                Product(name='华为MatePad Pro', price=4299.0, main_image='/assets/image/product/huawei_pad.png', category_id=3, stock=40, is_recommend=0),
                # 配件类（category_id=4）
                Product(name='AirPods Pro 2', price=1999.0, main_image='/assets/image/product/airpods.png', category_id=4, stock=100, is_recommend=1),
                Product(name='苹果原装充电器', price=299.0, main_image='/assets/image/product/charger.png', category_id=4, stock=200, is_recommend=0)
            ]
            db.session.add_all(products)

        # ========== 4. 用户测试数据 ==========
        if not User.query.first():
            users = [
                # 测试账号1：test / 123456（管理员/普通用户）
                User(username='test', password=encrypt_password('123456'), phone='13800138000'),
                # 测试账号2：admin / admin123（管理员）
                User(username='admin', password=encrypt_password('admin123'), phone='13900139000'),
                # 测试账号3：user1 / 123456（普通用户）
                User(username='user1', password=encrypt_password('123456'), phone='13700137000')
            ]
            db.session.add_all(users)

        # ========== 5. 购物车测试数据（关联user_id=1（test用户）和商品） ==========
        if not Cart.query.first():
            carts = [
                Cart(user_id=1, product_id=1, quantity=1),  # test用户：iPhone 15 Pro ×1
                Cart(user_id=1, product_id=5, quantity=1),  # test用户：MacBook Pro ×1
                Cart(user_id=1, product_id=10, quantity=2), # test用户：AirPods Pro ×2
                Cart(user_id=3, product_id=2, quantity=1)   # user1用户：华为Mate60 ×1
            ]
            db.session.add_all(carts)

        # ========== 6. 订单测试数据（关联user_id=1） ==========
        if not Order.query.first():
            # 先创建订单主表
            orders = [
                Order(user_id=1, total_price=5999.0, status=0),  # 待付款：iPhone 15 Pro
                Order(user_id=1, total_price=9999.0, status=1),  # 待发货：MacBook Pro
                Order(user_id=1, total_price=1999.0*2, status=2),# 待收货：AirPods Pro ×2
                Order(user_id=1, total_price=6999.0, status=3)   # 已完成：华为Mate60 Pro
            ]
            db.session.add_all(orders)
            db.session.flush()  # 刷新获取订单ID，用于订单项

            # 订单项测试数据（关联订单和商品）
            order_items = [
                # 订单1（id=1）：iPhone 15 Pro ×1
                OrderItem(order_id=1, product_id=1, product_name='iPhone 15 Pro', product_price=5999.0, quantity=1),
                # 订单2（id=2）：MacBook Pro ×1
                OrderItem(order_id=2, product_id=5, product_name='MacBook Pro 2025', product_price=9999.0, quantity=1),
                # 订单3（id=3）：AirPods Pro ×2
                OrderItem(order_id=3, product_id=10, product_name='AirPods Pro 2', product_price=1999.0, quantity=2),
                # 订单4（id=4）：华为Mate60 Pro ×1
                OrderItem(order_id=4, product_id=2, product_name='华为Mate60 Pro', product_price=6999.0, quantity=1)
            ]
            db.session.add_all(order_items)

        # 提交所有数据
        db.session.commit()
        print('✅ 测试数据初始化完成！')
        print('🔑 测试账号1：test / 123456')
        print('🔑 测试账号2：admin / admin123')
        print('🔑 测试账号3：user1 / 123456')

    # 3. 启动服务（原有逻辑不变）
    print('=====================================')
    print('✅ 后端服务启动成功！')
    print('🌐 前端访问：http://localhost:3000')
    print('=====================================')
    app.run(host='0.0.0.0', port=3000, debug=True)