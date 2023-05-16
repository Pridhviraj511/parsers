import os
from datetime import datetime

from pymongo import UpdateOne

from database.mongodb import get_db

INACTIVITY_LIMIT = os.getenv('INACTIVITY_LIMIT', 5 * 60 * 1000);

current = {}
client = get_db()

if __name__ == '__main__':

    current_db = client.get_database('oddsandmore').get_collection('bookmakers').find({'active': True})
    operations = []
    for bookmaker_item in current_db:
        bookmaker = bookmaker_item['name']

        inactivity_time = datetime.now() - bookmaker['lastUpdateOn']
        if inactivity_time > INACTIVITY_LIMIT:
            print(f'{bookmaker} is inactive for', inactivity_time)
            if not bookmaker_item['error']:
                # send alert
                operations.append(UpdateOne({'name': bookmaker}, {'error': True}))
                pass
        elif bookmaker_item['error']:
            operations.append(UpdateOne({'name': bookmaker}, {'error': False}))

    if len(operations):
       client.get_database('oddsandmore').get_collection('bookmakers').bulk_write(operations)
