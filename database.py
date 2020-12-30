from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from tinydb import TinyDB, Query
import datetime

class Database:
    def __init__(self, db='debug.json'):
        self.db = TinyDB(db, storage=CachingMiddleware(JSONStorage))

    def get_statistics(self, user_id):
        with self.db as db:
            q = Query()
            return db.table('stats').search(q.user_id == str(user_id))


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
    from pycountry import countries
    import pycountry_convert as pc
    def country_alpha2_to_continent_code(a2):
        if a2 == 'AQ': return 'AN'
        elif a2 == 'TF': return 'AN'
        elif a2 == 'EH': return 'AF'
        elif a2 == 'PN': return 'OC'
        elif a2 == 'SX': return 'NA'
        elif a2 == 'TL': return 'AS'
        elif a2 == 'UM': return 'NA'
        elif a2 == 'VA': return 'EU'
        else: return pc.country_alpha2_to_continent_code(a2)
    cc = pc.country_alpha2_to_continent_code('XK')
    c = pc.convert_continent_code_to_continent_name(cc)
    countries_pc = pc.convert_countries.list_country_alpha2()
    countries_p = [c.alpha_2 for c in countries]
    for a2 in countries_pc:
        country_alpha2_to_continent_code(a2)
    print(list(set(pc.convert_country_alpha2_to_continent_code.COUNTRY_ALPHA2_TO_CONTINENT_CODE.values())))
    #database = Database()
    #database.get_statistics('26442581')