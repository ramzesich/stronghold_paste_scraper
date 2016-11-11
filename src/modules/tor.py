import requests
import time

from modules.common import Base


class WebRequest(Base):
    def __init__(self, context):
        super().__init__(context)
        self._proxies = {'http': 'socks5://{}:{}'.format(self.context.config.TOR_HOSTNAME, self.context.config.TOR_HTTP_PROXY_PORT),
                         'https': 'socks5://{}:{}'.format(self.context.config.TOR_HOSTNAME, self.context.config.TOR_HTTPS_PROXY_PORT)}

    def get(self, url, json=False):
        self.logger.debug("Requesting %s", url)
        for attempt in range(self.context.config.WEB_MAX_RETRIES + 1):
            try:
                self.logger.debug("Attempt #%s", attempt)
                result = requests.get(url, proxies=self._proxies, timeout=self.context.config.WEB_REQUEST_TIMEOUT)
            except requests.RequestException as e:
                self.logger.error("Error when requesting URL %s: %s", url, e)
                time.sleep(self.context.config.WEB_RETRY_TIMEOUT)
            else:
                return result.json() if json else result.text
        raise ConnectionError("Max retries reached when trying to request url {}".format(url))
