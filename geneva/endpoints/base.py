"""Serves home page and miscellaneous pages.
"""

from flask import Blueprint, render_template

from geneva.config import Config

base = Blueprint('base', __name__, url_prefix=Config.BASE_URL)


@base.route('/')
def index_page():
    return render_template('index.html')
