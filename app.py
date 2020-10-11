import string
from datetime import datetime
from random import choices
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///link.db'
db = SQLAlchemy(app)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(255))
    short_url = db.Column(db.String(4), unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_link()

    def generate_short_link(self):
        characters = string.digits + string.ascii_letters
        short_url = ''.join(choices(characters, k=4))

        link = self.query.filter_by(short_url=short_url).first()

        if link:
            return self.generate_short_link()
        return short_url


@app.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    return redirect(link.original_url)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_link', methods=['POST'])
def add_link():
    posted_data = request.get_json()
    try:
        data = posted_data['original']
        link = Link(original_url=data)
        db.session.add(link)
        db.session.commit()
        return jsonify("Successfully link added, new url:" + str(link.short_url))
    except TypeError:
        original_url = request.form['original_url']
        link = Link(original_url=original_url)
        db.session.add(link)
        db.session.commit()
        return render_template('link_added.html',
                               new_link=link.short_url, original_url=link.original_url)


@app.route("/get_data/<short_url>", methods=["GET"])
def get_link(short_url):
    link = Link.query.filter_by(short_url=short_url).one()
    return jsonify(original_link=link.original_url,
                   short_link=link.short_url,
                   date_created=link.date_created)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
