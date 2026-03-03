from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Flavour, Order, OrderItem, Admin
from config import Config
from routes.api import api
from flask_jwt_extended import JWTManager
import os


app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)


db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

app.register_blueprint(api, url_prefix='/api')


@app.route('/')
def hello():
    return 'Sunrise Yogurt API is running! 🌅'

# Create tables (for development - migrations are better for production)
with app.app_context():
    db.create_all()
    print("Database tables created!")

# Auto-setup on first run (for production deployment)
with app.app_context():
    db.create_all()
    print("✅ Database tables created!")
    
    # Only create admin if ADMIN_INIT_PASSWORD is set in environment
    admin_init_password = os.environ.get('ADMIN_INIT_PASSWORD')
    
    if admin_init_password and Admin.query.count() == 0:
        print("🔧 Creating admin user from environment variable...")
        admin = Admin(username='admin')
        admin.set_password(admin_init_password)
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin created! Username: admin")
    elif Admin.query.count() == 0:
        print("⚠️  No admin exists! Set ADMIN_INIT_PASSWORD env variable to create one.")
    else:
        print(f"ℹ️  Admin user already exists")
    
    # Seed flavours if database is empty
    if Flavour.query.count() == 0:
        print("🔧 Seeding database with flavours...")
        
        flavours = [
            {'name': 'Strawberry', 'description': 'Sweet and creamy strawberry yogurt', 'price': 150.00, 'is_available': True},
            {'name': 'Lemon', 'description': 'Tangy and refreshing lemon yogurt', 'price': 150.00, 'is_available': True},
            {'name': 'Coconut', 'description': 'Tropical coconut flavored yogurt', 'price': 180.00, 'is_available': True},
            {'name': 'Vanilla', 'description': 'Classic smooth vanilla yogurt', 'price': 140.00, 'is_available': True},
            {'name': 'Mango', 'description': 'Exotic mango flavored yogurt', 'price': 170.00, 'is_available': True},
            {'name': 'Blueberry', 'description': 'Rich and fruity blueberry yogurt', 'price': 160.00, 'is_available': True}
        ]
        
        for flavour_data in flavours:
            flavour = Flavour(**flavour_data)
            db.session.add(flavour)
        
        db.session.commit()
        print(f"✅ Successfully seeded {len(flavours)} flavours!")
    else:
        print(f"ℹ️  Database already has {Flavour.query.count()} flavours")

if __name__ == '__main__':
    app.run(debug=True, port=5555)