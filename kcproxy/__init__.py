import os
import flask
import pathlib
import logging
import requests

logger = logging.getLogger("kcproxy")


class KCProxy(object):
    """
    This is the main class for a KCProxy instance. This handles assets and API data.
    """

    def __init__(self, server_ip: int, cache, app: flask.Flask = None):
        """
        Creates a new KCProxy instance.
        :param server_ip:
            The server IP to use. This will be used for every request made to the asset servers.
        :param cache:
            The cache instance to use. This is a `redis.Redis` instance, already connected.
        :param app:
            The flask app object to use.
        """
        self.server_ip = server_ip
        self.cache = cache
        self.app = app

        self.session = requests.Session()

    def init_app(self, app: flask.Flask):
        """
        Late app init.
        :param app: The Flask() instance.
        """
        self.app = app

    def proxy(self, route: str, params: tuple, method: str, cache: bool = True) -> bytes:
        """
        Proxies an asset or API route through, returning bytes.

        This will automatically attempt to load from redis, and from local file if applicable.
        :param route: The route to proxy through.
        :param params: The parameters for the request, e.g api token/version.
        :param cache: Should we cache the request using redis?
        :return: A tuple:
            [0] -> The status code of the request.
            [1] -> The contents of the request.
        """
        path = pathlib.Path(os.path.join(*(p for p in pathlib.Path(route).parts if p != '..')))
        logger.debug("Cleaned path: {}".format(path))

        return self._proxy_internal(path, params, cache, method)

    def _proxy_internal(self, path: pathlib.Path, params: tuple, cache: bool, method: str):
        # First, check the cache if applicable.
        if cache:
            cached_key = str(path) + str(params)  # hacky
            if self.cache.exists(cached_key):
                return 200, self.cache.get(cached_key)
        # Next, follow onto local files.
        new_path = pathlib.Path(self.app.config["STORAGE_LOCATION"] + "/" + str(path))
        logger.debug("Potential file path: " + str(new_path))
        if new_path.exists():
            # Load in.
            return 200, self._load_and_cache(new_path, str(path) + str(params), cache)
        # Otherwise, forward the request to the DMM server.
        return self._dmm_request(path, params, str(path) + str(params), method, cache)

    def _load_and_cache(self, new_path: pathlib.Path, cache_key: str, cache: bool):
        with new_path.open('rb') as f:
            data = f.read()
        if cache:
            self.cache.set(cache_key, data)
            self.cache.expire(cache_key, self.app.config.get("CACHE_TIME", 300))
        return data

    def _dmm_request(self, path: pathlib.Path, params: tuple, cache_key: str, method: str, cache: bool):
        # Create a new request object.
        r = self.session.request(method=method,
                url="http://" + self.app.config["SERVER_IP"] + ("/" if str(path)[0] != "/" else "") + str(path),
                params=params[0].to_dict(flat=True) if params[0] else None,
                data=params[1].to_dict(flat=True) if params[1] else None,
                headers=self._falsify_headers())
        if cache:
            self.cache.set(cache_key, r.content)
            self.cache.expire(cache_key, self.app.config.get("CACHE_TIME", 300))
        return r.status_code, r.content

    def _falsify_headers(self):
        return {
            "Origin": "http://{}".format(self.server_ip),
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80  Safari/537.36",
        }



