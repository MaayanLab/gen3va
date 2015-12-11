# This is only for development.
#
# In production, Flask is run by mod_wsgi, which imports the via wsgi.py.


from gen3va import app

app.run(debug=True, port=8084, host='0.0.0.0')
