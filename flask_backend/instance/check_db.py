import sqlite3
import os

# 1. 锁定数据库位置
# 确保路径指向 flask_backend/instance/yougou.db
db_path = os.path.join( 'yougou.db')

# 如果你在 flask_backend 目录下直接运行，请取消下面这行的注释，并注释掉上面那行
# db_path = os.path.join('instance', 'yougou.db')

print(f"📂 正在读取数据库: {db_path} ...")

if not os.path.exists(db_path):
    print("❌ 错误：找不到数据库文件！请确认路径。")
else:
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # ==================== 1. 查询商品信息 ====================
        print("\n" + "="*20 + " 📦 商品列表 (Product) " + "="*20)
        try:
            # 查询 id, name, price, main_image
            cursor.execute("SELECT id, name, price, main_image FROM product")
            rows = cursor.fetchall()

            if not rows:
                print("⚠️ 商品表为空")
            else:
                print(f"{'ID':<5} | {'价格':<10} | {'图片路径 (main_image)':<35} | {'商品名称'}")
                print("-" * 90)

                for row in rows:
                    p_id, price, main_image, name = row
                    img_display = main_image if main_image else "NULL"
                    # 截断过长的名称以便显示
                    name_display = (name[:15] + '..') if len(name) > 15 else name
                    print(f"{p_id:<5} | {price:<10} | {img_display:<35} | {name_display}")
        except Exception as e:
            print(f"❌ 读取商品表出错: {e}")


        # ==================== 2. 查询用户信息 (新增) ====================
        print("\n" + "="*20 + " 👤 用户列表 (User) " + "="*20)
        try:
            # 查询 id, username, phone, password
            cursor.execute("SELECT id, username, phone, password FROM user")
            user_rows = cursor.fetchall()

            if not user_rows:
                print("⚠️ 用户表为空")
            else:
                print(f"{'ID':<5} | {'用户名':<15} | {'手机号':<15} | {'密码 (加密哈希)'}")
                print("-" * 90)

                for row in user_rows:
                    u_id, username, phone, password = row

                    # 手机号处理：如果是空字符串显示“未设置”
                    phone_display = phone if phone else "未设置"

                    # 密码处理：只显示前20位，后面用...代替（因为哈希很长）
                    pwd_display = (password[:20] + '...') if password else "NULL"

                    print(f"{u_id:<5} | {username:<15} | {phone_display:<15} | {pwd_display}")
        except Exception as e:
            print(f"❌ 读取用户表出错: {e}")

    except Exception as e:
        print(f"❌ 数据库连接出错: {e}")
    finally:
        if conn:
            conn.close()
            print("\n✅ 查询结束，数据库连接已关闭。")