from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests as r

app = Flask(__name__, template_folder='templates')
load_dotenv()
api = os.getenv('API_KEY')
url = "https://api.real-debrid.com/rest/1.0/"
headers = {'Authorization': 'Bearer '+api}

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Hello World"

@app.route('/torrents')
def torrents():
    res = get_torrents()
    return render_template('index.html', res=res)

@app.route('/info/<id>')
def info(id):
    res = info_torrents(id)
    return render_template('info.html', res=res)

@app.route('/link/')
def link():
    param = request.args.get('link')
    res = check_link(param)
    print(res)
    return render_template('link.html', res=res)

def get_torrents():
    res = r.get(url+"torrents", headers=headers).json()
    return res

def info_torrents(id):
    res = r.get(url+"torrents/info/"+id, headers=headers).json()
    for i in res['files']:
        if i['selected'] == 0:
            res['files'].remove(i)
    return res

def check_link(link):
    data = {}
    res = r.post(url+"unrestrict/check", data=f"link={link}", headers=headers).json()
    data['filename'] = res['filename']
    data['filesize'] = res['filesize']
    data['streamable'] = 0
    if res['supported'] == 1:
        unrestrict = r.post(url+"unrestrict/link", data=f"link={link}", headers=headers).json()
        data['link'] = unrestrict['download']
        data['id'] = unrestrict['id']
        if unrestrict['streamable'] == 1:
            data['streamable'] = 1
            print(unrestrict['id'])
            stream = r.get(url+f"streaming/transcode/{unrestrict['id'][:-2]}", headers=headers).json()
            data['stream'] = stream
    return data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')