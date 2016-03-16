from redis import Redis
redis = Redis()

import time
from functools import update_wrapper
from flask import request, g
from flask import Flask, jsonify 


class RateLimit(object):
    # give the key an extra 10 seconds to expire
    # in redis, so badly synchronized clocks
    # between workers and the redis server do not cause any problems
    expiration_window = 10
    """
        key_prefix - keeps tracks of the ratelimit for each request
        limit and per - the number of request to allow over a period
        send_x_headers - boolean optoin to inject into each resposnse 
                         header the nubmer of remaining requests a client can make

    """
    def __init__(self, key_prefix, limit, per, send_x_headers):
        # a timestamp to indicate when a request limit can reset
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        # pipeline is used so that you cannot increment
        # without setting the expiration
        p = redis.pipeline()
        p.incr(self.key) # increments key
        p.expireat(self.key, self.reset + self.expiration_window) # expires based on the reset value
        self.current = p.execute()[0]

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current > x.limit)

def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)

def on_over_limit(limit):
    return (jsonify({'data':'You hit the rate limit','error':'429'}),429)

def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator


def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response