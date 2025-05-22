from flask import Flask, request, send_file, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__, static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    fmt = request.form['format']
    res = request.form.get('resolution', 'best')
    platform = request.form['platform']
    ext = 'mp3' if fmt == 'mp3' else 'mp4'
    filename = f"{platform}_{uuid.uuid4().hex}.{ext}"
    output_path = os.path.join("downloads", filename)

    ydl_opts = {
        'format': (
            'bestaudio' if fmt == 'mp3' else
            f'bestvideo[height<={res}]+bestaudio/best' if res != 'best' else
            'bestvideo+bestaudio/best'
        ),
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if fmt == 'mp3' else [],
        'merge_output_format': ext if fmt != 'mp3' else None,
        'noplaylist': True,
        'quiet': True
    }

    try:
        os.makedirs('downloads', exist_ok=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Lỗi khi tải video: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
