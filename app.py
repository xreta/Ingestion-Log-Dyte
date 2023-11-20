from flask import Flask, request, jsonify
import jsonschema
from jsonschema import validate
import pika
import json
from elasticsearch import Elasticsearch
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

conn = psycopg2.connect(
    dbname="logdb",
    user="postgres",
    password="1234",
    host="localhost"
)
cursor = conn.cursor()

log_schema = {
    "type": "object",
    "properties": {
        "level": {"type": "string"},
        "message": {"type": "string"},
        "resourceId": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "traceId": {"type": "string"},
        "spanId": {"type": "string"},
        "commit": {"type": "string"},
        "metadata": {"type": "object"},
    },
    "required": ["level", "message", "timestamp"]
}

# {
# 	"level": "error",
# 	"message": "Failed to connect to DB",
#     "resourceId": "server-1234",
# 	"timestamp": "2023-09-15T08:00:00Z",
# 	"traceId": "abc-xyz-123",
#     "spanId": "span-456",
#     "commit": "5e5342f",
#     "metadata": {
#         "parentResourceId": "server-0987"
#     }
# }


def add_log_to_postgres(log_data):
    query = sql.SQL(
        "INSERT INTO logs (level, message, resource_id, timestamp, trace_id, span_id, commit, parent_resource_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cursor.execute(query, (
        log_data['level'],
        log_data['message'],
        log_data['resourceId'],
        log_data['timestamp'],
        log_data['traceId'],
        log_data['spanId'],
        log_data['commit'],
        log_data.get('metadata', {}).get('parentResourceId')
    ))
    conn.commit()

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='logQueue')

es = Elasticsearch(["http://localhost:9200"])

def add_log_to_elasticsearch(log_data):
    es.index(index="logs", body=log_data)

@app.route('/logs', methods=['POST'])
def ingest_log():
    log_data = request.get_json()
    try:
        validate(instance=log_data, schema=log_schema)
        es_response = add_log_to_elasticsearch(log_data)
        add_log_to_postgres(log_data)
        return jsonify({"message": "Log ingested successfully", "elasticsearch": es_response}), 200
    except jsonschema.exceptions.ValidationError as err:
        return jsonify({"error": "Validation error", "details": str(err)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to ingest log", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000)
