from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from models import db
import os

# Import API Resources
from api_resources.auth import AuthRegister, AuthLogin, AuthLogout, AuthUser, AuthChangePassword, AuthChangeUsername, AuthDeleteAccount
from api_resources.data import Data, DataByDate
from api_resources.category import Categories, CategoryById
from api_resources.api_check import Apicheck

# Load environment variables
with open(".env", "r") as f:
    for line in f.readlines():
        if line.strip() and not line.strip().startswith("#"):
            attr, val = line.lstrip().split("=", 1)
            os.environ[attr] = val.rstrip("\n")

# Initialize Flask app
app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{}.{}:{}@{}:{}/{}".format(
    os.environ.get("uname"),
    os.environ.get("db"),
    os.environ.get("password"),
    os.environ.get("host"),
    os.environ.get("port"),
    os.environ.get("scheme")
)

app.config.update(
    BUNDLE_ERRORS=True,
    SECRET_KEY=os.urandom(40),
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Initialize database
db.init_app(app)

# Enable CORS for all routes (iOS app support)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize API
api = Api(app, prefix="/api")

# Register API endpoints
# Authentication
api.add_resource(AuthRegister, "/auth/register")
api.add_resource(AuthLogin, "/auth/login")
api.add_resource(AuthLogout, "/auth/logout")
api.add_resource(AuthUser, "/auth/user")
api.add_resource(AuthChangePassword, "/auth/change-password")
api.add_resource(AuthChangeUsername, "/auth/change-username")
api.add_resource(AuthDeleteAccount, "/auth/delete-account")

# Data management
api.add_resource(Data, "/data")
api.add_resource(DataByDate, "/data/<string:date>")

# Categories
api.add_resource(Categories, "/categories")
api.add_resource(CategoryById, "/categories/<int:category_id>")

# Health check
api.add_resource(Apicheck, "/health")

# Create tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # For local development
    app.run(debug=True, host="0.0.0.0", port=5000)
