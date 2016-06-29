# This is only for development.
#
# In production, Flask is run by mod_wsgi, which imports the via wsgi.py.


import argparse
from gen3va import app

parser = argparse.ArgumentParser()
parser.add_argument('--port',
                    default=8084,
                    type=int,
                    help='Port for development Flask application.')
args = parser.parse_args()

app.run(debug=True, port=args.port, host='0.0.0.0')
