bind = "0.0.0.0:8000"
workers = 4
timeout = 300
worker_class = "gevent"
# Access log - records incoming HTTP requests
accesslog = r"/var/log/gunicorn/access.log"
# Error log - records Gunicorn server goings-on
errorlog = r"/var/log/gunicorn/error.log"
# Whether to send  output to the error log 
capture_output = True
# How verbose the Gunicorn error logs should be 
loglevel = "info"
certfile = "ssl.crt"
keyfile = "ssl.key"