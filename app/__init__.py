from flask import Flask

def admin_app():
    app_admin = Flask(__name__, template_folder='templates', static_folder='static')
    from .controllers.crime_controllers_admin import admin_dashboard
    admin_dashboard(app_admin)
    return app_admin

def user_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Import and register controllers after app creation
    from .controllers.crime_controllers import register_user_routes
    register_user_routes(app)

    return app

def staff_app():
    """Create and configure the staff Flask app on port 7000."""
    app_staff = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Register staff controllers
    from .controllers.staff_controllers import register_staff_routes
    register_staff_routes(app_staff)
    
    return app_staff
