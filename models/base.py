import os
import json
from pynamodb.models import Model
from typing import Dict
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from dotenv import load_dotenv

class NotFoundException(Exception):
    pass

class Credentials:
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY')
    aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
    aws_session_token =  os.environ.get('AWS_SECRET_KEY')
    hostname = 'http://{hostname}:{port}'.format(hostname = os.environ.get('AWS_HOSTNAME'), port = os.environ.get('AWS_PORT'))
    host = os.environ.get('AWS_HOSTNAME') 
    port = os.environ.get('AWS_PORT')
    region = os.environ.get('AWS_REGION')

class PynamoCrud:
    @classmethod
    def first(cls, key, condition=None):
        found = None
        for f in cls.query(key, condition):
            found = f
            break
        if found is None:
            raise NotFoundException()
        return found

    def set_attributes(self, values: Dict):
        for k, v in values.items():
            if hasattr(self, k):
                if type(v) == dict:
                    value = setattr(self, k, json.dumps(v))
                else:
                    value = setattr(self, k, v)
        return self

class Route(Model, PynamoCrud):
    """
    A DynamoDB Namespace
    """
    class Meta(Credentials):
        table_name = 'dynamodb-route'
        aws_access_key_id = Credentials.aws_access_key_id
        aws_secret_access_key = Credentials.aws_secret_access_key
        aws_session_token = Credentials.aws_session_token
        region = Credentials.region
        host = Credentials.host
        port = Credentials.port

    uuid = UnicodeAttribute(range_key=True)
    namespace_uuid = UnicodeAttribute(hash_key=True)
    path = UnicodeAttribute()
    status_code = NumberAttribute()
    headers = UnicodeAttribute()
    body = UnicodeAttribute()
    verb = UnicodeAttribute()

    @property
    def curl_command(self):
        url = "http://localhost:8000/{}/{}".format(self.namespace_uuid, self.path)
        return "curl -X {verb} {url}".format(verb = self.verb, url=url)

class Namespace(Model, PynamoCrud):
    """
    A DynamoDB Namespace
    """
    class Meta(Credentials):
        table_name = 'dynamodb-namespace'
        aws_access_key_id = Credentials.aws_access_key_id
        aws_secret_access_key = Credentials.aws_secret_access_key
        aws_session_token = Credentials.aws_session_token
        region = Credentials.region
        host = Credentials.host
        port = Credentials.port

    print('data_cred_access_key: {cred_access_key}'.format(cred_access_key = Meta.aws_access_key_id))
    uuid = UnicodeAttribute(hash_key=True)

    def get_routes(self):
        return Route.query(self.uuid)

# Create the tables
if __name__ == "__main__":
    load_dotenv()
    Credentials.aws_access_key_id = os.environ.get('AWS_ACCESS_KEY')
    Credentials.aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
    Credentials.host = os.environ.get('AWS_HOSTNAME') 
    Credentials.port = os.environ.get('AWS_PORT')
    Credentials.region = os.environ.get('AWS_REGION')
    Namespace.create_table(read_capacity_units=1, write_capacity_units=1)
    Route.create_table(read_capacity_units=1, write_capacity_units=1)
