from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Flavour, Order, OrderItem
from config import Config
from routes.api import api
from flask_jwt_extended import JWTManager


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

if __name__ == '__main__':
    app.run(debug=True, port=5555)