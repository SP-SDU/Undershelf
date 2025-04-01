from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore
import flask_admin
from flask_admin import helpers as admin_helpers
from data.models import db, User, Role, Book
from presentation.views import views, MyModelView, UserView, CustomView
from data.seeding import background_seed  # Updated import path

# Create Flask application
app = Flask(__name__, 
           template_folder='presentation/templates',
           static_folder='presentation/static')
app.config.from_pyfile('config.py')

# Initialize database
db.init_app(app)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Register blueprints
app.register_blueprint(views)

# Initialize database tables
with app.app_context():
    db.create_all()
    if Book.query.count() == 0:
        background_seed(app)

# Create admin interface
admin = flask_admin.Admin(
    app,
    'My Dashboard',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

# Add admin views
admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(CustomView(name="Custom view", endpoint='custom', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))
admin.add_view(MyModelView(Book, db.session, menu_icon_type='fa', menu_icon_value='fa-book', name="Books"))

if __name__ == '__main__':
    app.run(debug=True)
