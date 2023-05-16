import json
import logging
import os
import time
from datetime import datetime
from threading import Thread

import pika
import requests
from humanfriendly import format_timespan
from pika.adapters.blocking_connection import BlockingChannel
from pymongo import UpdateOne

from database.mongodb import get_db

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))

DATABASE = os.getenv('DATABASE', 'oddsandmore')
COLLECTION = os.getenv('COLLECTION', 'heartbeat')

RMQ_HOSTNAME = os.getenv('RMQ_HOSTNAME', 'localhost')
RMQ_VHOST = os.getenv('RMQ_VHOST', '/')
RMQ_USERNAME = os.getenv('RMQ_USERNAME')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD')
RMQ_HEARTBEAT = os.getenv('RMQ_HEARTBEAT', 'heartbeat')
RMQ_HIBRID_VARIATION = os.getenv('RMQ_HIBRID_VARIATION', 'hibrid-variation')

INACTIVITY_LIMIT = os.getenv('INACTIVITY_LIMIT', 8 * 60)
NOTIFY_RANGE = os.getenv("NOTIFY_RANGE", 15 * 60)
BRIDGE_URI = os.environ.get('BRIDGE_URI', 'https://staging-api.oam.ltd:3010/api/bridge')

if RMQ_USERNAME is not None and RMQ_PASSWORD is not None:
    credentials = pika.PlainCredentials(RMQ_USERNAME, RMQ_PASSWORD)
else:
    credentials = pika.ConnectionParameters.DEFAULT_CREDENTIALS

last_sent = None
in_error = []
current = {}
active_bookmakers = []
inactive_bookmakers = []
client = get_db()


def get_hibrid_rmq():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            RMQ_HOSTNAME,
            virtual_host=RMQ_VHOST,
            credentials=credentials,
            heartbeat=300,
            client_properties={
                'connection_name': 'mongo-heartbeat',
            })
    )
    return connection.channel()


def send_alert(errors: list):
    global last_sent

    if not len(errors):
        return

    if not last_sent or time.time() - last_sent > NOTIFY_RANGE:
        last_sent = time.time()

        req = requests.post(
            'https://oddsandmore.webhook.office.com/webhookb2/17086f56-bb96-463c-8e57-6959d9737ba4@bec88a38-9e44-4bb4-8ab6-a190fff2a6ce/IncomingWebhook/4b95bce98ed94a37936adeedd88d240f/52e982b8-b747-4c6e-a446-27538aba09dd',
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
                                    "text": "\r".join(errors),
                                    "wrap": True
                                }
                            ]
                        }
                    }
                ]
            }), headers={"Content-Type": "application/json"})
        if req.status_code != 200:
            logging.error(errors)


def update_heartbeat(ch: BlockingChannel, method, properties, body):
    heartbeat = body.decode()
    logging.debug(f"Read heartbet for {heartbeat}")
    current[heartbeat] = time.time()
    client.get_database(DATABASE).get_collection(COLLECTION) \
        .update_one({'name': heartbeat}, {'$set': {'lastUpdateOn': datetime.now()}}, upsert=True)
    ch.basic_ack(method.delivery_tag)


def main_schedule(old_errors):
    global last_sent
    logging.info(f"Start main schedule for current status {current}")
    errors = {}
    status = {}
    for bookmaker in active_bookmakers:
        bookmaker_name = bookmaker['name']
        b_name = bookmaker['dbName']
        if not bookmaker['active']:
            continue
        elif bookmaker['dbName'] not in current:
            errors[bookmaker_name] = f'- {bookmaker_name} is inactive'
            status[b_name] = False
            continue

        inactivity_time = time.time() - current[bookmaker['dbName']]
        if inactivity_time > INACTIVITY_LIMIT:
            print(f'- {bookmaker_name} is inactive for', inactivity_time)
            errors[bookmaker_name] = f'- {bookmaker_name} is inactive for {format_timespan(int(inactivity_time))}'

            if bookmaker_name not in inactive_bookmakers:
                inactive_bookmakers.append(bookmaker_name)
                last_sent = None

            status[b_name] = False
        else:
            status[b_name] = True

            if bookmaker_name in inactive_bookmakers:
                errors[bookmaker_name] = f'- {bookmaker_name} is active now'
                inactive_bookmakers.remove(bookmaker_name)
                last_sent = None

    if errors != old_errors:
        send_alert(list(errors.values()))

        updates = [UpdateOne({'name': b}, {'$set': {'status': s}}) for b, s in status.items()]
        if len(updates):
            client.get_database(DATABASE).get_collection(COLLECTION).bulk_write(updates)

    hibrid_channel.basic_publish(
        exchange='',
        routing_key=RMQ_HIBRID_VARIATION,
        body=json.dumps({'type': 'heartbeat', 'bookmakers': status}).encode('utf-8'))

    hibrid_channel.basic_publish(
        exchange='',
        routing_key=f'test-{RMQ_HIBRID_VARIATION}',
        body=json.dumps({'type': 'heartbeat', 'bookmakers': status}).encode('utf-8'))

    return errors


def get_heartbeat_rmq():
    logging.info("Restart process main rmq")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            RMQ_HOSTNAME,
            virtual_host=RMQ_VHOST,
            credentials=credentials,
            heartbeat=300,

        ))
    channel = connection.channel()
    channel.basic_consume(
        queue=RMQ_HEARTBEAT,
        on_message_callback=update_heartbeat,
        consumer_tag='healt-check-python'
    )
    heartbeat_thread = Thread(target=channel.start_consuming)
    heartbeat_thread.start()
    return channel


if __name__ == '__main__':
    active_bookmakers_request = requests.get(f'{BRIDGE_URI}/bookmakers/active')
    active_bookmakers = active_bookmakers_request.json()

    current = {
        i['name']: i['lastUpdateOn'].timestamp() for i in
        client.get_database(DATABASE).get_collection(COLLECTION).find({})
    }

    hibrid_channel = get_hibrid_rmq()
    heartbeat_channel = get_heartbeat_rmq()

    time.sleep(5)
    while True:
        try:

            # check connection
            if hibrid_channel.is_closed or hibrid_channel.connection.is_closed:
                hibrid_channel = get_hibrid_rmq()
            # check heartbeat connection
            if heartbeat_channel.is_closed or heartbeat_channel.connection.is_closed:
                heartbeat_channel = get_heartbeat_rmq()

            in_error = main_schedule(in_error)

        except Exception as ex:
            logging.error(ex)

        time.sleep(5)
