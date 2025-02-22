import copy
import traceback
import sys
from pymongo import MongoClient, errors as MongoErrors, DESCENDING

class Database:
    def __init__(self, host=None, port=27017, username='', password='', db='tester'):
        # collection name definitions
        RESULTS_COLLECTION = 'results'
        RATELIMIT_COLLECTION = 'rate-limits'

        try:
            print('[mongoDB] Connecting to ' + host + ':' + str(port))
            print('[mongoDB] Using Database `' + db + '`')
            # client and DB
            self.client = MongoClient(
                host=host,
                port=port,
                username=username,
                password=password,
                serverSelectionTimeoutMS=3)
            self.db = self.client[db]

            # collections
            self.results = self.db[RESULTS_COLLECTION]
            self.rate_limits = self.db[RATELIMIT_COLLECTION]

            # Test connection immediately, instead of
            # when trying to write in a request, later.
            self.client.admin.command('ismaster')
        except MongoErrors.ServerSelectionTimeoutError:
            print(traceback.format_exc())
            sys.exit('MongoDB connection timed out.')
        except:
            print(traceback.format_exc())
            sys.exit('MongoDB connection failed.')

    def write_result(self, result):
        # copy.deepcopy; otherwise mongo ObjectId (_id) would be added,
        # screwing up later JSON serialisation of results
        self.results.insert_one(copy.deepcopy(result))

    def write_rate_limit(self, data):
        self.rate_limits.insert_one(data)

    def get_result_by_screen_name(self, screen_name):
        return self.results.find_one({ "profile.screen_name": screen_name }, sort=[("_id", DESCENDING)], projection={"_id": False})

