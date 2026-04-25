import json
import os

from dotenv import load_dotenv

from bots.core import Database
from bots.core import logger
from bots.core.clients import HttpClient
from bots.core.clients import TelegramClient


def run() -> None:
    """
    Fetches available property listings from a remote API, filters and processes the results, and sends new property notifications to a configured bot.
    """

    logger.info('[Menorca Properties] Running bot...')

    load_dotenv()

    db = Database('db/menorca-properties.json')
    http = HttpClient(
        headers={'Authorization': 'Bearer ' +
                 os.getenv('MENORCA_PROPERTIES_API_KEY')}
    )
    bot = TelegramClient(
        token=os.getenv('MENORCA_PROPERTIES_TELEGRAM_TOKEN'),
        chat=os.getenv('MENORCA_PROPERTIES_TELEGRAM_CHAT'),
    )

    for property_type in ['House', 'Apartment', 'Chalet', 'Villa']:
        status, response = http.get(
            'https://api.marcorfilacarreras.cloud/menorca-properties/v1/properties',
            parameters={
                'price_min': 150_000,
                'price_max': 300_000,
                'property_type': property_type,
                'availability': 'Available',
            },
        )

        if status != 200:
            logger.error(
                f'[Menorca Properties] Error fetching properties with status code {status}'
            )
            continue

        try:
            response = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(
                f'[Menorca Properties] Error decoding JSON response: {e}')
            continue

        properties = response.get('data', [])

        logger.info(f'[Menorca Properties] Found {len(properties)} properties')

        for property_ in properties:
            message = (
                f'📢 *NEW PROPERTY FOUND*\n\n'
                f"🏷 *Type:* {bot.escape(property_['property_type'])}\n\n"
                f"💰 *Price:* {bot.escape(str(property_['price']))} {bot.escape(property_['currency'])}\n\n"
                f"📊 *Status:* {bot.escape(property_['availability'])}\n\n"
                f"📍 *Location:* {bot.escape(property_['location']['address'] + ', ' + property_['location']['municipality'])}\n"
                f'[‎]({property_["location"]})'
            )

            if len(db.read(dict, filters={'id': property_['id']})) > 0:
                continue

            if not bot.send_message(message):
                logger.error(
                    f"[Menorca Properties] Failed to send message for property {property_['id']}"
                )
                continue

            db.add(property_)
            db.commit()
