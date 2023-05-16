import datetime
import json
import os

import pika

from database.mongodb import get_db

RMQ_VARIATION_QUEUE = os.getenv('RMQ_VARIATION_QUEUE', 'hibrid-variation')
RMQ_MONITOR_QUEUE = os.getenv('RMQ_MONITOR_QUEUE', 'hibrid')

RMQ_HOSTNAME = os.getenv('RMQ_HOSTNAME', 'localhost')
RMQ_VHOST = os.getenv('RMQ_VHOST')
RMQ_USERNAME = os.getenv('RMQ_USERNAME')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD')

MAIN = os.getenv('MAIN_BOOKMAKER', 'feedmaker')
ENABLE_TEST = int(os.getenv('ENABLE_TEST', 0)) == 1

client = get_db()

if RMQ_USERNAME is not None and RMQ_PASSWORD is not None:
    credentials = pika.PlainCredentials(RMQ_USERNAME, RMQ_PASSWORD)
else:
    credentials = pika.ConnectionParameters.DEFAULT_CREDENTIALS

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        RMQ_HOSTNAME,
        virtual_host=RMQ_VHOST,
        credentials=credentials,
        heartbeat=15,
        client_properties={
            'connection_name': 'hibrid-monitor',
        }))
channel = connection.channel()


def old_odd_variations(updates):
    message = {
        'type': 'odd-variation',
        'variations': [],
        'mainLines': '#'
    }

    for update in updates:
        if update['_id'] not in message:
            message['_id'] = update['_id']
            message['sportId'] = update['sport_id']
            message['bookmakerName'] = update['bookmaker_name']
            message['status'] = update['status'] if 'status' in update else True

        if str(update['last_update']).isnumeric():
            updt = datetime.datetime.fromtimestamp(update['last_update']).strftime('%Y-%m-%dT%H:%M:%S')
        else:
            updt = update['last_update']

        message['variations'].append({
            'marketName': update['market_name'],
            'sbv': str(update['sbv']).replace(',', '.'),
            'outcomeName': update['outcome_name'],
            'odd': update['odd'],
            'lastUpdate': updt
        })
    return message


def odd_variations(variation: dict):

    if variation['sportId'] == 1 and 'mainLines' in variation and 'O/U' in variation['mainLines']:
        variation['mainLines']['O/U'] = '#'

    message = {
        'type': 'odd-variation',
        '_id': variation['id'],
        'sportId': variation['sportId'],
        'bookmakerName': variation['bookmakerName'],
        'status': variation['status'],
        'mainLines': variation['mainLines'],
        'variations': [],
    }

    for update in variation['updates']:
        if str(update['last_update']).isnumeric():
            updt = datetime.datetime.fromtimestamp(update['last_update']).strftime('%Y-%m-%dT%H:%M:%S')
        else:
            updt = update['last_update']

        message['variations'].append({
            'marketName': update['market_name'],
            'sbv': str(update['sbv']).replace(',', '.'),
            'outcomeName': update['outcome_name'],
            'odd': update['odd'],
            'lastUpdate': updt
        })

    return message


def fixture_variation(variation):
    if 'bookmaker_name' not in variation or 'sport_id' not in variation or variation['bookmaker_name'] != MAIN:
        return None
    return {
        '_id': variation['_id'],
        'type': 'fixture-variation',
        'bookmakerName': variation['bookmaker_name'],
        'sportId': variation['sport_id'],
        'variations': [{k: v for k, v in variation.items() if k not in ('_id', 'bookmaker_name', 'sport_id', 'type')}]
    }


def mapping_variation(variation, vtype: str):
    message = {'type': vtype, '_id': variation['_id']}
    events = {i['bookmakerName']: i for i in variation['events']}
    main_event = events[MAIN]
    for key in ['homeName', 'homeId', 'awayName', 'awayId', 'date', 'tournamentId', 'tournamentName', 'categoryId',
                'categoryName',
                'sportId', 'sportName']:
        try:
            if isinstance(main_event[key], datetime.datetime):
                message[key] = main_event[key].strftime('%Y-%m-%dT%H:%M:%S')
            elif key == 'date':
                message[key] = datetime.datetime.fromtimestamp(main_event[key]).strftime('%Y-%m-%dT%H:%M:%S')
            else:
                message[key] = main_event[key]
        except:
            main_event[key] = None

    for bookmaker, event in events.items():
        message[f'{bookmaker}_id'] = event['id']
        odds = client.get_database(bookmaker) \
            .get_collection('activeEvents') \
            .find_one({'_id': event['id']}, {'back': 1, 'lay': 1})

        if odds is not None and 'back' in odds:
            back = odds['back']
            if back is None: continue
            result = {}
            for market in back:
                key = f'{market}'
                result[key] = {}
                for spread in back[market]:
                    if not isinstance(back[market][spread], dict): continue
                    if 'main' not in result[key]:
                        result[key]['main'] = spread
                    result[key][spread] = {}
                    for sign in back[market][spread]:
                        try:
                            result[key][spread][sign] = back[market][spread][sign]['odd']
                        except:
                            pass
            message[f'{bookmaker}'] = result
    return message


def main(ch, method, properties, body):
    variation = json.loads(body.decode())

    if 'type' not in variation:
        return
    elif variation['type'] == 'ov' and 'id' in variation:
        message = odd_variations(variation)
    elif variation['type'] == 'ov':
        message = old_odd_variations(variation['updates'])
    elif variation['type'] == 'fx':
        message = fixture_variation(variation)
    elif variation['type'] == 'map':
        message = mapping_variation(variation, 'new-event')
    elif variation['type'] == 'manual-map':
        message = mapping_variation(variation, 'new-event')
    else:
        message = variation

    ch.basic_ack(method.delivery_tag)

    if message is not None:
        channel.basic_publish(
            exchange='',
            routing_key=RMQ_MONITOR_QUEUE,
            body=json.dumps(message).encode('utf-8'))
        print('produced message', message)

        if ENABLE_TEST:
            channel.basic_publish(
                exchange='',
                routing_key=RMQ_MONITOR_QUEUE + '-test',
                body=json.dumps(message).encode('utf-8'))


if __name__ == '__main__':
    channel.basic_consume(queue=RMQ_VARIATION_QUEUE, auto_ack=False, on_message_callback=main,
                          consumer_tag='hibrid-monitor')
    channel.start_consuming()
