from pymongo import MongoClient, ReplaceOne, DESCENDING
from datetime import datetime, timedelta
import json
import pandas as pd
import traceback
import itertools
from fuzzywuzzy import fuzz
from bson import ObjectId

class DATABASE_SETUP:
    def __init__(self):
        # with open('./config/mongo.json') as jsFile:
        #     mongo_dict = json.load(jsFile)
        # self.mongo_host = mongo_dict['host']
        # self.mongo_port = mongo_dict['port']
        # self.mongodb_url = MongoClient("mongodb://global_tnms:fkJmzaD0JINWr@localhost:27017/?authSource=admin&readPreference=primary&appname=mongodb-vscode%200.6.10&ssl=false")
        self.mongodb_url = MongoClient("mongodb://global_tnms:fkJmzaD0JINWr@mongo:27017/?authSource=admin&readPreference=primary&appname=mongodb-vscode%200.6.10&ssl=false")
        
        self.db = 'TNMS_Live'
    

    
    def update_setup(self, company, location, tollid, laneno, isactive):
        try:
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['setup']
            myquery = {
                        'company':company,
                        'location' : location,
                        "tollid": tollid,
                        "laneno": laneno,
                        # "inout":request_data['inout'],
                        # "cctvlink":request_data['cctvlink']
                    }
            resp = collection.update_one(myquery, { "$set": { "isactive": isactive} })
            mongo_db_client.close()
        except:
            print(traceback.print_exc())
            return -2
    # def resetpassword(self,request_data, password):
    #     try:
    #         # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
    #         mongo_db_client = self.mongodb_url
    #         db = mongo_db_client[self.db]
    #         collection = db['users']

    #         # ids = request_data['id']
    #         # ids = [ObjectId(i) for i in ids]
    #         # myquery = myquery = {
    #         #         "$and" :[{"company":request_data['company']}, {"location":request_data['location']}, {'tollid': request_data['tollid']}, {'_id': { "$in" : ids }}]
    #         #         }
    #         # resp = collection.delete_many(myquery)

    #         resp = collection.update_one({'_id':ObjectId(request_data['id'])}, { '$set': { "password": password }})
    #         print(resp.raw_result)
    #         resp = resp.upserted_id
    #         mongo_db_client.close()
    #         if resp:
    #             return resp
    #         else:
    #             return 0
    #     except Exception as e:
    #         return -2

    def setup_data(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['setup']
            # collection.insert_many([request_data])
            request_data['isactive'] = True
            check_keys = {
                        'company':request_data['company'],
                        'location' : request_data['location'],
                        "tollid": request_data['tollid'],
                        "laneno": request_data['laneno'],
                        # "inout":request_data['inout'],
                        # "cctvlink":request_data['cctvlink']
                    }
            resp = collection.replace_one(check_keys, request_data, upsert=True)
            resp = resp.upserted_id                 
            mongo_db_client.close()
            if resp:
                return resp
            else:
                return 0
            # mongo_db_client.close()
            # return 0
        except Exception as e:
            print(traceback.print_exc())
            return -2

    def getsetupdetails(self, company, location, tollid):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['setup']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}]
                    }
            docs = list(collection.find(myquery))
            for doc in docs:
                doc['_id'] = str(doc['_id'])
                doc['id'] = doc.pop('_id')
            mongo_db_client.close()
            return docs
        except:
            print(traceback.print_exc())
            return -2


    def getcamerastatusdetails(self, company, location, tollid):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['setup']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}]
                    }
            docs = list(collection.find(myquery))
            active = 0
            inactive = 0
            for doc in docs:
                if doc['isactive']:
                    active+=1
                else:
                    inactive+=1
                # doc['_id'] = str(doc['_id'])
                # doc['id'] = doc.pop('_id')
            mongo_db_client.close()
            return active, inactive
        except:
            print(traceback.print_exc())
            return -2


    def savesetupdata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['setup']
            # collection.insert_many([request_data])
            
            check_keys = {
                # 'emailid':request_data['emailid'],
                '_id':ObjectId(request_data['id']),
            }
            request_data.pop("id")
            collection.replace_one(check_keys, request_data, upsert=True)
            
            # collection.insert_one(request_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            print(traceback.print_exc())
            return -2

    def deletesetup(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['setup']

            # ids = request_data['id']
            # ids = [ObjectId(i) for i in ids]
            # myquery = myquery = {
            #         "$and" :[{"company":request_data['company']}, {"location":request_data['location']}, {'tollid': request_data['tollid']}, {'_id': { "$in" : ids }}]
            #         }
            # resp = collection.delete_many(myquery)
            resp = collection.delete_one({'_id':ObjectId(request_data['id'])})
            mongo_db_client.close()
            if resp:
                return resp.deleted_count
            else:
                return 0
        except Exception as e:
            return -2