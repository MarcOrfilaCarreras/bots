import json
import os

from dotenv import load_dotenv

from bots.core import Database
from bots.core import logger
from bots.core.clients import HttpClient
from bots.core.clients import TelegramClient


def run() -> None:
    """
    Fetches active BOE auctions from a remote API, filters and processes the results, and sends new auction notifications to a configured bot.
    """

    logger.info('[Subastas BOE] Running bot...')

    load_dotenv()

    db = Database('db/subastas-boe.json')
    http = HttpClient(
        headers={'Authorization': 'Bearer ' +
                 os.getenv('SUBASTAS_BOE_API_KEY')}
    )
    bot = TelegramClient(
        token=os.getenv('SUBASTAS_BOE_TELEGRAM_TOKEN'),
        chat=os.getenv('SUBASTAS_BOE_TELEGRAM_CHAT'),
    )

    status, response = http.get(
        'https://api.marcorfilacarreras.cloud/subastas-boe/v1/auctions',
        parameters={
            'auction_type': 'Todos',
            'auction_status': 'Celebrándose',
            'asset_type': 'Todos',
            'asset_subtype': 'Todos',
            'province': 'Illes Balears',
            'start_date': '2026-03-27',
            'end_date': '2026-04-25',
            'page': 1,
        },
    )

    if status != 200:
        logger.error(
            f'[Subastas BOE] Error fetching auctions with status code {status}'
        )
        return

    try:
        response = json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f'[Subastas BOE] Error decoding JSON response: {e}')
        return

    auctions = response.get('data', [])

    logger.info(f'[Subastas BOE] Found {len(auctions)} auctions')

    for auction in auctions:
        message = (
            f'📢 *NEW AUCTION FOUND*\n\n'
            f'📅 *Start date:* {bot.escape(auction["start_date"])}\n\n'
            f'⏳ *End date:* {bot.escape(auction["end_date"])}\n\n'
            f'💰 *Appraisal:* {bot.escape(str(auction["appraisal"]))}\n\n'
            f'💸 *Minimum bid:* {bot.escape(str(auction["bid"]["minimum"]))}\n\n'
            f'🔒 *Deposit:* {bot.escape(str(auction["bid"]["deposit"]))}\n'
            f'[‎](https://subastas.boe.es/detalleSubasta.php?idSub={auction["id"]})'
        )

        if len(db.read(dict, filters={'id': auction['id']})) > 0:
            continue

        if not bot.send_message(message):
            logger.error(
                f"[Subastas BOE] Failed to send message for auction {auction['id']}"
            )
            continue

        db.add(auction)
        db.commit()
