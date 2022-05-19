# Copyright 2022 Kaiyu Zheng
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
