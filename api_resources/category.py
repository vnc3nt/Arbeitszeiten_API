from flask_restful import Resource, reqparse
from models import db, users, data, category
from api_resources.auth import token_required
from sqlalchemy import func

class Categories(Resource):
    """Manage work categories"""
    
    @token_required
    def get(self, user_id):
        """Get all categories for the authenticated user"""
        
        categories = db.session.query(category).filter(category.userid == user_id).all()
        
        output = [{
            'id': cat.id,
            'name': cat.name,
            'color': cat.color
        } for cat in categories]
        
        return {
            'categories': output,
            'total': len(output)
        }, 200
    
    @token_required
    def post(self, user_id):
        """Create a new category"""
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name ist erforderlich')
        parser.add_argument('color', type=str, required=True, help='Farbe ist erforderlich')
        args = parser.parse_args()
        
        # Check if category name already exists for this user
        existing = db.session.query(category).filter(
            category.userid == user_id,
            category.name == args['name']
        ).first()
        
        if existing:
            return {'message': 'Kategorie mit diesem Namen existiert bereits'}, 409
        
        # Generate new category ID
        max_id = db.session.query(func.max(category.id)).scalar()
        new_id = (max_id or 0) + 1
        
        # Create new category
        new_category = category(
            id=new_id,
            userid=user_id,
            name=args['name'],
            color=args['color']
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        return {
            'message': 'Kategorie erfolgreich erstellt',
            'id': new_id,
            'name': args['name'],
            'color': args['color']
        }, 201


class CategoryById(Resource):
    """Manage individual category by ID"""
    
    @token_required
    def get(self, user_id, category_id):
        """Get a specific category"""
        
        cat = db.session.query(category).filter(
            category.id == category_id,
            category.userid == user_id
        ).first()
        
        if not cat:
            return {'message': 'Kategorie nicht gefunden'}, 404
        
        return {
            'id': cat.id,
            'name': cat.name,
            'color': cat.color
        }, 200
    
    @token_required
    def put(self, user_id, category_id):
        """Update a category"""
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name ist erforderlich')
        parser.add_argument('color', type=str, required=True, help='Farbe ist erforderlich')
        args = parser.parse_args()
        
        # Find category
        cat = db.session.query(category).filter(
            category.id == category_id,
            category.userid == user_id
        ).first()
        
        if not cat:
            return {'message': 'Kategorie nicht gefunden'}, 404
        
        # Check if new name conflicts with another category
        if args['name'] != cat.name:
            existing = db.session.query(category).filter(
                category.userid == user_id,
                category.name == args['name'],
                category.id != category_id
            ).first()
            
            if existing:
                return {'message': 'Kategorie mit diesem Namen existiert bereits'}, 409
        
        # Update category
        cat.name = args['name']
        cat.color = args['color']
        
        db.session.commit()
        
        return {
            'message': 'Kategorie erfolgreich aktualisiert',
            'id': cat.id,
            'name': cat.name,
            'color': cat.color
        }, 200
    
    @token_required
    def delete(self, user_id, category_id):
        """Delete a category and all associated data"""
        
        # Find category
        cat = db.session.query(category).filter(
            category.id == category_id,
            category.userid == user_id
        ).first()
        
        if not cat:
            return {'message': 'Kategorie nicht gefunden'}, 404
        
        # Delete all data entries associated with this category
        data_count = db.session.query(data).filter(
            data.userid == user_id,
            data.categoryid == category_id
        ).delete()
        
        # Delete category
        db.session.delete(cat)
        db.session.commit()
        
        return {
            'message': 'Kategorie erfolgreich gelöscht',
            'deleted_data_entries': data_count
        }, 200
