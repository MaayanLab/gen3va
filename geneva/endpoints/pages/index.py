"""Serves home page and miscellaneous pages.
"""

from flask import Blueprint, render_template

from geneva.config import Config

index_page = Blueprint('base', __name__, url_prefix=Config.BASE_URL)


@index_page.route('/')
def index():
    return render_template('index.html')
