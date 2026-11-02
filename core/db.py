import pymongo
from django.conf import settings
from bson import ObjectId

_client = None

def get_db():
    global _client
    if _client is None:
        _client = pymongo.MongoClient(settings.MONGODB_URI)
    return _client[settings.MONGODB_NAME]

def get_users_collection():
    return get_db()['users']

def get_skills_collection():
    return get_db()['skills']

def get_appointments_collection():
    return get_db()['appointments']

def serialize_doc(doc):
    """Helper to convert MongoDB document _id to string id."""
    if not doc:
        return doc
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        res = {}
        for k, v in doc.items():
            if k == '_id':
                res['id'] = str(v)
            elif isinstance(v, ObjectId):
                res[k] = str(v)
            elif isinstance(v, dict):
                res[k] = serialize_doc(v)
            elif isinstance(v, list):
                res[k] = [serialize_doc(i) for i in v]
            else:
                res[k] = v
        return res
    return doc
