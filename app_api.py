import os

from flask import Flask, jsonify
from utils import error_handler
from models.wearer_model import Wearer, db
from utils.error_handler import CustomError
from utils.file_parsing import file_parse

app = Flask(__name__)

ENV = 'prod'
heroku_db = os.environ.get("DATABASE_URL")

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/galaxy4analytics'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = heroku_db.replace('postgres', 'postgresql')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET'])
def index():
    return jsonify('routes: /analytics || /get_data || /insert_data'), 200


@app.route('/insert_data', methods=['POST'])
def post_data():
    """" insert data to postgres DB, data is parsed from local files """
    data = file_parse()

    if not data:
        raise error_handler.data_not_found()

    for datum in data:
        date = str(datum['date'])
        time = str(datum['time'])
        heart_rate = str(datum['heart_rate'])

        data = Wearer(date, time, heart_rate)
        db.session.add(data)

    db.session.commit()

    return jsonify({
        'status': 'data inserted',
    }), 200


@app.route('/get_data', methods=['GET'])
def get_data():
    """ get all data """
    data = Wearer.query.order_by(Wearer.date).all()

    if not data:
        raise error_handler.db_data_not_found()

    return jsonify(str(data)), 200


@app.errorhandler(CustomError)
def handle_bad_request(error):
    """ handle & return the custom errors as json """
    return error.to_jsonified(), error.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)
