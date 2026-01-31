from app import app
from models import db, Flavour

def seed_flavours():
    """Add sample yogurt flavours to the database"""
    
    flavours = [
        {
            'name': 'Strawberry',
            'description': 'Sweet and creamy strawberry yogurt',
            'price': 150.00,
            'is_available': True
        },
        {
            'name': 'Lemon',
            'description': 'Tangy and refreshing lemon yogurt',
            'price': 150.00,
            'is_available': True
        },
        {
            'name': 'Coconut',
            'description': 'Tropical coconut flavored yogurt',
            'price': 180.00,
            'is_available': True
        },
        {
            'name': 'Vanilla',
            'description': 'Classic smooth vanilla yogurt',
            'price': 140.00,
            'is_available': True
        },
        {
            'name': 'Mango',
            'description': 'Exotic mango flavored yogurt',
            'price': 170.00,
            'is_available': True
        },
        {
            'name': 'Blueberry',
            'description': 'Rich and fruity blueberry yogurt',
            'price': 160.00,
            'is_available': True
        }
    ]
    
    with app.app_context():
        # Clear existing flavours (optional - only for development)
        Flavour.query.delete()
        
        # Add new flavours
        for flavour_data in flavours:
            flavour = Flavour(**flavour_data)
            db.session.add(flavour)
        
        db.session.commit()
        print(f"✅ Successfully added {len(flavours)} flavours!")

if __name__ == '__main__':
    seed_flavours()