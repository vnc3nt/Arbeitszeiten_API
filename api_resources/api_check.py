from flask_restful import Resource

class Apicheck(Resource):
    """Health check endpoint"""
    
    def get(self):
        """Check if API is running"""
        return {
            'status': 'healthy',
            'message': 'API is running'
        }, 200