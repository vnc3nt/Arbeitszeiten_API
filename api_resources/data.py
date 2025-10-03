from flask import request
from flask_restful import Resource, reqparse
from models import db, data, category, users
from api_resources.auth import token_required
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func

class Data(Resource):
    """Manage time tracking data"""
    
    @token_required
    def get(self, user_id):
        """Get all data for the authenticated user"""
        
        # Get query parameters - aber NICHT required!
        parser = reqparse.RequestParser()
        parser.add_argument('start_date', type=str, required=False, location='args')  # <-- location='args'
        parser.add_argument('end_date', type=str, required=False, location='args')
        parser.add_argument('category_id', type=int, required=False, location='args')
        
        try:
            args = parser.parse_args()
        except Exception as e:
            # Falls Parsing fehlschlägt, ignoriere es und verwende leere args
            args = {'start_date': None, 'end_date': None, 'category_id': None}
        
        # Base query
        query = db.session.query(data).filter(data.userid == user_id)
        
        # Apply filters if provided
        if args['start_date']:
            try:
                start_date = datetime.strptime(args['start_date'], '%Y-%m-%d').date()
                query = query.filter(data.date >= start_date)
            except ValueError:
                return {'message': 'Ungültiges start_date Format. Verwenden Sie YYYY-MM-DD'}, 400
        
        if args['end_date']:
            try:
                end_date = datetime.strptime(args['end_date'], '%Y-%m-%d').date()
                query = query.filter(data.date <= end_date)
            except ValueError:
                return {'message': 'Ungültiges end_date Format. Verwenden Sie YYYY-MM-DD'}, 400
        
        if args['category_id']:
            query = query.filter(data.categoryid == args['category_id'])
        
        # Get data ordered by date
        user_data = query.order_by(data.date.desc()).all()
        
        # Get categories for mapping
        categories = db.session.query(category).filter(category.userid == user_id).all()
        category_map = {cat.id: {'name': cat.name, 'color': cat.color} for cat in categories}
        
        # Format output
        output = []
        for entry in user_data:
            data_entry = {
                'date': entry.date.strftime('%Y-%m-%d'),
                'hours': float(entry.data) if entry.data else None,
                'max_hours': float(entry.maxhours) if entry.maxhours else None
            }
            
            if entry.categoryid and entry.categoryid in category_map:
                data_entry['category'] = {
                    'id': entry.categoryid,
                    'name': category_map[entry.categoryid]['name'],
                    'color': category_map[entry.categoryid]['color']
                }
            
            output.append(data_entry)
        
        return {
            'data': output,
            'total_entries': len(output)
        }, 200
    
    @token_required
    def post(self, user_id):
        """Add or update time tracking data"""
        
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=str, required=True, help='Datum ist erforderlich (Format: YYYY-MM-DD)')
        parser.add_argument('category_id', type=int, required=False)  # ⭐ NICHT MEHR REQUIRED!
        parser.add_argument('hours', type=float, required=True, help='Stunden sind erforderlich')
        parser.add_argument('max_hours', type=float, required=False)
        args = parser.parse_args()
        
        # Parse date
        try:
            entry_date = datetime.strptime(args['date'], '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Ungültiges Datumsformat. Verwenden Sie YYYY-MM-DD'}, 400
        
        # ⭐ NEU: Verify category nur wenn gegeben
        if args['category_id'] is not None:
            user_category = db.session.query(category).filter(
                category.id == args['category_id'],
                category.userid == user_id
            ).first()
            
            if not user_category:
                return {'message': 'Kategorie nicht gefunden oder gehört nicht zum Benutzer'}, 404
        
        # ⭐ NEU: Check if entry exists (mit oder ohne category_id)
        if args['category_id'] is not None:
            existing_entry = db.session.query(data).filter(
                data.userid == user_id,
                data.date == entry_date,
                data.categoryid == args['category_id']
            ).first()
        else:
            existing_entry = db.session.query(data).filter(
                data.userid == user_id,
                data.date == entry_date,
                data.categoryid.is_(None)  # ⭐ Suche explizit nach NULL
            ).first()
        
        if existing_entry:
            # Update existing entry
            existing_entry.data = Decimal(str(args['hours']))
            if args['max_hours'] is not None:
                existing_entry.maxhours = Decimal(str(args['max_hours']))
            message = 'Daten erfolgreich aktualisiert'
        else:
            # Create new entry
            new_entry = data(
                userid=user_id,
                date=entry_date,
                categoryid=args['category_id'],  # ⭐ Kann None sein
                data=Decimal(str(args['hours'])),
                maxhours=Decimal(str(args['max_hours'])) if args['max_hours'] is not None else None
            )
            db.session.add(new_entry)
            message = 'Daten erfolgreich hinzugefügt'
        
        db.session.commit()
        
        return {
            'message': message,
            'date': entry_date.strftime('%Y-%m-%d'),
            'hours': args['hours']
        }, 201 if not existing_entry else 200



class DataByDate(Resource):
    """Manage time tracking data by specific date"""
    
    @token_required
    def get(self, user_id, date):
        """Get all data entries for a specific date"""
        
        try:
            entry_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Ungültiges Datumsformat. Verwenden Sie YYYY-MM-DD'}, 400
        
        # Get all entries for this date
        entries = db.session.query(data).filter(
            data.userid == user_id,
            data.date == entry_date
        ).all()
        
        # Get categories
        categories = db.session.query(category).filter(category.userid == user_id).all()
        category_map = {cat.id: {'name': cat.name, 'color': cat.color} for cat in categories}
        
        output = []
        for entry in entries:
            data_entry = {
                'date': entry.date.strftime('%Y-%m-%d'),
                'hours': float(entry.data) if entry.data else None,
                'max_hours': float(entry.maxhours) if entry.maxhours else None
            }
            
            if entry.categoryid and entry.categoryid in category_map:
                data_entry['category'] = {
                    'id': entry.categoryid,
                    'name': category_map[entry.categoryid]['name'],
                    'color': category_map[entry.categoryid]['color']
                }
            
            output.append(data_entry)
        
        return {
            'date': date,
            'entries': output,
            'total_hours': sum(float(e.data) for e in entries if e.data)
        }, 200
    
    @token_required
    def delete(self, user_id, date):
        """Delete all data entries for a specific date"""
        
        try:
            entry_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Ungültiges Datumsformat. Verwenden Sie YYYY-MM-DD'}, 400
        
        # Delete all entries for this date
        deleted_count = db.session.query(data).filter(
            data.userid == user_id,
            data.date == entry_date
        ).delete()
        
        db.session.commit()
        
        return {
            'message': f'{deleted_count} Einträge gelöscht',
            'date': date
        }, 200
    
    @token_required
    def patch(self, user_id, date):
        """Update hours for a specific date and category"""
        
        parser = reqparse.RequestParser()
        parser.add_argument('category_id', type=int, required=False)  # ⭐ NICHT MEHR REQUIRED!
        parser.add_argument('hours', type=float, required=False)
        parser.add_argument('max_hours', type=float, required=False)
        parser.add_argument('increment', type=float, required=False)
        args = parser.parse_args()
        
        try:
            entry_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Ungültiges Datumsformat. Verwenden Sie YYYY-MM-DD'}, 400
        
        # ⭐ NEU: Wenn category_id gegeben ist, validiere sie
        if args['category_id'] is not None:
            user_category = db.session.query(category).filter(
                category.id == args['category_id'],
                category.userid == user_id
            ).first()
            
            if not user_category:
                return {'message': 'Kategorie nicht gefunden oder gehört nicht zum Benutzer'}, 404
        
        # ⭐ NEU: Finde Eintrag für dieses Datum (OHNE category_id Filter wenn null)
        if args['category_id'] is not None:
            # Suche mit category_id
            entry = db.session.query(data).filter(
                data.userid == user_id,
                data.date == entry_date,
                data.categoryid == args['category_id']
            ).first()
        else:
            # Suche OHNE category_id - nimm den ersten Eintrag für dieses Datum
            entry = db.session.query(data).filter(
                data.userid == user_id,
                data.date == entry_date
            ).first()
        
        # ⭐ NEU: Wenn kein Eintrag existiert, erstelle einen neuen
        if not entry:
            # Berechne die Stunden
            if args['hours'] is not None:
                new_hours = args['hours']
            elif args['increment'] is not None:
                new_hours = max(0, args['increment'])
            else:
                new_hours = 0
            
            # Erstelle neuen Eintrag
            entry = data(
                userid=user_id,
                date=entry_date,
                categoryid=args['category_id'],  # ⭐ Kann None sein!
                data=Decimal(str(new_hours)),
                maxhours=Decimal(str(args['max_hours'])) if args['max_hours'] is not None else None
            )
            db.session.add(entry)
            message = 'Neuer Eintrag erstellt'
        else:
            # Update existierenden Eintrag
            if args['hours'] is not None:
                entry.data = Decimal(str(args['hours']))
            elif args['increment'] is not None:
                current_hours = float(entry.data) if entry.data else 0.0
                new_hours = max(0, current_hours + args['increment'])
                entry.data = Decimal(str(new_hours))
            
            # Update max_hours if provided
            if args['max_hours'] is not None:
                entry.maxhours = Decimal(str(args['max_hours']))
            
            message = 'Eintrag erfolgreich aktualisiert'
        
        db.session.commit()
        
        return {
            'message': message,
            'date': date,
            'hours': float(entry.data) if entry.data else None
        }, 200


