from __init__ import db

import string
from random import choices
from datetime import datetime, timedelta


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(255))
    short_url = db.Column(db.String(4), unique=True)
    lifetime = db.Column(db.Integer, default=90)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_expire = db.Column(db.DateTime, default=datetime.now() + timedelta(days=90))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_link()

    def generate_short_link(self):
        characters = f'{string.digits}{string.ascii_letters}'
        short_url = ''.join(choices(characters, k=4))
        link = self.query.filter_by(short_url=short_url).first()
        return self.generate_short_link() if link else short_url
