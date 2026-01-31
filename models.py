from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string

db = SQLAlchemy()

class Flavour(db.Model):
    __tablename__ = 'flavours'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)  
    image_url = db.Column(db.String(500))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    order_items = db.relationship('OrderItem', backref='flavour', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'is_available': self.is_available
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Customer details
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120))
    delivery_address = db.Column(db.Text, nullable=False)
    
    # Order details
    total_amount = db.Column(db.Float, nullable=False)
    order_status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    payment_method = db.Column(db.String(30), default='mpesa')  # mpesa, cash_on_delivery
    
    # For M-Pesa (you'll add this later)
    mpesa_transaction_id = db.Column(db.String(100))
    mpesa_phone = db.Column(db.String(20))
    
    # Notes
    customer_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def generate_order_number(self):
        """Generate unique order number like ORD-20250130-ABC123"""
        date_str = datetime.utcnow().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"ORD-{date_str}-{random_str}"
    
    def to_dict(self, include_items=True):
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'delivery_address': self.delivery_address,
            'total_amount': self.total_amount,
            'order_status': self.order_status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'customer_notes': self.customer_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data 
    
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    flavour_id = db.Column(db.Integer, db.ForeignKey('flavours.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)  # Price when order was made
    
    def to_dict(self):
        return {
            'id': self.id,
            'flavour': self.flavour.to_dict() if self.flavour else None,
            'quantity': self.quantity,
            'price_at_time': self.price_at_time,
            'subtotal': self.quantity * self.price_at_time
        }