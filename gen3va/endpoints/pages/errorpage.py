"""Error handling.
"""


from flask import Blueprint
from gen3va.config import Config
from gen3va import app
from flask import render_template


error_page = Blueprint('error_page',
                       __name__,
                       url_prefix=Config.BASE_URL)


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('404.html')