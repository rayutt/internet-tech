import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify
import limit


app = Flask(__name__)

@app.after_request
def inject_headers(response):
	return limit.inject_x_rate_headers(response)

@app.route('/rate-limited')
@limit.ratelimit(limit=2, per=10 * 1)
def index():
    return jsonify({'response':'This is a rate limited response'})

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)