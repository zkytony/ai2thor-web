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

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from .myconfig import ADMIN_ID, ADMIN_USERNAME, ADMIN_PASSWORD

db = SQLAlchemy(session_options={"expire_on_commit":True})

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column(db.DateTime(timezone=True), nullable=False)  # Time this session is added to the database
    start_time = db.Column(db.DateTime(timezone=True))   # Time this session started
    end_time = db.Column(db.DateTime(timezone=True))   # Time this session started
    controller = db.Column(db.String(120), nullable=False)
    assistant = db.Column(db.String(120), nullable=False)
    monitor = db.Column(db.String(120), nullable=False)
    floor_plan = db.Column(db.String(120), nullable=False)
    target_objects = db.Column(db.String(255))  # comma-separated object classes

    def __repr__(self):
        return "<Session {}>".format(self.id)

    @property
    def scene_name(self):
        """Synonym for floor_plan; It could have the format
               FloorPlanXX-<random_seed(int) | default>"""
        return self.floor_plan

    def target_object_types(self):
        """Returns a list of target objects. Order matters."""
        return [target_object.strip()
                for target_object in self.target_objects.split(",")]

    def target_object(self, round_num):
        return self.target_object_types()[round_num]

    @property
    def finished(self):
        return self.end_time is not None


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(120))
    create_time = db.Column(db.DateTime(timezone=True), nullable=False)
    update_time = db.Column(db.DateTime(timezone=True))
    event_waiting = db.Column(db.String(20))
    feedback = db.Column(db.Text)


def add_admin(admin_id=ADMIN_ID,
              username=ADMIN_USERNAME,
              password=ADMIN_PASSWORD):
    if Admin.query.filter_by(id=admin_id).first() is None:
        admin = Admin(id=admin_id,
                      username=username,
                      password=generate_password_hash(password, method="sha256"))
        db.session.add(admin)
        db.session.commit()
