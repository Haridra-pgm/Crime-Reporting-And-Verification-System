from flask import Flask, render_template, request, redirect, url_for, session, flash

def staff_app():
    """Create and configure the staff Flask app on port 7000."""
    app_staff = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Register staff controllers
    from .controllers.staff_controllers import register_staff_routes
    register_staff_routes(app_staff)
    
    return app_staff
