from flask import Flask

app = Flask(__name__)


@app.route('/domains/', methods=['GET'])
def domain_get_all():
    return 'hi'


@app.route('/domains/<domain>', methods=['GET'])
def domain_get(domain):
    return 'hi'


@app.route('/domains/<domain>', methods=['POST'])
def domain_add(domain):
    pass


@app.route('/domains/<domain>', methods=['DELETE'])
def domain_delete(domain):
    return 'Hello'
