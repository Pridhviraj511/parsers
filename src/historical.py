import json
import logging
import os
from datetime import datetime
from typing import List

import pika
import requests
from pymongo import UpdateOne, MongoClient

from database.mongodb import get_db

RMQ_HOSTNAME = os.getenv('RMQ_HOSTNAME', 'localhost')
RMQ_VHOST = os.getenv('RMQ_VHOST')
RMQ_USERNAME = os.getenv('RMQ_USERNAME')
RMQ_PASSWORD = os.getenv('RMQ_PASSWORD')
RMQ_TOPIC_ODD_VARIATION = os.getenv('RMQ_TOPIC_ODD_VARIATION', 'odd-variation')
DEBUG = os.getenv('DEBUG', "0")

client: MongoClient = get_db()

logging.basicConfig(level=logging.DEBUG if int(DEBUG) == 1 else logging.INFO)


def send_alert(error: str, updates: dict):
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
                                "text": f"HISTORICAL: {error}",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": f"Updates:- {updates}",
                                "wrap": True
                            }
                        ]
                    }
                }
            ]
        }), headers={"Content-Type": "application/json"})
    if req.status_code != 200:
        logging.error(error)


def get_historical(id: int, update: dict):
    transaction: List[UpdateOne] = []
    key = f"back.{update['market_name']}.{str(update['sbv']).replace('.', ',')}.{update['outcome_name']}"

    value = {'change': update['odd'], 'date': datetime.fromtimestamp(update['last_update'])}
    transaction.append(UpdateOne(
        {'_id': id},
        {'$push': {key: value}},
        upsert=True
    ))
    return transaction


def main(ch, method, properties, body):
    updates = json.loads(body.decode())
    logging.debug(f"Received message: {updates}")

    try:
        
        if 'id' in updates:
            # New Variations format
            _id = updates['id']
            name = updates['bookmakerName']
        else:
            _id = updates['updates'][0]['_id']
            name = updates['updates'][0]['bookmaker_name']

        historical_updates = []
        for update in updates['updates']:
            historical_updates += get_historical(_id, update)

        if name is None:
            raise Exception("Name not valid")

        logging.debug(historical_updates)
        client.get_database(name).get_collection('historical').bulk_write(historical_updates)

    except Exception as ex:
        logging.error(f"There are some errors:{ex} \n updates={updates}")
        send_alert(f"There are some errors:{ex}", updates)
        return

    ch.basic_ack(method.delivery_tag)


if __name__ == '__main__':
    if RMQ_USERNAME is not None and RMQ_PASSWORD is not None:
        credentials = pika.PlainCredentials(RMQ_USERNAME, RMQ_PASSWORD)
    else:
        credentials = pika.ConnectionParameters.DEFAULT_CREDENTIALS

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RMQ_HOSTNAME, virtual_host=RMQ_VHOST, credentials=credentials))
    channel = connection.channel()

    channel.basic_consume(queue=RMQ_TOPIC_ODD_VARIATION, on_message_callback=main)

    channel.start_consuming()
