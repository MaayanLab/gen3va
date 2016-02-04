"""Handles logins and logouts.
"""

from flask import Blueprint, request, redirect, render_template, url_for
from flask.ext.login import login_user, logout_user, login_required

from substrate import User
from gen3va.config import Config


auth_pages = Blueprint('auth_pages',
                       __name__,
                       url_prefix=Config.BASE_URL)


@auth_pages.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('pages/login.html')

    username = request.form['username']
    password = request.form['password']

    registered_user = User.get(username, password)
    if registered_user is None:
        logout_user()
        return render_template('pages/login.html',
                               error='Username or password is invalid')

    login_user(registered_user)
    return redirect(url_for('index_page.index'))


@auth_pages.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_pages.login'))
