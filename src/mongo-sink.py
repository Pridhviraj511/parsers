import json
import logging
import os
import traceback
from datetime import datetime

import pika
from pika.adapters.blocking_connection import BlockingChannel

from database.mongodb import get_db

RMQ_HOSTNAME = os.getenv('RMQ_HOSTNAME', 'localhost')
RMQ_VHOST = os.getenv('RMQ_VHOST', '/')
RMQ_USERNAME = os.getenv('RMQ_USERNAME')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD')
RMQ_TOPIC_FIXTURE_VARIATION = os.getenv('RMQ_TOPIC_FIXTURE_VARIATION', 'mongo-sink')
LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)

client = get_db()
logging.basicConfig(level=LOG_LEVEL)


def store_on_mongo(ch: BlockingChannel, method, properties, body):
    event = json.loads(body.decode())

    if 'betradarId' not in event: event['betradarId'] = '0'
    logging.info('{_id} {betradarId} {bookmakerName} {homeName} - {awayName}'.format(**event))

    _id = event['_id']
    del event['_id']

    try:

        # add
        if 'isNew' in event and event['isNew']:
            event['_insertOn'] = datetime.utcnow()

        event['_modifyOn'] = datetime.utcnow()
        event['date'] = datetime.fromtimestamp(float(event['date']))

        client.get_database(event['bookmakerName']).get_collection('activeEvents') \
            .update_one({'_id': _id}, {'$set': event}, upsert=True)

    except:
        tb = traceback.format_exc()
        logging.error(f'{_id} {event} - {tb}')

    ch.basic_ack(method.delivery_tag)


if __name__ == '__main__':

    if RMQ_USERNAME is not None and RMQ_PASSWORD is not None:
        credentials = pika.PlainCredentials(RMQ_USERNAME, RMQ_PASSWORD)
    else:
        credentials = pika.ConnectionParameters.DEFAULT_CREDENTIALS

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            RMQ_HOSTNAME,
            virtual_host=RMQ_VHOST,
            credentials=credentials,
            heartbeat=300,
            client_properties={
                'connection_name': 'mongo-sink',
            }
        ))
    channel = connection.channel()
    channel.basic_consume(queue=RMQ_TOPIC_FIXTURE_VARIATION, on_message_callback=store_on_mongo, consumer_tag='mongo-sink')
    channel.basic_qos(0, 1)

    channel.start_consuming()
