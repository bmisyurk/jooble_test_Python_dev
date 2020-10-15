from models import Link
from __init__ import app, db

from flask import jsonify, request
from datetime import datetime, timedelta


def single_addition(link, lifetime):
    row = Link(original_url=''.join(link.split()),
               lifetime=lifetime,
               date_expire=(datetime.now() + timedelta(days=lifetime)))
    db.session.add(row)
    db.session.commit()
    return jsonify(code=200,
                   log='Successfully added link',
                   original_link=row.original_url,
                   new_link=f'{request.host_url}{row.short_url}',
                   lifetime=f'{row.lifetime} days')


def multiple_addition(links, lifetime):
    for link in links:
        if link.strip():
            row = Link(original_url=''.join(link.split()),
                       lifetime=lifetime,
                       date_expire=(datetime.now() + timedelta(days=lifetime)))
            db.session.add(row)
            db.session.commit()
    return jsonify(code=200,
                   log='Successfully added links')


