import os
import requests

# 定义图片存放目录 (对应 app.py 中的 FRONTEND_ROOT)
# 假设脚本在项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, 'frontend', 'assets', 'image')

# 确保目录结构存在
DIRS = [
    os.path.join(IMG_DIR, 'banner'),
    os.path.join(IMG_DIR, 'product'),
]

for d in DIRS:
    if not os.path.exists(d):
        os.makedirs(d)
        print(f"创建目录: {d}")

# 定义需要下载的图片映射关系 (文件名 -> 在线图片源)
IMAGES = {
    # 轮播图
    'banner/banner1.png': 'https://placehold.co/800x400/FF4400/white?text=iPhone+15+New',
    'banner/banner2.png': 'https://placehold.co/800x400/333333/white?text=MacBook+Pro',
    'banner/banner3.png': 'https://placehold.co/800x400/007AFF/white?text=Huawei+Mate60',
    'banner/banner4.png': 'https://placehold.co/800x400/4CD964/white?text=Pad+Sale',
    # 商品图 (确保和 product_data.py 中的路径对应)
    'product/iphone15.png': 'https://placehold.co/400x400/eeeeee/333?text=iPhone+15',
    'product/huawei_mate60.png': 'https://placehold.co/400x400/eeeeee/333?text=Mate60+Pro',
    'product/mi14.png': 'https://placehold.co/400x400/eeeeee/333?text=Xiaomi+14',
    'product/macbook.png': 'https://placehold.co/400x400/eeeeee/333?text=MacBook+Pro',
    'product/lenovo_y9000p.png': 'https://placehold.co/400x400/eeeeee/333?text=Lenovo+Y9000P',
    'product/dell_xps.png': 'https://placehold.co/400x400/eeeeee/333?text=Dell+XPS',
    'product/ipad_pro.png': 'https://placehold.co/400x400/eeeeee/333?text=iPad+Pro',
    'product/huawei_pad.png': 'https://placehold.co/400x400/eeeeee/333?text=MatePad',
    'product/airpods.png': 'https://placehold.co/400x400/eeeeee/333?text=AirPods',
    'product/charger.png': 'https://placehold.co/400x400/eeeeee/333?text=Charger',
    'product/vivo_x100.png': 'https://placehold.co/400x400/eeeeee/333?text=Vivo+X100',
    'product/product1.png': 'https://placehold.co/400x400/eeeeee/333?text=Default+Product',
}

def download_image(filename, url):
    filepath = os.path.join(IMG_DIR, filename)
    if os.path.exists(filepath):
        return

    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(res.content)
            print(f"   -> 成功下载: {filename}")
        else:
            print(f"   -> 失败 (Status {res.status_code})")
    except Exception as e:
        print(f"   -> 错误: {e}")

if __name__ == '__main__':
    if not os.path.exists(os.path.join(BASE_DIR, 'frontend')):
        print("❌ 错误：请确保在包含 frontend 目录的项目根目录运行此脚本！")
    else:
        print("=== 开始初始化图片资源 ===")
        for name, url in IMAGES.items():
            download_image(name, url)
        print("=== 图片初始化完成 ===")