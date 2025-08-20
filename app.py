from flask import Flask, request, send_file, jsonify
import os
import tempfile
import random
from werkzeug.utils import secure_filename
import subprocess
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

@app.route('/')
def home():
    return jsonify({
        'status': 'Anime Recap Backend Running',
        'version': '1.0'
    })

@app.route('/process', methods=['POST'])
def process_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file'}), 400
        
        file = request.files['video']
        duration = int(request.form.get('duration', 60))
        
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(input_path)
        
        output_path = os.path.join(temp_dir, 'recap_clip.mp4')
        
        # Simple processing - extract random segment
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'csv=p=0', input_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        video_duration = float(result.stdout.strip())
        
        max_start = max(0, video_duration - duration)
        start_time = random.uniform(0, max_start)
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-ss', str(start_time), '-t', str(duration),
            '-c:v', 'libx264', '-c:a', 'aac',
            '-preset', 'ultrafast', output_path
        ]
        subprocess.run(cmd, check=True)
        
        return send_file(output_path, as_attachment=True, download_name='anime_recap.mp4')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
