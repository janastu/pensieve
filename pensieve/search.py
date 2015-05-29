from flask import Flask, render_template, request, make_response, jsonify
from elasticsearch import Elasticsearch
from urlparse import urlparse
from flask_cors import cross_origin
from logging import FileHandler
import json
import logging
import requests
import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/index/mouchak', methods=['POST'])
def createIndex():
    """This endpoint should be used to index pages of a Mouchak installation.
    FIXME:
    - Endpoint is only accessible from the index page of search service.
    - Does not support cross origin requests.
    - Better name for the function.

    """
    es = Elasticsearch()
    if not es.indices.exists(urlparse(request.form['url']).netloc):
        url = request.form['url']
        if not request.form['url'].endswith('/'):
            url = request.form['url'] + '/'
        try:
            contents = requests.get(url + "pages").json()
            for content in contents:
                es.index(index=urlparse(request.form['url']).netloc,
                         doc_type="html", body=content, id=content['id'])
            response = make_response()
            response.data = "Website indexed."
            return response
        except:
            response = make_response()
            response.status_code = 204
            return response
    else:
        response = make_response()
        response.status_code = 409
        response.data = {"reason": "Index already exists"}
        return response


@app.route('/index/content', methods=['POST'])
@cross_origin()
def indexContent():
    """API to index data from sources other than Mouchak.  Accepts list of key
    value pairs. The list is a value for a key named records.

    """
    es = Elasticsearch()
    data = request.get_json()
    url = data.get('url')
    if not url.endswith('/'):
        url = url + '/'
    try:
        contents = data.get('records')
        for record in contents:
            es.index(index=urlparse(url).netloc,
                     doc_type="json", body=record)
        response = make_response()
        response.data = "Data indexed."
        return response
    except:
        response = make_response()
        response.status_code = 500
        return response


@app.route("/update", methods=['POST'])
@cross_origin()
def update():
    es = Elasticsearch()
    es.index(index=request.form['index'],
             doc_type=request.form['doc_type'],
             body=json.loads(request.form['content']),
             id=request.form['id'])
    response = make_response()
    response.data = "Updated."
    return response


@app.route("/search")
def search():
    return render_template('search.html')


@app.route("/search/<string:index>/<string:doc_type>", methods=['GET'])
@cross_origin()
def searchByParams(index, doc_type):
    es = Elasticsearch()
    start = request.args.get('from') or 0
    size = request.args.get('size') or 10
    if 'type' in request.args:
        query = es.search(index, doc_type, body={'query':
                                                 {'prefix':
                                                  {request.args['type']:
                                                   request.args['q']}}},
                          from_=start, size=size)
    else:
        query = es.search(index, doc_type, q=request.args.get('q'),
                          default_operator='AND', size=size, from_=start)

    return jsonify(query['hits'])


@app.route("/hits/<string:index>/<string:doc_type>")
@cross_origin()
def getHits(index, doc_type):
    es = Elasticsearch()
    query_body = {"size": 0,
                  "aggs":
                  {"grouped_by":
                   {
                       "terms":
                       {
                           "field": request.args['field'],
                           "size": 0
                       }}}}
    query = es.search(index, doc_type, body=query_body)
    return jsonify(query['aggregations'])


fil = FileHandler(os.path.join(os.path.dirname(__file__), 'logme'), mode='a')
fil.setLevel(logging.ERROR)
app.logger.addHandler(fil)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
