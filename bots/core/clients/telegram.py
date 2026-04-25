import json
import re

from bots.core import logger
from bots.core.clients import HttpClient


class TelegramClient(HttpClient):
    """
    A simple Telegram wrapper for sending messages.
    """

    URL = 'https://api.telegram.org'

    def __init__(self, token: str, chat: str) -> None:
        """
        Initializes the Telegram bot instance.

        Args:
            token: The Bot API Token.
            chat: The Telegram Chat ID.
        """

        super().__init__(
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        )

        self.token = token
        self.chat = chat

        if token is None:
            logger.info(f'[{self.__class__.__name__}] No token provided')

        if self.chat is None:
            logger.info(f'[{self.__class__.__name__}] No chat provided.')

    def send_message(self, message: str = '') -> bool:
        """
        Sends a plain text message to the configured Telegram chat.

        Args:
            message: The text content to send.
        """

        logger.info(f'[{self.__class__.__name__}] Sending a message')

        parameters = {
            'chat_id': self.chat,
            'text': message,
            'parse_mode': 'MarkdownV2',
        }

        status, response = self.get(
            f'{self.URL}/bot{self.token}/sendMessage', parameters=parameters
        )

        logger.debug(f'[{self.__class__.__name__}] GET status code {status}')

        if status != 200:
            logger.warning(
                f'[{self.__class__.__name__}] Failed to send a message with status {status}'
            )
            return False

        try:
            data = json.loads(response)
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(
                f'[{self.__class__.__name__}] Failed to parse content: {e}')
            return False

        if not data.get('ok'):
            logger.warning(
                f'[{self.__class__.__name__}] Failed to send a message with status {status}'
            )
            return False

        logger.info(f'[{self.__class__.__name__}] Message sent successfully')
        return True

    def escape(self, text: str = '') -> str:
        """
        Escapes special characters to comply with Telegram's MarkdownV2 formatting.

        Args:
            text: The raw string containing potential Markdown characters.
        """

        return re.sub(r'([_*[\]()~`>#+-=|{}.!])', r'\\\1', text)
