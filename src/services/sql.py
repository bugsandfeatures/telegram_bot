from src.config import Config
import sqlite3

class DataBase:

    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    async def add_users(self, user_id, name):
        with self.connect:
            return self.cursor.execute("""INSERT INTO users (user_id, name, role) VALUES (?, ?, ?)""",
                                       [user_id, name, 'admin' if user_id == Config.admin_ids else 'user'])

    # async def update_label(self, label, user_id):
    #     with self.connect:
    #         return self.cursor.execute("""UPDATE users SET label=(?) WHERE user_id=(?)""",
    #                                    [label, user_id])
    #
    # async def get_payment_status(self, user_id):
    #     with self.connect:
    #         return self.cursor.execute("""SELECT bought, label FROM users WHERE user_id=(?)""",
    #                                    [user_id]).fetchall()
    #
    # async def update_payment_status(self, user_id):
    #     with self.connect:
    #         return self.cursor.execute("""UPDATE users SET bought=(?) WHERE user_id=(?)""",
    #                                    [True, user_id])

    async def get_products(self):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM products""").fetchall()

    async def get_user_product(self, product_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM products WHERE product_id=(?)""", [product_id]).fetchall()

    async def get_cart(self, user_id):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM cart WHERE user_id=(?)""", [user_id]).fetchall()

    async def add_to_cart(self, user_id, product_id):
        with self.connect:
            return self.cursor.execute("""INSERT INTO cart (user_id, product_id) VALUES (?, ?)""",
                                       [user_id, product_id])

    async def empty_cart(self, user_id):
        with self.connect:
            return self.cursor.execute("""DELETE FROM cart WHERE user_id=(?)""", [user_id])
