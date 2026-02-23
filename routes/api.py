from flask import Blueprint, request, jsonify
from models import db, Flavour, Order, OrderItem , Admin
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required 

api = Blueprint('api', __name__)

# ==================== FLAVOUR ROUTES ====================

@api.route('/flavours', methods=['GET'])
def get_flavours():
    """Get all available yogurt flavours"""
    flavours = Flavour.query.filter_by(is_available=True).all()
    return jsonify([flavour.to_dict() for flavour in flavours]), 200

@api.route('/flavours/<int:flavour_id>', methods=['GET'])
def get_flavour(flavour_id):
    """Get a specific flavour by ID"""
    flavour = Flavour.query.get_or_404(flavour_id)
    return jsonify(flavour.to_dict()), 200

# Admin only - add new flavour
@api.route('/flavours', methods=['POST'])
@jwt_required()
def create_flavour():
    """Create a new flavour (admin)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        if 'name' not in data or 'price' not in data:
            return jsonify({'error': 'Missing required fields: name and price'}), 400
        
        new_flavour = Flavour(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            image_url=data.get('image_url'),
            is_available=data.get('is_available', True)
        )
        
        db.session.add(new_flavour)
        db.session.commit()
        
        return jsonify({
            'message': 'Flavour created successfully',
            'flavour': new_flavour.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': f'Flavour "{data["name"]}" already exists'}), 409
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': f'Invalid data type: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin only - update flavour
@api.route('/flavours/<int:flavour_id>', methods=['PUT'])
@jwt_required()
def update_flavour(flavour_id):
    """Update a flavour (admin)"""
    flavour = Flavour.query.get_or_404(flavour_id)
    data = request.get_json()
    
    flavour.name = data.get('name', flavour.name)
    flavour.description = data.get('description', flavour.description)
    flavour.price = data.get('price', flavour.price)
    flavour.image_url = data.get('image_url', flavour.image_url)
    flavour.is_available = data.get('is_available', flavour.is_available)
    
    db.session.commit()
    
    return jsonify(flavour.to_dict()), 200

# Admin only - delete flavour
@api.route('/flavours/<int:flavour_id>', methods=['DELETE'])
@jwt_required()
def delete_flavour(flavour_id):
    """Delete a flavour (admin)"""
    flavour = Flavour.query.get_or_404(flavour_id)
    db.session.delete(flavour)
    db.session.commit()
    
    return jsonify({'message': 'Flavour deleted successfully'}), 200


# ==================== ORDER ROUTES ====================

@api.route('/orders', methods=['POST'])
def create_order():
    """Create a new order (customer facing)"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['customer_name', 'customer_phone', 'delivery_address', 'items']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create order
    order = Order(
        order_number=Order().generate_order_number(),
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        customer_email=data.get('customer_email'),
        delivery_address=data['delivery_address'],
        customer_notes=data.get('customer_notes'),
        payment_method=data.get('payment_method', 'cash_on_delivery'),
        total_amount=0  # We'll calculate this
    )
    
    total = 0
    
    # Add order items
    for item_data in data['items']:
        flavour = Flavour.query.get(item_data['flavour_id'])
        if not flavour:
            return jsonify({'error': f'Flavour {item_data["flavour_id"]} not found'}), 404
        
        if not flavour.is_available:
            return jsonify({'error': f'{flavour.name} is not available'}), 400
        
        quantity = item_data['quantity']
        price = flavour.price
        
        order_item = OrderItem(
            flavour_id=flavour.id,
            quantity=quantity,
            price_at_time=price
        )
        
        order.items.append(order_item)
        total += price * quantity
    
    order.total_amount = total
    
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'message': 'Order created successfully!',
        'order': order.to_dict()
    }), 201

@api.route('/orders/<string:order_number>', methods=['GET'])
def get_order(order_number):
    """Get order details by order number (for customer to track)"""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return jsonify(order.to_dict()), 200

@api.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    """Get all orders (admin only)"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict(include_items=False) for order in orders]), 200

@api.route('/orders/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    """Update order status (admin only)"""
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    
    if 'order_status' in data:
        order.order_status = data['order_status']
    
    if 'payment_status' in data:
        order.payment_status = data['payment_status']
    
    if 'admin_notes' in data:
        order.admin_notes = data['admin_notes']
    
    if 'mpesa_transaction_id' in data:
        order.mpesa_transaction_id = data['mpesa_transaction_id']
    
    order.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(order.to_dict()), 200

@api.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def cancel_order(order_id):
    """Cancel an order"""
    order = Order.query.get_or_404(order_id)
    
    if order.order_status == 'delivered':
        return jsonify({'error': 'Cannot cancel delivered order'}), 400
    
    order.order_status = 'cancelled'
    db.session.commit()
    
    return jsonify({'message': 'Order cancelled successfully'}), 200


# ==================== STATS/DASHBOARD ROUTES (Admin) ====================

@api.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get basic statistics (admin dashboard)"""
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(order_status='pending').count()
    completed_orders = Order.query.filter_by(order_status='delivered').count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
    
    return jsonify({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue
    }), 200

@api.route('/flavours/all', methods=['GET'])
@jwt_required()
def get_all_flavours():
    """Get all flavours including unavailable ones (admin)"""
    flavours = Flavour.query.all()
    return jsonify([flavour.to_dict() for flavour in flavours]), 200


# =====================Admin Login jwt=====================

@api.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400

    admin = Admin.query.filter_by(username=data["username"]).first()

    if not admin or not admin.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=admin.id)

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200