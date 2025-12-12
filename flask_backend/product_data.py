# product_data.py
# 模拟的电商真实数据源

raw_products = [
    # === 手机 (Category ID: 1) ===
    {
        "name": "iPhone 15 Pro Max 256GB 原色钛金属",
        "price": 9999.0,
        "category_id": 1,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 50,
        "image": "/assets/image/product/iphone15.png"
    },
    {
        "name": "华为 Mate 60 Pro+ 16GB+512GB 宣白",
        "price": 8999.0,
        "category_id": 1,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 20,
        "image": "/assets/image/product/huawei_mate60.png"
    },
    {
        "name": "小米 14 Ultra 摄影套装版",
        "price": 6999.0,
        "category_id": 1,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 80,
        "image": "/assets/image/product/mi14.png"
    },
    {
        "name": "Redmi K70 Pro 冠军版",
        "price": 3599.0,
        "category_id": 1,
        "is_recommend": 0,
        "is_sale": 1,
        "stock": 200,
        "image": "/assets/image/product/mi14.png"
    },
    # === 电脑 (Category ID: 2) ===
    {
        "name": "MacBook Pro 14英寸 M3 Max芯片",
        "price": 26999.0,
        "category_id": 2,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 10,
        "image": "/assets/image/product/macbook.png"
    },
    {
        "name": "联想拯救者 Y9000P 2024 i9-14900HX",
        "price": 10999.0,
        "category_id": 2,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 50,
        "image": "/assets/image/product/lenovo_y9000p.png"
    },
    {
        "name": "戴尔 XPS 13 Plus 旗舰轻薄本",
        "price": 15999.0,
        "category_id": 2,
        "is_recommend": 0,
        "is_sale": 1,
        "stock": 15,
        "image": "/assets/image/product/dell_xps.png"
    },
    # === 平板 (Category ID: 3) ===
    {
        "name": "iPad Pro 12.9英寸 M2芯片",
        "price": 9299.0,
        "category_id": 3,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 40,
        "image": "/assets/image/product/ipad_pro.png"
    },
    {
        "name": "华为 MatePad Pro 13.2英寸",
        "price": 5199.0,
        "category_id": 3,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 35,
        "image": "/assets/image/product/huawei_pad.png"
    },
    # === 配件 (Category ID: 4) ===
    {
        "name": "AirPods Pro (第二代) 配MagSafe盒",
        "price": 1899.0,
        "category_id": 4,
        "is_recommend": 1,
        "is_sale": 1,
        "stock": 200,
        "image": "/assets/image/product/airpods.png"
    },
    {
        "name": "Apple 20W USB-C 电源适配器",
        "price": 149.0,
        "category_id": 4,
        "is_recommend": 0,
        "is_sale": 1,
        "stock": 500,
        "image": "/assets/image/product/charger.png"
    },
]