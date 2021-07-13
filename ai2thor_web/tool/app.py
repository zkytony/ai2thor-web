import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from datetime import datetime
from .myconfig import *
from .models import db, Session, Admin, add_admin

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()
        add_admin(admin_id=ADMIN_ID,
                  username=ADMIN_USERNAME,
                  password=ADMIN_PASSWORD)

    @app.route('/')
    def landing():
        return render_template("landing.fhtml", title="Welcome")

    from .session_view import sessmgr
    app.register_blueprint(sessmgr)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
