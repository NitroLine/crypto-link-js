import base64
import json
import random
import string
from flask import request

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from flask import Flask, send_from_directory, render_template, abort

app = Flask(__name__)

BLOCK_SIZE = 16
FILEPATH = 'channels.json'

# Use a key with sufficient entropy

def encrypt(message, key):
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(key, AES.MODE_CBC, IV)
    return base64.b64encode(IV + aes.encrypt(pad(message.encode('utf-8'), BLOCK_SIZE)))


def decrypt(encrypted, key):
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[: BLOCK_SIZE]
    aes = AES.new(key, AES.MODE_CBC, IV)
    return unpad(aes.decrypt(encrypted[BLOCK_SIZE:]), BLOCK_SIZE).decode('utf-8')


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


@app.route("/")
def index():
    stream_id = request.args.get('id', 0)
    sub_key = request.args.get('key', 0)
    with open(FILEPATH) as f:
        streams = json.load(f)
    streams = streams['channels']
    stream = None
    for st in streams:
        if str(st['id']) == stream_id:
            stream = st
    if not stream:
        abort(404)
        return {}, 404
    sub_key = int(sub_key)
    if len(stream['keys']) <= sub_key:
        abort(404)
        return {}, 404

    stream_keys = stream['keys'][sub_key]
    stream_link = stream['link']
    key = randomword(32)
    encrypted = encrypt(stream_keys, key.encode()).decode()
    print("Encrypted Base:", encrypted)
    print("Key:", key)
    return render_template('index.html', steam={
        'encrypted_keys': encrypted,
        'key': key,
        'link': stream_link,
        'title': stream['name']
    })


@app.route('/js/<path:path>')
def send_static(path):
    return send_from_directory('js', path)


if __name__ == '__main__':
    context = ('fullchain.pem', 'privkey.pem')  # certificate and key files
    app.run(ssl_context=context, host="0.0.0.0")
