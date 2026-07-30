from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from config import Config
from database.database import init_db
from database.models import User

# Import Blueprints
from routes.auth import auth_bp
from routes.students import students_bp
from routes.attendance import attendance_bp
from routes.monitoring import monitoring_bp
from routes.analytics import analytics_bp
from routes.reports import reports_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access the classroom monitoring system.'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize Database & Seed Demo Data
init_db(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(students_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(monitoring_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(reports_bp)

# Global Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  REAL-TIME CLASSROOM ATTENTIVENESS & AUTOMATED ATTENDANCE SYSTEM")
    print("  B.E. Artificial Intelligence & Data Science Final Year Project")
    print("="*70)
    print("  * System Server: http://127.0.0.1:5000")
    print("  * Demo Account Credentials: username = admin | password = admin123")
    print("="*70 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
