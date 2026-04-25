from requests import RequestException
from requests import Session

from bots.core import logger
from bots.core.utils.requests import rate_limit


class HttpClient(object):
    """
    Base class for HTTP clients.

    Attributes:
        headers (dict): Default HTTP headers to include on requests.
        session (requests.Session): Reused session for connection pooling.
    """

    def __init__(self, headers: dict = {}):
        """
        Initialize a HttpClient instance.

        Args:
            headers (dict, optional): Default headers to include in requests.
        """

        self.headers = headers
        self.session = Session()

    @rate_limit(3)
    def get(
        self,
        url: str,
        parameters: dict = None,
        headers: dict = None,
        is_binary: bool = False,
    ) -> (int, str | None):
        """
        Perform a GET request using the internal requests.Session.

        Args:
            url (str): Target URL.
            parameters (dict, optional): Query parameters for the request.
            headers (dict, optional): Headers to use for this request. If not
                provided, `self.headers` will be used.
            is_binary (bool, optional): Whether to return the response content as bytes instead of text. Defaults to False.
        """

        parameters = parameters or {}
        headers = headers or self.headers

        logger.info(
            f'[{self.__class__.__name__}] Starting GET request to {url}')

        try:
            response = self.session.get(
                url=url, params=parameters, headers=headers)
        except RequestException as e:
            logger.error(
                f'[{self.__class__.__name__}] GET request to {url} failed {str(e)}'
            )
            return -1, None

        if response.status_code != 200:
            logger.warning(
                f'[{self.__class__.__name__}] GET request to {url} returned status {response.status_code}'
            )
            return response.status_code, None

        logger.info(
            f'[{self.__class__.__name__}] GET request to {url} succeeded with status {response.status_code}'
        )
        return response.status_code, response.content if is_binary else response.text

    @rate_limit(3)
    def post(
        self, url: str, payload: dict = None, headers: dict = None
    ) -> (int, str | None):
        """
        Perform a POST request using the internal requests.Session.

        Args:
            url (str): Target URL.
            payload (dict, optional): Form data or payload to send in the body.
            headers (dict, optional): Headers to use for this request. Falls
                back to `self.headers` when not provided.
        """

        payload = payload or {}
        headers = headers or self.headers

        logger.info(
            f'[{self.__class__.__name__}] Starting POST request to {url}')

        try:
            response = self.session.post(
                url=url,
                data=payload,
                headers=headers,
            )
        except RequestException as e:
            logger.error(
                f'[{self.__class__.__name__}] POST request to {url} failed {str(e)}'
            )
            return -1, None

        if response.status_code != 200:
            logger.warning(
                f'[{self.__class__.__name__}] POST request to {url} returned status {response.status_code}'
            )
            return response.status_code, None

        logger.info(
            f'[{self.__class__.__name__}] POST request to {url} succeeded with status {response.status_code}'
        )

        return response.status_code, response.text

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the instance.
        """

        attrs = ', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())
        return f'<{self.__class__.__name__} {attrs}>'
