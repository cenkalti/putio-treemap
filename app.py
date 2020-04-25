import os

import putiopy
from flask import Flask, request, redirect, url_for

import treemap

app = Flask(__name__)

auth_helper = putiopy.AuthHelper(os.environ['PUTIO_CLIENT_ID'],
                                 os.environ['PUTIO_CLIENT_SECRET'],
                                 os.environ['PUTIO_REDIRECT_URL'])


@app.route('/')
def index():
    return redirect(auth_helper.authentication_url)


@app.route('/callback')
def callback():
    token = auth_helper.get_access_token(request.args['code'])
    return redirect(url_for('get_treemap', token=token))


@app.route('/treemap/<token>')
@app.route('/treemap/<token>/<int:file_id>')
def get_treemap(token: str, file_id: int = 0):
    return treemap.get(token, file_id)
