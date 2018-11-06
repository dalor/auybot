from flask import Flask, request
from dbot import Bot, reply_markup as repl
import youtube_dl
import subprocess
import time
import os

app = Flask(__name__)

b = Bot('496285003:AAF84RjUVVhOPKrlX4etieJLBlDh53rlC-Y')

TEMP = 'temp/'

files = {}
DOWNLOAD_WAIT = 100

if not os.path.exists(TEMP):
    os.makedirs(TEMP)

ydl_opts = {
        'format': 'bestaudio/best',
        'get-url': True,
        'skip-download': True,
        'quiet': True,
        'no-warnings': True
    }

def get_params(song_url):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(song_url, download=False)
        audio_url = info_dict['url']
        title = info_dict['title']
        thumbnail = info_dict['thumbnail']
        id_ = info_dict['id']
        return id_, title, audio_url, thumbnail

def save_audio(song_url):
    id_, title, audio_url, thumbnail = get_params(song_url)
    filename = '{}{}.mp3'.format(TEMP, title)
    global files
    if id_ in files:
        for i in range(DOWNLOAD_WAIT):
            if files[id_]:
                return title
            time.sleep(1)
    else:
        files[id_] = False
        subprocess.Popen(['../ffmpeg-3.4.2-64bit-static/ffmpeg', '-i', audio_url, '-i', thumbnail, '-c', 'copy', '-map', '0', '-map', '1', '-c:a', 'libmp3lame', filename], stderr=subprocess.DEVNULL).wait()
        files[id_] = True
        return title

@b.message('.*(youtu\.be\/|youtube\.com\/watch\?v\=)([A-Za-z0-9\_\-]+).*')
def mess_down(a):
    prev_msg = a.msg('Loading...').send()['result']['message_id']
    title = save_audio(a.args[1] + a.args[2])
    prev_msg = a.editmessagetext(message_id=prev_msg, text='Sending...').send()['result']['message_id']
    a.audio(title=title, data={'audio': open('{}{}.mp3'.format(TEMP, title), 'rb')}).send()
    a.delete(prev_msg).send()

@app.route('/hook', methods=['POST']) #Telegram should be connected to this hook
def webhook():
    b.check(request.get_json())
    return 'ok', 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)