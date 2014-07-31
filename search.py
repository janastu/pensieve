from flask import Flask, render_template, request, make_response
from elasticsearch import Elasticsearch
from urlparse import urlparse
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/index', methods=['POST'])
def createIndex():
    es = Elasticsearch()
    if not es.indices.exists(urlparse(request.form['url']).netloc):
        url = request.form['url']
        if not request.form['url'].endswith('/'):
            url = request.form['url'] + '/'
        try:
            contents = requests.get(url + "pages").json()
            for content in contents:
                es.index(index=urlparse(request.form['url']).netloc,
                         doc_type="html", body=content)
            response = make_response()
            response.data = "Website indexed."
            return response
        except:
            response = make_response()
            response.status_code = 204
            # response.mimetype = "application/json"
            # response.data = {"reason": "No content found."}
            return response
    else:
        response = make_response()
        response.status_code = 409
        response.data = {"reason": "Index already exists"}
        return response


@app.route("/search")
def search():
    return render_template('search.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)