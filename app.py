import logging
from flask import Flask, render_template
from flask import request
import jinja2

from kcproxy import KCProxy

app = Flask("kcproxy")

my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('./templates'),
])
app.jinja_loader = my_loader

app.config.from_object('config')

logging.basicConfig(level=logging.DEBUG)
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

fileHandler = logging.FileHandler("kcproxy.log")
fileHandler.setFormatter(logFormatter)
logging.getLogger().addHandler(fileHandler)

logger = logging.getLogger("kcproxy")

try:
    import redis
except ImportError:
    app.config["ENABLE_CACHING"] = False

if app.config["ENABLE_CACHING"]:
    our_redis = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["REDIS_DB"]
    )
else:
    # Create a 'fake' redis class, which always returns false, meaning .exists checks never work.
    class FakeRedis:
        def _(*args, **kwargs): return False

        def __getattr__(self, *args, **kwargs): return self._


    our_redis = FakeRedis()

our_proxy = KCProxy(server_ip=app.config["SERVER_IP"], cache=our_redis)
our_proxy.init_app(app)


@app.before_request
def loginfo():
    if 'X-Forwarded-For' in request.headers:
        logger.info("Request IP: {}".format(request.headers["X-Forwarded-For"]))
    else:
        logger.info("Request IP: {}".format(request.remote_addr))


@app.route("/")
def root():
    return render_template("main.htm", api_token=request.args.get("api_token"))


@app.route("/kcs/<path:path>", methods=["GET", "POST"])
def kcs(path):
    logger.debug("Request recieved: /kcs/{}".format(path))

    data = our_proxy.proxy("/kcs/" + path, (request.args, request.form), request.method)

    return data[1], data[0], {"Content-Type": "application/octet-stream",
                              "X-Forwarded-From": app.config["SERVER_IP"] + "/kcs/{}".format(path),
                              "X-Forwarded-By": "KCProxy 1.0 - https://github.com/SunDwarf/KCProxy"}


@app.route("/kcsapi/<path:path>", methods=["GET", "POST"])
def kcsapi(path):
    logger.debug("Request recieved: /kcsapi/{}".format(path))

    if path == "api_start2":
        cache = True
    else:
        cache = False

    data = our_proxy.proxy("/kcsapi/" + path, (request.args, request.form), request.method, cache)

    return data[1], data[0], {"Content-Type": "application/json",
                              "X-Forwarded-From": app.config["SERVER_IP"] + "/kcsapi/{}".format(path),
                              "X-Forwarded-By": "KCProxy 1.0 - https://github.com/SunDwarf/KCProxy"}
