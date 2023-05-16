import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta
from time import sleep

import requests

from database.mongodb import get_db, update_many
from models import BOOKMAKERS
from utils.calculations import str_to_date

DEBUG = os.getenv('DEBUG', "0")

logging.basicConfig(level=logging.DEBUG if int(DEBUG) == 1 else logging.INFO)


def send_alert(error: str):
    req = requests.post(
        'https://oddsandmore.webhook.office.com/webhookb2/17086f56-bb96-463c-8e57-6959d9737ba4@bec88a38-9e44-4bb4-8ab6-a190fff2a6ce/IncomingWebhook/6d4996471f07481b8bbd4d67620ed611/52e982b8-b747-4c6e-a446-27538aba09dd',
        json.dumps({
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"MANAGER: {error}",
                                "wrap": True
                            }
                        ]
                    }
                }
            ]
        }), headers={"Content-Type": "application/json"})
    if req.status_code != 200:
        logging.error(error)


def process_interval(a):
    if not a:
        return None

    try:
        prev_time, prev_odd = None, None
        n, z = 0, 0
        for time, odd in a.items():
            if prev_time is None:
                prev_time, prev_odd = time, odd
                continue

            minutes = int((time - prev_time).total_seconds() / 60)
            z += minutes * prev_odd
            n += minutes
            prev_odd = odd
            prev_time = time

        if n == 0:
            return round(prev_odd, 2)

        return round(z / n, 2)

    except Exception as e:
        logging.warning(f'manager error (process_interval), error: {e}')


def split_into_intervals(date):
    x8 = date + timedelta(hours=-1)
    x7 = date + timedelta(hours=-2)
    x6 = date + timedelta(hours=-3)
    x5 = date + timedelta(hours=-4)
    x4 = x5.replace(hour=0, minute=0, second=0, microsecond=0)
    x3 = x4 + timedelta(days=-1)
    x2 = x4 + timedelta(days=-2)

    return x2, x3, x4, x5, x6, x7, x8


def average_for_key(a1, a2, a3, a4, a5, a6, a7, a8):
    return {
        "1": process_interval(a1),
        "2": process_interval(a2),
        "3": process_interval(a3),
        "4": process_interval(a4),
        "5": process_interval(a5),
        "6": process_interval(a6),
        "7": process_interval(a7),
        "8": process_interval(a8)
    }


def sort_and_populate_dates(intervals: dict) -> dict:
    sorting_dict, populating_dict = {}, {}

    # first: convert dates to str and then sort them.
    for i, j in intervals.items():
        sorting_dict.update({str(i): j})
    sorting_dict = dict(sorted(sorting_dict.items()))

    # second: populating empty intervals with previous odd.
    prev_value = None
    for i, j in sorting_dict.items():
        if j is None:
            if prev_value is None:
                continue
            j = prev_value
        populating_dict.update({str_to_date(i).replace(second=0, microsecond=0): j})
        prev_value = j

    return populating_dict


def get_averages(historical_odds: dict, date: datetime) -> dict:
    averages = defaultdict(dict)
    x2, x3, x4, x5, x6, x7, x8 = split_into_intervals(date)

    for key, value in historical_odds.items():

        if not key.startswith('back') and not key.startswith('lay'):
            continue

        averages[key] = {}
        for market_name, market in value.items():
            averages[key][market_name] = {}
            for sbv, outcomes in market.items():
                averages[key][market_name][sbv] = {}
                for outcome_name, hist in outcomes.items():
                    a8, a7, a6, a5, a4, a3, a2, a1 = {}, {}, {}, {}, {}, {}, {}, {}
                    main_intervals = {date: None, x8: None, x7: None, x6: None, x5: None, x4: None, x3: None, x2: None}
                    for h in hist:
                        main_intervals.update({h['date']: h['change']})

                    for k, v in sort_and_populate_dates(main_intervals).items():

                        if k <= x2:
                            a1.update({k: v})
                        if x2 <= k <= x3:
                            a2.update({k: v})
                        if x3 <= k <= x4:
                            a3.update({k: v})
                        if x4 <= k <= x5:
                            a4.update({k: v})
                        if x5 <= k <= x6:
                            a5.update({k: v})
                        if x6 <= k <= x7:
                            a6.update({k: v})
                        if x7 <= k <= x8:
                            a7.update({k: v})
                        if x8 <= k <= date:
                            a8.update({k: v})

                    averages[key][market_name][sbv][outcome_name] = average_for_key(a1, a2, a2, a4, a5, a6, a7, a8)

    return averages


def calculate_historical_averages(database, event_id, date, bookmaker_name):
    try:
        # for testing
        # from examples import historicals as historical_odds
        historical_odds = database.find_one({'_id': event_id})

        if not historical_odds:
            return

        averages = get_averages(historical_odds, date)

        result = database.update_one({'_id': event_id}, {'$set': {'averages': averages}})

        if (not result.upserted_id or result.raw_result.get('updatedExisting', None) is not False) and (
                result.upserted_id is not None or result.raw_result.get('updatedExisting', None) is not True):
            logging.warning(f'{bookmaker_name} - Historical error {event_id} {averages}')

    except Exception as e:
        logging.error(f'{bookmaker_name} - Error on calculate_historical_averages, event: {event_id} error: {e}')
        send_alert(f'{bookmaker_name} - Error on calculate_historical_averages, event: {event_id} error: {e}')


def activation_and_movement(bookmaker_name, date):
    db = get_db(db_name=bookmaker_name)
    collections = db.list_collection_names()
    if 'activeEvents' not in collections:
        return

    logging.info(bookmaker_name.upper())

    # activate events
    update_many(database=bookmaker_name, collection_name='activeEvents',
                fil={'status': True, 'noOdds': False, 'live': False, 'date': {'$gt': date}},
                upd={'$set': {'active': True}}, connection=db)

    # deactivate events
    update_many(database=bookmaker_name, collection_name='activeEvents',
                fil={'$or': [{'status': False}, {'noOdds': True}, {'live': True}, {'date': {'$lt': date}}]},
                upd={'$set': {'active': False}}, connection=db)

    # for LIVE
    if 'liveEvents' in collections:
        logging.info(f'{bookmaker_name.upper()} LIVE')
        update_many(database=bookmaker_name, collection_name='liveEvents',
                    fil={'status': True, 'noOdds': False},
                    upd={'$set': {'active': True}}, connection=db)

        update_many(database=bookmaker_name, collection_name='liveEvents',
                    fil={'$or': [{'status': False}, {'noOdds': True}]},
                    upd={'$set': {'active': False}}, connection=db)

    # for outrights
    if 'activeOutrights' in collections:
        logging.info(f'{bookmaker_name.upper()} OUTRIGHTS')
        # activate outrights
        update_many(database=bookmaker_name, collection_name='activeOutrights',
                    fil={'status': True, 'live': False, 'date': {'$gt': date}},
                    upd={'$set': {'active': True}}, connection=db)

        # deactivate outrights
        update_many(database=bookmaker_name, collection_name='activeOutrights',
                    fil={'$or': [{'status': False}, {'live': True}, {'date': {'$lt': date}}]},
                    upd={'$set': {'active': False}}, connection=db)

    events = db.activeEvents.find({'date': {'$lt': date}})
    # date + timedelta(minutes=5) if we want to wait 5min before moving them
    for event in events:

        try:
            calculate_historical_averages(db.historical, event['_id'], event['date'], bookmaker_name)

            updates = {x: event[x] for x in event if x != '_id'}
            result = db.passiveEvents.update_one({'_id': event['_id']}, {"$set": updates}, upsert=True)

            if (result.upserted_id and result.raw_result.get('updatedExisting', None) is False) or (
                    result.upserted_id is None and result.raw_result.get('updatedExisting', None) is True):
                result = db.activeEvents.delete_one({'_id': event['_id']})

                if result.deleted_count != 1:
                    logging.warning(f'{bookmaker_name}: manager error (activation_and_movement 3) ' +
                                    f'for event id {event["_id"]} deleted: {result.deleted_count}')
            else:
                logging.warning(f'{bookmaker_name}: manager error (activation_and_movement 2): {result.upserted_id}, ' +
                                f'{result.raw_result.get("updatedExisting", None)}')

        except Exception as e:
            logging.error(f'{bookmaker_name}: manager error (activation_and_movement), event: {event["_id"]} error: {e}')
            send_alert(f'{bookmaker_name}: manager error (activation_and_movement), event: {event["_id"]} error: {e}')
            break

    if 'activeOutrights' in collections:
        events = db.activeOutrights.find({'endDate': {'$lt': date}})
        # date + timedelta(minutes=5) if we want to wait 5min before moving them
        for event in events:

            try:
                calculate_historical_averages(db.historical, event['_id'], event['endDate'], f"{bookmaker_name} outrights")

                updates = {x: event[x] for x in event if x != '_id'}
                result = db.passiveOutrights.update_one({'_id': event['_id']}, {"$set": updates}, upsert=True)

                if (result.upserted_id and result.raw_result.get('updatedExisting', None) is False) or (
                        result.upserted_id is None and result.raw_result.get('updatedExisting', None) is True):
                    result = db.activeOutrights.delete_one({'_id': event['_id']})

                    if result.deleted_count != 1:
                        logging.info(
                            'manager error (activation_and_movement) 3, something is not ok' + result.deleted_count +
                            f'{bookmaker_name}: manager error (activation_and_movement 3) for event id {event["_id"]}')
                else:
                    logging.warning(f'manager error (activation_and_movement 2): {result.upserted_id}, '
                                    f'{result.raw_result.get("updatedExisting", None)}')

            except Exception as e:
                logging.error(f'{bookmaker_name}: Error on activation_and_movement, event: {event["_id"]}  error: {e}')
                send_alert(f'{bookmaker_name}: Error on activation_and_movement, event: {event["_id"]} error: {e}')
                break


def main():
    while True:
        ddd = datetime.utcnow().replace(microsecond=0)

        try:
            print(f'START {ddd.isoformat()}')
            # for all bookies: activate or deactivate if needed and move to passive collection
            for database in BOOKMAKERS:
                activation_and_movement(bookmaker_name=database, date=ddd)

        except Exception as e:
            print(f'manager error (main), error: {e}')

        sleep(60)


if __name__ == '__main__':
    main()
