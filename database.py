from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb import TinyDB, Query
from pycountry import countries
import datetime

class Database:
    def __init__(self, db='debug.json'):
        self.db = TinyDB(db, storage=CachingMiddleware(JSONStorage))

    def print_database(self, user_id):
        with self.db as db:
            q = Query()
            print(db.table('stats').search(q.user_id == str(user_id)))

    def insert_answer(self, user_id, country_id, answer_country_id):
        with self.db as db:
            stats = db.table('stats')
            now = datetime.datetime.now()
            timestamp = "{}-{}-{}-{}-{}-{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
            data = {
                'user_id': str(user_id),
                'created': str(timestamp),
                'country_id': str(country_id),
                'answer_country_id': str(answer_country_id)
            }
            stats.insert(data)
            return data

if __name__ == "__main__":
    database = Database()
    database.print_database('26442581')