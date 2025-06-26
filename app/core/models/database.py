from pymongo import MongoClient, ReplaceOne, DESCENDING
from datetime import datetime, timedelta
import json
import pandas as pd
import traceback
import itertools
from fuzzywuzzy import fuzz
from bson import ObjectId

class DATABASE:
    def __init__(self):
        # with open('./config/mongo.json') as jsFile:
        #     mongo_dict = json.load(jsFile)
        # self.mongo_host = mongo_dict['host']
        # self.mongo_port = mongo_dict['port']
        # self.mongodb_url = MongoClient("mongodb://global_tnms:fkJmzaD0JINWr@localhost:27017/?authSource=admin&readPreference=primary&appname=mongodb-vscode%200.6.10&ssl=false")
        self.mongodb_url = MongoClient("mongodb://global_tnms:fkJmzaD0JINWr@mongo:27017/?authSource=admin&readPreference=primary&appname=mongodb-vscode%200.6.10&ssl=false")
        
        self.db = 'TNMS_Live'
    

    def insert_data(self,company,location,tollid,laneno,inout,vehicletype,vehiclesubtype,vehicleno,imagepath,videopath,time):
        database_data = {}
        similarity = 0
        try:
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehicle_detail']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}, {'laneno': laneno}]
                    }
            rec = list(collection.find(myquery, sort=[( '_id', DESCENDING )] ).limit(1))
            if rec:
                similarity = fuzz.ratio(vehicleno.lower(), rec[0].get('vehicleno').lower())
            if similarity<70 or vehicleno=='unprocessed':
                database_data['company'] = company
                database_data['location'] = location
                database_data['tollid'] = str(tollid)
                database_data['laneno'] = str(laneno)
                database_data['vehicletype'] = vehicletype
                # database_data['vehicle_subtype'] = get_vehicle_info(plateno)
                database_data['vehiclesubtype'] = vehiclesubtype
                database_data['image'] = imagepath.split('app/')[-1]
                database_data['vehicleno'] = str(vehicleno)
                database_data['time'] = time
                database_data['videoclip'] = videopath.split('app/')[-1]
                database_data['inout'] = inout
                exemptionflag = self.checkvehicleexempted(company, location, tollid, vehicleno)
                monthlypass = self.checkvehicleinmonthlypass(company, location, tollid, vehicleno)
                cvrwithindtp = self.checkvehicleincvedtp(company, location, tollid, vehicleno)
                database_data['exemptionflag'] = exemptionflag
                database_data['monthlypass'] = monthlypass
                database_data['cvrwithindtp'] = cvrwithindtp
                if exemptionflag=='Y' or monthlypass=='Y' or vehicletype=='Other':
                    database_data['fee'] = 0
                else:
                    if cvrwithindtp=='Y':
                        cvrwithindtp = True
                    else:
                        cvrwithindtp = False
                    database_data['fee'] = self.getvehiclefee(company, location, tollid, vehicletype, vehiclesubtype, cvrwithindtp)
                database_data['archived'] = False
                # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
                
                # collection.insert_many([request_data])

                # check_keys = {
                #     # 'emailid':request_data['emailid'],
                #     'vehicleno':request_data['vehicleno'],
                #     'jobid' : request_data['jobid']
                # }
                collection.insert_one(database_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            traceback.print_exc()
            return -2
    

    def reset_password(self, request_data, new_hashed_password):
        try:
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['users']

            # Updating fan quantity form 10 to 25.
            filter = {'_id':ObjectId(request_data['id'])}
            # Values to be updated.
            newvalues = { "$set": { 'password': new_hashed_password } }
            
            # Using update_one() method for single 
            # updation.
            resp = collection.update_one(filter, newvalues)
            resp = resp.modified_count
            if resp:
                return resp
            else:
                return None
        except:
            print(traceback.print_exc())

    def change_password(self, request_data, new_hashed_password):
        try:
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['users']

            # Updating fan quantity form 10 to 25.
            # filter = {'_id':ObjectId(request_data['id'])}
            filter = {
                        'company':request_data['company'],
                        'location' : request_data['location'],
                        "tollid": request_data['tollid'],
                        "email": request_data['email'],
                    }
            # Values to be updated.
            newvalues = { "$set": { 'password': new_hashed_password } }
            
            # Using update_one() method for single 
            # updation.
            resp = collection.update_one(filter, newvalues)
            resp = resp.modified_count
            if resp:
                return resp
            else:
                return None
        except:
            print(traceback.print_exc())


    def check_reset_password_token(self, reques_password_token):
        try:
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['codes']

            myquery = {
                    "$and" :[{"resetcode":reques_password_token},{"status": 1},{"expired_in":  {"$gte": (datetime.utcnow() - timedelta(days=0, minutes=10))}}]
                    }
            resp = collection.find_one(myquery)
            # print(resp)
            return resp
        except:
            print(traceback.print_exc())


    def add_user(self, request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['users']
            # collection.insert_many([request_data])
            request_data['created'] = datetime.utcnow()
            request_data['updated'] = datetime.utcnow()
            check_keys = {
                        'company':request_data['company'],
                        'location' : request_data['location'],
                        "tollid": request_data['tollid'],
                        "email": request_data['email'],
                        "group": request_data['group']
                    }
            resp = collection.replace_one(check_keys, request_data, upsert=True) 

            print(resp.raw_result)           
            mongo_db_client.close()
            if resp.upserted_id :
                return resp.upserted_id 
            else:
                return None
            # mongo_db_client.close()
            # return 0
        except Exception as e:
            print(traceback.print_exc())
            return -2

    def insertuserlogs(self, username, event):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['userlogs']
            # collection.insert_many([request_data])
            
            resp = collection.insert_one({"username":username, "datetime": datetime.utcnow(), "event": event}) 
            mongo_db_client.close()
            if resp.inserted_id :
                return resp.inserted_id 
            else:
                return None
            # mongo_db_client.close()
            # return 0
        except Exception as e:
            print(traceback.print_exc())
            return -2

    # def update_user(self, request_data):
    #     try:
    #         # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
    #         mongo_db_client = self.mongodb_url
    #         db = mongo_db_client[self.db]
    #         collection = db['users']
    #         # collection.insert_many([request_data])

    #         check_keys = {
    #                     'company':request_data['company'],
    #                     'location' : request_data['location'],
    #                     "tollid": request_data['tollid'],
    #                     "email": request_data['email'],
    #                     "group": request_data['group']
    #                 }
    #         resp = collection.replace_one(check_keys, request_data, upsert=True) 

    #         print(resp.raw_result)           
    #         mongo_db_client.close()
    #         if resp.upserted_id :
    #             return resp.upserted_id 
    #         else:
    #             return None
    #         # mongo_db_client.close()
    #         # return 0
    #     except Exception as e:
    #         print(traceback.print_exc())
    #         return -2

    def check_user(self, request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['users']
            # collection.insert_many([request_data])

            resp = collection.find_one({'username':request_data['username']})
            if resp:
                resp['_id'] = str(resp['_id'])
                resp['id'] = resp.pop('_id')
            mongo_db_client.close()
            # print(resp)
            if resp:
                return resp
            else:
                return None
            # mongo_db_client.close()
            # return 0
        except Exception as e:
            print(traceback.print_exc())
            return -2

    def updatevehicletypedata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehicletypes']
            # collection.insert_many([request_data])

            # check_keys = {
            #     # 'emailid':request_data['emailid'],
            #     'licence_plate':request_data['licence_plate'],
            #     'jobid' : request_data['jobid']
            # }
            collection.insert_many(request_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2
    def updatevehiclesubtypedata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehiclesubtypes']
            # collection.insert_many([request_data])

            # check_keys = {
            #     # 'emailid':request_data['emailid'],
            #     'licence_plate':request_data['licence_plate'],
            #     'jobid' : request_data['jobid']
            # }
            collection.insert_many(request_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2

    def updatgroupsdata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['groups']
            # collection.insert_many([request_data])

            # check_keys = {
            #     # 'emailid':request_data['emailid'],
            #     'licence_plate':request_data['licence_plate'],
            #     'jobid' : request_data['jobid']
            # }
            collection.insert_many(request_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2
    
    def updatetollfeedata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['toll_fee']
            # collection.insert_many([request_data])

            # check_keys = {
            #     # 'emailid':request_data['emailid'],
            #     'licence_plate':request_data['licence_plate'],
            #     'jobid' : request_data['jobid']
            # }
            collection.insert_many(request_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2

    # def addtollfeedata(self,request_data):
    #     try:
    #         # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
    #         mongo_db_client = self.mongodb_url
    #         db = mongo_db_client[self.db]
    #         collection = db['toll_fee']
    #         # collection.insert_many([request_data])

    #         check_keys = {
    #             'company':request_data['company'],
    #             'location' : request_data['location'],
    #             "tollid": request_data['tollid'],
    #             "vehicletype": request_data['vehicletype'],
    #             "singlejourny":request_data['singlejourny'],
    #             "retunjourney":request_data['retunjourney'],
    #             "monthlypass":request_data['monthlypass'],
    #             "commercialvehicleregisteredwithinthedistrictofplaza":request_data['commercialvehicleregisteredwithinthedistrictofplaza'],
    #             "effectivedate":request_data['effectivedate'],
    #             "tilldate":request_data['tilldate']
    #         }
    #         # request_data.pop("id")
    #         collection.replace_one(check_keys, request_data, upsert=True)

    #         # collection.insert_one(request_data)

    #         mongo_db_client.close()
    #         return 0
    #     except Exception as e:
    #         print(traceback.print_exc())
    #         return -2

    def addtollfeedata(self,request_data):
        try:
            resp = None
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['toll_fee']
            # collection.insert_many([request_data])
            request_data['tilldate'] = datetime(9999, 1, 1, 00, 00, 00)   

            myquery = {
                    "$and" :[{"company":request_data['company']},{"location":request_data['location']}, {'tollid': request_data['tollid']}, {'vehicletype': request_data['vehicletype']}, {'vehiclesubtype': request_data['vehiclesubtype']}]
                    }
            
            docs = list(collection.find(myquery).sort("effectivedate",-1))
            # print(docs)
            
            if docs:
                # print(request_data['effectivedate'].timestamp())
                # print(docs[0].get('effectivedate').timestamp())
                if request_data['effectivedate'].timestamp()>docs[0].get('effectivedate').timestamp():

                    check_keys = {
                        'company':request_data['company'],
                        'location' : request_data['location'],
                        "tollid": request_data['tollid'],
                        "vehicletype": request_data['vehicletype'],
                        "vehiclesubtype": request_data['vehiclesubtype'],
                        "singlejourny":request_data['singlejourny'],
                        "retunjourney":request_data['retunjourney'],
                        "monthlypass":request_data['monthlypass'],
                        "commercialvehicleregisteredwithinthedistrictofplaza":request_data['commercialvehicleregisteredwithinthedistrictofplaza'],
                        "effectivedate":request_data['effectivedate'],
                        "tilldate":request_data['tilldate']
                    }
                    # request_data.pop("id")
                    resp = collection.replace_one(check_keys, request_data, upsert=True)
                    resp = resp.upserted_id
                    # collection.insert_one(request_data)
                    # print(resp)
                    if resp:
                        id = docs[0].get('_id')
                        result = collection.update_one({'_id': id}, {'$set': { "tilldate" :  request_data['effectivedate']} })
                else:
                    resp = 1  

            else:
                check_keys = {
                        'company':request_data['company'],
                        'location' : request_data['location'],
                        "tollid": request_data['tollid'],
                        "vehicletype": request_data['vehicletype'],
                        "vehiclesubtype": request_data['vehiclesubtype'],
                        "singlejourny":request_data['singlejourny'],
                        "retunjourney":request_data['retunjourney'],
                        "monthlypass":request_data['monthlypass'],
                        "commercialvehicleregisteredwithinthedistrictofplaza":request_data['commercialvehicleregisteredwithinthedistrictofplaza'],
                        "effectivedate":request_data['effectivedate'],
                        "tilldate":request_data['tilldate']
                    }
                    # request_data.pop("id")
                resp = collection.replace_one(check_keys, request_data, upsert=True)
                resp = resp.upserted_id                 
            mongo_db_client.close()
            if resp:
                return resp
            else:
                return 0
        except Exception as e:
            mongo_db_client.close()
            print(traceback.print_exc())
            return -2

    def savetollfeedata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['toll_fee']
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

    def updateuserdata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['users']
            # collection.insert_many([request_data])
            check_keys = {
                # 'emailid':request_data['emailid'],
                '_id':ObjectId(request_data['id']),
            }
            request_data.pop("id")
            data = collection.find_one(check_keys)
            print(data)
            for key, item in request_data.items():
                data[key] = item
            data['updated'] = datetime.utcnow()
            resp = collection.update_one(check_keys, {"$set": data})
            if resp:
                return resp.modified_count
            # collection.insert_one(request_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            print(traceback.print_exc())
            return -2

    def deletetollfee(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['toll_fee']

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

    def updateexemptedvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['exempted_vehicles']
            # bulk = collection.initialize_unordered_bulk_op()
            # for data in request_data:
            # check_keys = {
            #             'company':request_data[0]['company'],
            #             'location' : request_data[0]['location'],
            #             "tollid": request_data[0]['tollid'],
            #             "vehicleno": request_data[0]['vehicleno'],
            # }
            requests = [ReplaceOne({
                        'company':data['company'],
                        'location' : data['location'],
                        "tollid": data['tollid'],
                        "vehicleno": data['vehicleno'],
                        }, data, upsert=True) for data in request_data]
            print(requests)
            collection.bulk_write(requests)
            mongo_db_client.close()
            return 0
        except Exception as e:
            print(traceback.print_exc())
            return -2

    def addexemptedvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['exempted_vehicles']
            # collection.insert_many([request_data])

            check_keys = {
                "company": request_data['company'],
                "location": request_data['location'],
                "tollid": request_data['tollid'],
                "vehicleno":request_data['vehicleno'],
                "vehicletype": request_data['vehicletype'],
                "vehiclesubtype":request_data['vehiclesubtype'],
                "exemptiontag":request_data['exemptiontag'],
            }
            # collection.insert_one(request_data)
            resp = collection.replace_one(check_keys, request_data, upsert=True)
            mongo_db_client.close()
            if resp:
                return resp.upserted_id
                # print(resp.upserted_id)
            else:
                return 0
            
        except Exception as e:
            return -2

    def saveexemptedvehicledata(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['exempted_vehicles']

            check_keys = {
                # 'emailid':request_data['emailid'],
                '_id':ObjectId(request_data['id']),
            }
            request_data.pop("id")
            collection.replace_one(check_keys, request_data, upsert=True)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2

    def deleteexemptedvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['exempted_vehicles']

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

    def updatemonthlypassvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['monthlypass_vehicles']
            # collection.insert_many([request_data])

            # check_keys = {
            #     # 'emailid':request_data['emailid'],
            #     'licence_plate':request_data['licence_plate'],
            #     'jobid' : request_data['jobid']
            # }
            collection.insert_many(request_data)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2

    def addmonthlypassvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['monthlypass_vehicles']
            # collection.insert_many([request_data])

            check_keys = {
                "company": request_data['company'],
                "location": request_data['location'],
                "tollid": request_data['tollid'],
                "vehicleno": request_data['vehicleno'],
                "vehicletype": request_data['vehicletype'],
                "vehiclesubtype":request_data['vehiclesubtype'],
                "startdate":request_data['startdate'],
                "enddate":request_data['enddate']
            }
            # collection.insert_one(request_data)
            resp = collection.replace_one(check_keys, request_data, upsert=True)
            mongo_db_client.close()
            if resp:
                return resp.upserted_id
            else:
                return 0
        except Exception as e:
            return -2

    def savemonthlypassvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['monthlypass_vehicles']

            check_keys = {
                # 'emailid':request_data['emailid'],
                '_id':ObjectId(request_data['id']),
            }
            request_data.pop("id")
            collection.replace_one(check_keys, request_data, upsert=True)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2


    def deletemonthlypassvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['monthlypass_vehicles']

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
            print(traceback.print_exc())
            return -2

    def getvehicletypedata(self):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehicletypes']
            docs = list(collection.find({}, {'_id': False}))
            docs = [item['vehicletype'] for item in docs]
            mongo_db_client.close()
            return docs
        except:
            print(traceback.print_exc())
            return -2

    def getvehiclesubtypedata(self):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehiclesubtypes']
            docs = list(collection.find({}, {'_id': False}))
            docs = [item['vehiclesubtype'] for item in docs]
            mongo_db_client.close()
            return docs
        except:
            print(traceback.print_exc())
            return -2

    def getgroupsdata(self):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['groups']
            docs = list(collection.find({}, {'_id': False}))
            docs = [item['groups'] for item in docs]
            mongo_db_client.close()
            return docs
        except:
            print(traceback.print_exc())
            return -2


    def getcvrdtpvehicledata(self, company, location, tollid):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['cvrwithindtp_vehicles']
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

    def addcvrdtpvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['cvrwithindtp_vehicles']
            # collection.insert_many([request_data])

            check_keys = {
                "company": request_data['company'],
                "location": request_data['location'],
                "tollid": request_data['tollid'],
                "vehicleno": request_data['vehicleno'],
                "vehicletype": request_data['vehicletype'],
                "vehiclesubtype":request_data['vehiclesubtype'],
                "startdate":request_data['startdate'],
            }
            # collection.insert_one(request_data)
            resp = collection.replace_one(check_keys, request_data, upsert=True)
            mongo_db_client.close()
            if resp:
                return resp.upserted_id
            else:
                return 0
        except Exception as e:
            return -2


    def savecvrdtpvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['cvrwithindtp_vehicles']

            check_keys = {
                # 'emailid':request_data['emailid'],
                '_id':ObjectId(request_data['id']),
            }
            request_data.pop("id")
            collection.replace_one(check_keys, request_data, upsert=True)

            mongo_db_client.close()
            return 0
        except Exception as e:
            return -2

    def deletecvrdtpvehicle(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['cvrwithindtp_vehicles']

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

    def deleteuser(self,request_data):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['users']

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

    
    def checkvehicleinmonthlypass(self, company, location, tollid, vehicleno):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['monthlypass_vehicles']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}, {'vehicleno':vehicleno}, {'status':'Valid'}]
                    }
            docs = list(collection.find(myquery))
            # for doc in docs:
            #     doc['_id'] = str(doc['_id'])
            #     doc['id'] = doc.pop('_id')
            mongo_db_client.close()
            if docs:
                return 'Y'
            else:
                return 'N'
        except:
            print(traceback.print_exc())
            return -2

    def checkvehicleexempted(self, company, location, tollid, vehicleno):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['exempted_vehicles']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}, {'vehicleno':vehicleno}, {'exemptiontag':'Y'}]
                    }
            docs = list(collection.find(myquery))
            # for doc in docs:
            #     doc['_id'] = str(doc['_id'])
            #     doc['id'] = doc.pop('_id')
            mongo_db_client.close()
            if docs:
                return 'Y'
            else:
                return 'N'
        except:
            print(traceback.print_exc())
            return None

    def checkvehicleincvedtp(self, company, location, tollid, vehicleno):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['cvrwithindtp_vehicles']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}, {'vehicleno':vehicleno}]
                    }
            docs = list(collection.find(myquery))
            # for doc in docs:
            #     doc['_id'] = str(doc['_id'])
            #     doc['id'] = doc.pop('_id')
            mongo_db_client.close()
            if docs:
                return 'Y'
            else:
                return 'N'
        except:
            print(traceback.print_exc())
            return None

    def getvehiclefee(self, company, location, tollid, vehicletype, vehiclesubtype, cvrwithindtp):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['toll_fee']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}, {'vehiclesubtype': vehiclesubtype}]
                    }
            if cvrwithindtp:
                fee = collection.find_one(myquery)['commercialvehicleregisteredwithinthedistrictofplaza']
            else:
                fee = collection.find_one(myquery)['singlejourny']
                

            mongo_db_client.close()
            if fee:
                return fee
            else:
                return 0
        except:
            print(traceback.print_exc())
            return 0

    def vehicle_details(self, company, location, tollid, laneno):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehicle_detail']
            myquery = {
                    "$and" :[{"company":company}, {"location":location}, {'tollid': tollid}, {'laneno': laneno}]
                    }
            docs = list(collection.find(myquery))
            # print(docs)
            if docs:
                for doc in docs:
                    doc['_id'] = str(doc['_id'])
                    doc['id'] = doc.pop('_id')
                df = pd.DataFrame(docs)
                df['time'] = df['time'].dt.tz_localize('UTC')
                df['time'] = df['time'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
                hrs24 = timedelta(hours=24)
                # df = df[df['time']>(datetime(2021, 8, 1, 00, 00, 00) - hrs24)]
                df = df[df['time']>(datetime.now()-hrs24)]
                # print(df)
                if not df.empty:
                    df.sort_values(by='time', ascending=False, inplace=True)
                    df["time"] = df["time"].astype(str)

                    # # find combinations that have greater than 70 match
                    # dfx = pd.DataFrame(itertools.combinations(df["vehicleno"].values, 2)).assign(
                    #     ratio=lambda d: d.apply(lambda t: fuzz.ratio(t[0], t[1]), axis=1)
                    # ).loc[lambda d: d["ratio"].gt(70)]
                    # # exclude rows that have big match to another row...
                    # df = df.loc[~df["vehicleno"].isin(dfx[1])]
                    # print(df)
                # print(dfx)
                    mongo_db_client.close()
                    return df.to_dict('records')
                else:
                    print('I am in else')
                    mongo_db_client.close()
                    return []
            
        except:
            print(traceback.print_exc())
            return -2
    def get_summary(self, company, location, tollid):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehicle_detail']
            myquery = {
                    "$and" :[{"company":company}, {"location":location}, {'tollid': tollid}]
                    }
            docs = list(collection.find(myquery, {'_id': 0}))
            # ic(docs)
            df = pd.DataFrame(docs)
            df['time'] = df['time'].dt.tz_localize('UTC')
            df['time'] = df['time'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
            hrs24 = timedelta(hours=24)
            # df = df[df['time']>(datetime(2021, 8, 1, 00, 00, 00) - hrs24)]
            df = df[df['time']>(datetime.now() - hrs24)]
            df.sort_values(by='time', ascending=True, inplace=True)
            df["time"] = df["time"].astype(str)

            # find combinations that have greater than 70 match
            dfx = pd.DataFrame(itertools.combinations(df["vehicleno"].values, 2)).assign(
                ratio=lambda d: d.apply(lambda t: fuzz.ratio(t[0], t[1]), axis=1)
            ).loc[lambda d: d["ratio"].gt(70)]
            # exclude rows that have big match to another row...
            df = df.loc[~df["vehicleno"].isin(dfx[1])]
            # print(dfx)
            dfforsummary = df[['vehicletype', 'fee']].copy()
            summarydf = dfforsummary.groupby('vehicletype').agg({'vehicletype':'count', 'fee': 'sum'}).rename(columns={'vehicletype':'count'}).reset_index().rename(columns={'vehicletype':'vehicle'})#
            summarydf.loc['Total']= summarydf.sum()
            summarydf.loc['Total', 'vehicle'] = 'Total'
            print(summarydf)
            mongo_db_client.close()
            return summarydf.to_dict('records')
        except:
            print(traceback.print_exc())
            return -2

    def gettollfeedata(self, company, location, tollid):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['toll_fee']
            myquery = {
                    "$and" :[{"company":company}, {"location":location}, {'tollid': tollid}]
                    }
            docs = list(collection.find(myquery))
            finaldf = pd.DataFrame()
            for doc in docs:
                doc['_id'] = str(doc['_id'])
                doc['id'] = doc.pop('_id')
            df = pd.DataFrame(docs)
            for vehicletype, vdf in df.groupby('vehiclesubtype'):
                finaldf = finaldf.append(vdf[vdf['effectivedate']>datetime.now()])
                tempdf = vdf[vdf['effectivedate']<datetime.now()]
                tempdf.sort_values('effectivedate', inplace=True, ascending =False)
                tempdf.reset_index(drop = True, inplace=True)
                if not tempdf.empty:
                    finaldf = finaldf.append(tempdf.loc[0])
            mongo_db_client.close()
            return finaldf.to_dict('records')
        except:
            print(traceback.print_exc())
            return -2

    def gettollfeedataforedit(self, company, location, tollid, vehicletype):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['toll_fee']
            myquery = {
                    "$and" :[{"company":company}, {"location":location}, {'tollid': tollid},  {'vehicletype': vehicletype}]
                    }
            docs = list(collection.find(myquery))
            # docs = collection.find(myquery).map(function(doc) {return {'id': doc._id.str }})
            for doc in docs:
                doc['_id'] = str(doc['_id'])
                doc['id'] = doc.pop('_id')
            # print(docs)
            mongo_db_client.close()
            return docs
        except:
            print(traceback.print_exc())
            return -2

    def getexemptedveicledata(self, company, location, tollid):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['exempted_vehicles']
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
    def getusersdata(self, requestdata):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['users']
            data = [{k: v} for k, v in requestdata.items() if v]
            myquery = {
                    "$and" :data
                    }
            docs = list(collection.find(myquery, {'password': 0}))
            for doc in docs:
                doc['_id'] = str(doc['_id'])
                doc['id'] = doc.pop('_id')
            mongo_db_client.close()
            return docs
        except:
            print(traceback.print_exc())
            return -2
    def getexemptedveicledataforedit(self, company, location, tollid, vehicleno):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['exempted_vehicles']
            myquery = {
                    "$and" :[{"company":company}, {"location":location}, {'tollid': tollid}, {'vehicleno':vehicleno}]
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


    def getmonthlypassvehicledata(self, company, location, tollid):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['monthlypass_vehicles']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}]
                    }
            docs = list(collection.find(myquery))
            if docs:
                for doc in docs:
                    doc['_id'] = str(doc['_id'])
                    doc['id'] = doc.pop('_id')
                df =pd.DataFrame(docs)
                df.loc[:, 'status'] = 'Valid'
                df.loc[df['enddate']<datetime.now(), 'status'] = 'Expired'
                mongo_db_client.close()
                print(df)
                return df.to_dict('records')
        except:
            print(traceback.print_exc())
            return -2

   

    def getmonthlypassveicledataforedit(self, company, location, tollid, vehicleno):
        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['monthlypass_vehicles']
            myquery = {
                    "$and" :[{"company":company},{"location":location}, {'tollid': tollid}, {'vehicleno': vehicleno}]
                    }
            docs = list(collection.find(myquery))
            for doc in docs:
                doc['_id'] = str(doc['_id'])
            mongo_db_client.close()
            return docs
        except:
            print(traceback.print_exc())
            return -2

    def check_vehicle(self, job_id, plateno):
        # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
        mongo_db_client = self.mongodb_url
        db = mongo_db_client[self.db]
        collection = db['vehicle_detail']
        myquery = {
                    "$and" :[{"jobid":job_id}, {'vehicleno': plateno}]
                    }
        docs = list(collection.find(myquery, {'_id': 0}))
        mongo_db_client.close()
        if docs:
            return True
        else:
            return False

    def getdashboard_data_new(self, requestdata):
        # def dashboard_data(self, requesdata):

        vehicletypemapping = {'car':"Car/Jeep/Van", 'jeep': "Car/Jeep/Van", 'van':"Car/Jeep/Van",
        'lcv':"LCV",
        'truck':"Bus/Truck", 'bus':"Bus/Truck", 
        '3axle':"Upto 3 Axle Vehicle",
        '4axle':"4 to 6 Axle", '5axle':"4 to 6 Axle", '6axle':"4 to 6 Axle",
        '7axle':"7 or more Axle",
        'exempt':"Exempted Vehicles",
        'Total': "Total"}

        cards_mapping = {"Car": "cars", "Truck": "trucks", "Bus": "trucks", "LCV":"lcv", "Other":'others'}

        try:
            # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
            mongo_db_client = self.mongodb_url
            db = mongo_db_client[self.db]
            collection = db['vehicle_detail']
            requestdata['vehicletype'] = requestdata['vehicletype']
            datefrom = {'time': {"$gte": requestdata['datefrom']}}
            dateto = {'time': {"$lte": requestdata['dateto']}}
            location = {'location':{"$in":requestdata['location']}}
            tollid = {'tollid':{"$in":requestdata['tollid']}}
            laneno = {'laneno':{"$in":requestdata['laneno']}}
            requestdata.pop('datefrom')
            requestdata.pop('dateto')
            requestdata.pop('location')
            requestdata.pop('tollid')
            requestdata.pop('laneno')
            data = [{k: v} for k, v in requestdata.items() if v]
            data.append(location)
            data.append(tollid)
            data.append(laneno)
            data.append(datefrom)
            data.append(dateto)
            print(data)
            # myquery = requestdata.items()
            myquery = {"$and":data}
            # if laneno and not vehicleno and not vehicletype and not vehiclesubtype and not datefrom and not dateto:
            # myquery = {{"company":company}, {"location":location}, {'tollid': tollid}, {'laneno': laneno}}
            docs = list(collection.find(myquery))
            if docs:
                for doc in docs:
                    doc['_id'] = str(doc['_id'])
                    doc['id'] = doc.pop('_id')
                df = pd.DataFrame(docs)
                print(df)
                df['time'] = df['time'].dt.tz_localize('UTC')
                df['time'] = df['time'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
                df.sort_values(by='time', ascending=True, inplace=True)
                df["time"] = df["time"].astype(str)

                # if len(docs)>1:
                # # find combinations that have greater than 70 match
                #     dfx = pd.DataFrame(itertools.combinations(df["vehicleno"].values, 2)).assign(
                #         ratio=lambda d: d.apply(lambda t: fuzz.ratio(t[0], t[1]), axis=1)
                #     ).loc[lambda d: d["ratio"].gt(70)]
                #     # exclude rows that have big match to another row...
                #     df = df.loc[~df["vehicleno"].isin(dfx[1])]
                #     print(dfx)
                dfforsummary = df[['vehiclesubtype', 'fee']].copy()
                # dfforsummary['vehiclesubtype'] = dfforsummary['vehicletype'].map(vehicletypemapping)
                summarydf = dfforsummary.groupby('vehiclesubtype').agg({'vehiclesubtype':'count', 'fee': 'sum'}).rename(columns={'vehiclesubtype':'count'}).reset_index().rename(columns={'vehiclesubtype':'vehicle'})#
                summarydf.loc['Total']= summarydf.sum()
                summarydf.loc['Total', 'vehicle'] = 'Total'
                print(summarydf)
                forcardsdf = df[['vehicletype', 'fee']].copy()
                forcardsdf['vehicletype'] = forcardsdf['vehicletype'].map(cards_mapping)
                forcardsdf = forcardsdf.groupby('vehicletype').agg({'vehicletype':'count'}).rename(columns={'vehicletype':'count'}).reset_index().rename(columns={'vehicletype':'vehicle'})#
                forcardsdf.loc['Total']= forcardsdf.sum()
                forcardsdf.loc['Total', 'vehicle'] = 'Total Vehicles'
                print(forcardsdf)
                mongo_db_client.close()
                # print(df)
                # print(summarydf)
                # print(forcardsdf)
                return df.to_dict('records'), summarydf.to_dict('records'), forcardsdf.to_dict('records')
            else:
                mongo_db_client.close()
                return [{
                            "jobid": "NA",
                            "company": requestdata['company'],
                            "location": requestdata['location'],
                            "tollid": requestdata['tollid'],
                            "laneno": requestdata['laneno'],
                            "vehicletype": "NA",
                            "vehiclesubtype": "NA",
                            "image": "NA",
                            "vehicleno": "NA",
                            "time": "NA",
                            "videoclip": "NA",
                            "fee": 0,
                            "inout": "NA",
                            "exemptionflag": "NA",
                            "monthlypass": "NA",
                            "cvrwithindtp": "NA"
                            }
                        ], [
                            {
                            "vehicle": "NA",
                            "count": 0,
                            "fee": 0
                            },
                            {
                            "vehicle": "Total",
                            "count": 0,
                            "fee": 0
                            }
                        ], [
                            {
                            "vehicle": "cars",
                            "count": 0
                            },
                            {
                            "vehicle": "trucks",
                            "count": 0
                            },
                            {
                            "vehicle": "Total Vehicles",
                            "count": 0
                            }
                        ]
        except:
            print(traceback.print_exc())
            return -2, -2, -2

    def getdashboard_data(self, requestdata):
            # def dashboard_data(self, requesdata):

            vehicletypemapping = {'car':"Car/Jeep/Van", 'jeep': "Car/Jeep/Van", 'van':"Car/Jeep/Van",
            'lcv':"LCV",
            'truck':"Bus/Truck", 'bus':"Bus/Truck", 
            '3axle':"Upto 3 Axle Vehicle",
            '4axle':"4 to 6 Axle", '5axle':"4 to 6 Axle", '6axle':"4 to 6 Axle",
            '7axle':"7 or more Axle",
            'exempt':"Exempted Vehicles",
            'Total': "Total"}

            cards_mapping = {"Car": "cars", "Truck": "trucks", "Bus": "trucks", "LCV":"lcv", "Other":'others'}

            try:
                # mongo_db_client = MongoClient(self.mongo_host, self.mongo_port)
                mongo_db_client = self.mongodb_url
                db = mongo_db_client[self.db]
                collection = db['vehicle_detail']
                requestdata['vehicletype'] = requestdata['vehicletype']
                datefrom = {'time': {"$gte": requestdata['datefrom']}}
                dateto = {'time': {"$lte": requestdata['dateto']}}
                requestdata.pop('datefrom')
                requestdata.pop('dateto')
                data = [{k: v} for k, v in requestdata.items() if v]
                data.append(datefrom)
                data.append(dateto)
                # myquery = requestdata.items()
                myquery = {"$and":data}
                # if laneno and not vehicleno and not vehicletype and not vehiclesubtype and not datefrom and not dateto:
                # myquery = {{"company":company}, {"location":location}, {'tollid': tollid}, {'laneno': laneno}}
                docs = list(collection.find(myquery))
                if docs:
                    for doc in docs:
                        doc['_id'] = str(doc['_id'])
                        doc['id'] = doc.pop('_id')
                    df = pd.DataFrame(docs)
                    print(df)
                    df['time'] = df['time'].dt.tz_localize('UTC')
                    df['time'] = df['time'].dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
                    df.sort_values(by='time', ascending=True, inplace=True)
                    df["time"] = df["time"].astype(str)

                    # if len(docs)>1:
                    # # find combinations that have greater than 70 match
                    #     dfx = pd.DataFrame(itertools.combinations(df["vehicleno"].values, 2)).assign(
                    #         ratio=lambda d: d.apply(lambda t: fuzz.ratio(t[0], t[1]), axis=1)
                    #     ).loc[lambda d: d["ratio"].gt(70)]
                    #     # exclude rows that have big match to another row...
                    #     df = df.loc[~df["vehicleno"].isin(dfx[1])]
                    #     print(dfx)
                    dfforsummary = df[['vehiclesubtype', 'fee']].copy()
                    # dfforsummary['vehiclesubtype'] = dfforsummary['vehicletype'].map(vehicletypemapping)
                    summarydf = dfforsummary.groupby('vehiclesubtype').agg({'vehiclesubtype':'count', 'fee': 'sum'}).rename(columns={'vehiclesubtype':'count'}).reset_index().rename(columns={'vehiclesubtype':'vehicle'})#
                    summarydf.loc['Total']= summarydf.sum()
                    summarydf.loc['Total', 'vehicle'] = 'Total'
                    print(summarydf)
                    forcardsdf = df[['vehicletype', 'fee']].copy()
                    forcardsdf['vehicletype'] = forcardsdf['vehicletype'].map(cards_mapping)
                    forcardsdf = forcardsdf.groupby('vehicletype').agg({'vehicletype':'count'}).rename(columns={'vehicletype':'count'}).reset_index().rename(columns={'vehicletype':'vehicle'})#
                    forcardsdf.loc['Total']= forcardsdf.sum()
                    forcardsdf.loc['Total', 'vehicle'] = 'Total Vehicles'
                    print(forcardsdf)
                    mongo_db_client.close()
                    # print(df)
                    # print(summarydf)
                    # print(forcardsdf)
                    return df.to_dict('records'), summarydf.to_dict('records'), forcardsdf.to_dict('records')
                else:
                    mongo_db_client.close()
                    return [{
                                "jobid": "NA",
                                "company": requestdata['company'],
                                "location": requestdata['location'],
                                "tollid": requestdata['tollid'],
                                "laneno": requestdata['laneno'],
                                "vehicletype": "NA",
                                "vehiclesubtype": "NA",
                                "image": "NA",
                                "vehicleno": "NA",
                                "time": "NA",
                                "videoclip": "NA",
                                "fee": 0,
                                "inout": "NA",
                                "exemptionflag": "NA",
                                "monthlypass": "NA",
                                "cvrwithindtp": "NA"
                                }
                            ], [
                                {
                                "vehicle": "NA",
                                "count": 0,
                                "fee": 0
                                },
                                {
                                "vehicle": "Total",
                                "count": 0,
                                "fee": 0
                                }
                            ], [
                                {
                                "vehicle": "cars",
                                "count": 0
                                },
                                {
                                "vehicle": "trucks",
                                "count": 0
                                },
                                {
                                "vehicle": "Total Vehicles",
                                "count": 0
                                }
                            ]
            except:
                print(traceback.print_exc())
                return -2, -2, -2

        