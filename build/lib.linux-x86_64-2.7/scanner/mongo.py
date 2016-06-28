from pymongo import MongoClient

################################################################################
# MONGO DB INIT
# TODO if I want an history of values for graphs and such, I need to save all
# data incoming from nodes into the database for future use.
# TODO figure out a way to save data efficiently and in a simple-to-use manner
################################################################################

mongodb = MongoClient()
db = mongodb.net_scanner
gcm_collection = db.gcm_test

def insert_gcm(registration_id):
    print "Inserting GCM %s" % registration_id
    element = {
            "_id": registration_id
            }
    gcm_collection.insert_one(element)

def remove_gcm(registration_id):
    print "Removing GCM %s" % registration_id
    element = {
            "_id": registration_id
            }
    gcm_collection.delete_one(element)

def get_gcm_list():
    cursor = gcm_collection.find()
    reg_id_list = []
    for regid in cursor:
        print "Regid is %s" % str(regid)
        reg_id_list.append(regid['_id'])

    return reg_id_list
