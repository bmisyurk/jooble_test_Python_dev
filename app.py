import string
from datetime import datetime, date, time, timedelta
from random import choices
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///link.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
        characters = string.digits + string.ascii_letters
        short_url = ''.join(choices(characters, k=4))
        link = self.query.filter_by(short_url=short_url).first()
        return self.generate_short_link() if link else short_url


@app.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    return redirect(link.original_url)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/link_added', methods=['POST'])
def add_link():
    original_url = request.form['original_url']
    lifetime = request.form['lifetime']
    row = Link(original_url=original_url.strip(), lifetime=lifetime)
    db.session.add(row)
    db.session.commit()
    return render_template('link_added.html',
                           new_link=row.short_url, original_url=row.original_url)



@app.route('/add_link', methods=['POST'])
def add_link_from_api():
    posted_data = request.get_json()
    try:
        if 'original_links' not in posted_data.keys() or not posted_data['original_links']:
            return bad_request("key 'original_links' is empty or not found")
        if check_lifetime(posted_data) is None:
            return bad_request("key 'lifetime' is out of range")
        links = posted_data['original_links'].split(',')
        lifetime = check_lifetime(posted_data)
        cnt_links = len(links)
        if cnt_links > 1:  # multiple addition
            for link in links:
                row = Link(original_url=link.strip(),
                           lifetime=lifetime,
                           date_expire=(datetime.now() + timedelta(days=lifetime)))
                db.session.add(row)
                db.session.commit()
            return jsonify(code=200,
                           log="Successfully added links")
        else:  # single addition
            row = Link(original_url=str(links[0]).strip(),
                       lifetime=lifetime,
                       date_expire=(datetime.now() + timedelta(days=lifetime)))
            db.session.add(row)
            db.session.commit()
            return jsonify(code=200,
                           log="Successfully added link",
                           original_link=row.original_url,
                           new_link=request.host_url + row.short_url,
                           lifetime="%s days" % row.lifetime)
    except Exception as e:
        return bad_request(e)


def check_lifetime(data, num=None):
    if 'lifetime' in data.keys():
        if 0 < int(data['lifetime']) <= 365:
            num = int(data['lifetime'])
        else:
            return num
    else:
        num = 90
    return num


@app.route("/get_data/<short_url>", methods=["GET"])
def get_link_from_api(short_url):
    try:
        row = Link.query.filter_by(short_url=short_url).one()
        return jsonify(original_link=row.original_url,
                       short_link=request.host_url + row.short_url,
                       date_created=row.date_created,
                       date_expire=row.date_expire,
                       lifetime="%s days" % row.lifetime)
    except Exception as e:
        return jsonify(status="Url not found or was expired"), 404


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(status="Method not allowed"), 405


@app.errorhandler(400)
def bad_request(e):
    return jsonify(status="Bad Request", error=str(e)), 400


if __name__ == '__main__':
    app.run(debug=True)
