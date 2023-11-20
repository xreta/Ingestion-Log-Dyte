from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

app = Flask(__name__)

# Initialize Elasticsearch and PostgreSQL connections
es = Elasticsearch(["http://localhost:9200"])
conn = psycopg2.connect(dbname="logdb", user="postgres", password="1234", host="localhost")
conn.set_session(autocommit=True)

@app.route('/query', methods=['GET'])
def query_form():
    return render_template('query_form.html')

@app.route('/results', methods=['POST'])
def query_results():
    level = request.form.get('level')
    message = request.form.get('message')
    resource_id = request.form.get('resourceId')
    timestamp = request.form.get('timestamp')
    trace_id = request.form.get('traceId')
    span_id = request.form.get('spanId')
    commit = request.form.get('commit')
    parent_resource_id = request.form.get('parentResourceId')

    results = []

    # Elasticsearch query
    es_query = {"bool": {"must": []}}
    if message:
        es_query["bool"]["must"].append({"match": {"message": message}})
    if timestamp:
        es_query["bool"]["must"].append({"range": {"timestamp": {"gte": timestamp}}})

    if es_query["bool"]["must"]:
        es_response = es.search(index="logs", body={"query": es_query})
        for hit in es_response['hits']['hits']:
            hit_data = hit['_source']
            hit_data['parent_resource_id'] = hit_data.get('metadata', {}).get('parentResourceId', 'N/A')
            results.append(hit_data)

    # PostgreSQL query
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        sql_query = "SELECT *, parent_resource_id as parent_resource_id FROM logs WHERE TRUE"
        sql_params = []

        if level:
            sql_query += " AND level = %s"
            sql_params.append(level)
        if resource_id:
            sql_query += " AND resource_id = %s"
            sql_params.append(resource_id)
        if trace_id:
            sql_query += " AND trace_id = %s"
            sql_params.append(trace_id)
        if span_id:
            sql_query += " AND span_id = %s"
            sql_params.append(span_id)
        if commit:
            sql_query += " AND commit = %s"
            sql_params.append(commit)
        if parent_resource_id:
            sql_query += " AND parent_resource_id = %s"
            sql_params.append(parent_resource_id)
        if timestamp:
            try:
                datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                sql_query += " AND timestamp >= %s"
                sql_params.append(timestamp)
            except ValueError:
                pass 

        cursor.execute(sql_query, sql_params)
        records = cursor.fetchall()
        results.extend(records)

    results = [result for result in results if any(result.values())]

    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
