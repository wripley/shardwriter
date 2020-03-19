# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modified from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/cloud-sql/mysql/sqlalchemy/main.py

import os
import sys
from flask import Flask, render_template, request, Response

import sqlalchemy

app = Flask(__name__)

# { "IP": <SqlAlchemyConnection> }
# Ex: { "10.103.160.3": <SqlAlchemyConnection> }
db_connections = dict()

def get_db_connection(ip_address):
    if ip_address in db_connections:
        return db_connections[ip_address]
    else:
        db_user = os.get_environ("DB_USER")
        db_pass = os.get_environ("DB_PASSWORD")
        db = sqlalchemy.create_engine(
            # Equivalent URL:
            # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
            sqlalchemy.engine.url.URL(
                drivername="mysql+pymysql",
                username=db_user,
                password=db_pass,
                host=ip_address,
                database="db"
            ),
        )
        db_connections[ip_address] = db
        return db


@app.route("/", methods=["POST"])
def shard_write():
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    print(request)
    request_json = request.get_json(silent=True)
    request_args = request.args

    print(request_json)
    print(request_json["instances"])

    db_instances = request_json["instances"]
    firstName = request_json["firstName"]
    lastName = request_json["lastName"]
    statement = sqlalchemy.text("INSERT INTO people (FirstName, LastName) VALUES (\"{}\",\"{}\");".format(firstName,lastName))
    for instance_ip in db_instances:
        # The SQLAlchemy engine will help manage interactions, including automatically
        # managing a pool of connections to your database
        db = get_db_connection(instance_ip)
        try:
            with db.connect() as connection:
                connection.execute(statement).fetchall()
        except Exception as e:
            print(e)
    return Response(
        status=200,
        response="Message written")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

