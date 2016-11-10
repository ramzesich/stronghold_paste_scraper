import requests

from modules.common import Base


class WebRequest(Base):
    def __init__(self, context):
        super().__init__(context)
        self._proxies = {'http': self.context.config.TOR_HTTP_PROXY,
                         'https': self.context.config.TOR_HTTPS_PROXY}

    def get(self, url, json=False):
        self.logger.debug("Requesting %s", url)
        try:
            result = requests.get(url, proxies=self._proxies, timeout=self.context.config.WEB_REQUEST_TIMEOUT)
        except requests.RequestException as e:
            self.logger.error("Error when requesting URL %s: %s", url, e)
            return None
        return result.json() if json else result.text