from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, DateTimeField, TextField
from datetime import datetime

db = SqliteDatabase('ecommerce.db')

class BaseModel(Model):
    class Meta:
        database = db

class Product(BaseModel):
    name = CharField()      
    price = IntegerField() 
    stock = IntegerField()  

class Order(BaseModel):
    customer_name = CharField()
    customer_email = CharField()
    customer_address = TextField()  
    created_at = DateTimeField(default=datetime.now)

class OrderItem(BaseModel):
    order = ForeignKeyField(Order, backref='items')  
    product = ForeignKeyField(Product, backref='order_items') 
    quantity = IntegerField()  
    subtotal = IntegerField() 

db.connect()
db.create_tables([Product, Order, OrderItem], safe=True)

if not Product.select().exists():
    products = [
        {"name": "Laptop", "price": 1000, "stock": 10},
        {"name": "Phone", "price": 500, "stock": 20},
        {"name": "Smartwatch", "price": 200, "stock": 30},
        {"name": "Keyboard", "price": 50, "stock": 50},
        {"name": "Mouse", "price": 30, "stock": 60},
        {"name": "Monitor", "price": 150, "stock": 20},
        {"name": "Printer", "price": 120, "stock": 15},
        {"name": "Desk Lamp", "price": 40, "stock": 35},
        {"name": "USB Flash Drive", "price": 20, "stock": 100},
        {"name": "Router", "price": 60, "stock": 25},
        {"name": "Speakers", "price": 70, "stock": 30},
        {"name": "Webcam", "price": 90, "stock": 10},
        {"name": "Gaming Chair", "price": 250, "stock": 8},
        {"name": "Graphics Card", "price": 400, "stock": 5},
        {"name": "Microphone", "price": 120, "stock": 20},
        {"name": "Projector", "price": 500, "stock": 7},
        {"name": "Desk Organizer", "price": 25, "stock": 50},
        {"name": "External Hard Drive", "price": 80, "stock": 40},
        {"name": "Tablet", "price": 300, "stock": 15},
        {"name": "Headphones", "price": 100, "stock": 25},
    ]
    Product.insert_many(products).execute()