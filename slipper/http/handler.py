# coding=utf-8

from flask import Flask


app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    return 'ok'
#
#
# @app.route('/register', methods=['POST'])
# def register():
#     """Just register any contract."""
#
#
# @app.route('/wait', methods=['POST'])
# def wait():
#     """Register contract and wait for result."""