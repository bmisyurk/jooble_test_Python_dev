from models import Link
from __init__ import app, db
from processing import single_addition, multiple_addition, url_expired

from datetime import datetime, timedelta
from flask import render_template, request, redirect, jsonify


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        lifetime = request.form['lifetime']
        row = Link(original_url=original_url.strip(), lifetime=lifetime)
        db.session.add(row)
        db.session.commit()
        return render_template('link_added.html',
                               new_link=row.short_url, original_url=row.original_url)
    else:
        return render_template('index.html')


@app.route('/add_link', methods=['POST'])
def add_link_from_api():
    posted_data = request.get_json()
    try:
        if 'original_links' not in posted_data.keys() or not posted_data['original_links']:
            return bad_request("key 'original_links' is empty or not found")
        if not 0 < int(posted_data.get('lifetime', 90)) <= 365:
            return bad_request("key 'lifetime' is out of range")
        links = posted_data['original_links'].split(',')
        lifetime = int(posted_data.get('lifetime', 90))
        if len(links) > 1:  # multiple addition links
            return multiple_addition(links, lifetime)
        else:               # single addition link
            return single_addition(links[0], lifetime)
    except Exception as e:
        return bad_request(e)


@app.route('/<string:short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    return redirect(link.original_url) if link.date_expire > datetime.now() else url_expired(link.date_expire)


@app.route('/get_data/<string:short_url>', methods=["GET"])
def get_link_from_api(short_url):
    try:
        row = Link.query.filter_by(short_url=short_url).one()
        return jsonify(original_link=row.original_url,
                       short_link=f'{request.host_url}{row.short_url}',
                       date_created=row.date_created,
                       date_expire=row.date_expire,
                       lifetime=f'{row.lifetime} days')
    except:
        return jsonify(status='Url not found or was expired'), 404


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(status='Method not allowed'), 405


@app.errorhandler(400)
def bad_request(e):
    return jsonify(status='Bad Request', error=str(e)), 400


if __name__ == '__main__':
    app.run(debug=True)
