from flask import Flask, url_for
from flask_security import Security, SQLAlchemyUserDatastore
import flask_admin
from sqlalchemy import inspect
from extensions import db
from data.models import User, Role
from presentation.views import MyModelView, CustomView, views
from flask_admin import helpers as admin_helpers
from data.seeds import seed

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

# Create admin interface
admin = flask_admin.Admin(
    app,
    'Dashboard Example',
    base_template='my_master.html',
    template_mode='bootstrap3',
)

# Register blueprints
app.register_blueprint(views)

with app.app_context():
    db.create_all()

    # Seed if any table is empty
    if any(db.session.query(db.Model.metadata.tables[table]).count() == 0
           for table in inspect(db.engine).get_table_names()):
        seed(app, user_datastore)

# Add admin model views
admin.add_view(MyModelView(Role, db.session))
admin.add_view(CustomView(User, db.session))


@security.context_processor
def security_context_processor():
    return {
        'admin_base_template': admin.base_template,
        'admin_view': admin.index_view,
        'h': admin_helpers,
        'get_url': url_for
    }


if __name__ == '__main__':
    app.run(debug=True)
