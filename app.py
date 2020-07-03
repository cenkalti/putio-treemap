import os

import putiopy
from flask import Flask, request, redirect, url_for, session

import treemap

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

auth_helper = putiopy.AuthHelper(os.environ['PUTIO_CLIENT_ID'],
                                 os.environ['PUTIO_CLIENT_SECRET'],
                                 os.environ['PUTIO_REDIRECT_URL'])


@app.route('/')
def index():
    if 'token' in session:
        return redirect(url_for('get_treemap'))
    return redirect(auth_helper.authentication_url)


@app.route('/callback')
def callback():
    token = auth_helper.get_access_token(request.args['code'])
    session['token'] = token
    return redirect(url_for('get_treemap'))


@app.route('/logout')
def logout():
    if 'token' in session:
        del session['token']
    return 'Logged out successfully.'


@app.route('/treemap')
def get_treemap():
    token = request.args.get('token', session['token'])
    file_id = request.args.get('id', 0, int)
    try:
        return treemap.get(token, file_id)
    except treemap.ExpiredToken:
        return redirect(auth_helper.authentication_url)
