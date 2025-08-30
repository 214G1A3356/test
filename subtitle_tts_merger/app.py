from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sys
import pysrt
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from werkzeug.utils import secure_filename

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

template_dir = os.path.join(application_path, 'templates')
static_dir = os.path.join(application_path, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv', 'srt'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'video' not in request.files or 'subtitle' not in request.files:
        return redirect(request.url)
    video_file = request.files['video']
    subtitle_file = request.files['subtitle']
    if video_file.filename == '' or subtitle_file.filename == '':
        return redirect(request.url)
    if video_file and allowed_file(video_file.filename) and subtitle_file and allowed_file(subtitle_file.filename):
        video_filename = secure_filename(video_file.filename)
        subtitle_filename = secure_filename(subtitle_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        subtitle_path = os.path.join(app.config['UPLOAD_FOLDER'], subtitle_filename)
        video_file.save(video_path)
        subtitle_file.save(subtitle_path)
        return redirect(url_for('editor', video_filename=video_filename, subtitle_filename=subtitle_filename))
    return redirect(request.url)

@app.route('/editor')
def editor():
    video_filename = request.args.get('video_filename')
    subtitle_filename = request.args.get('subtitle_filename')
    if not video_filename or not subtitle_filename:
        return redirect(url_for('index'))

    subtitle_path = os.path.join(app.config['UPLOAD_FOLDER'], subtitle_filename)
    try:
        subs = pysrt.open(subtitle_path)
    except Exception as e:
        # Handle parsing errors, maybe redirect with an error message
        return redirect(url_for('index'))

    uploaded_tts_files = []
    for sub in subs:
        tts_filename = f"tts_{video_filename.rsplit('.', 1)[0]}_{sub.index}.mp3"
        tts_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], tts_filename)
        if os.path.exists(tts_audio_path):
            uploaded_tts_files.append(sub.index)

    return render_template('editor.html', subs=subs, video_filename=video_filename, subtitle_filename=subtitle_filename, uploaded_tts_files=uploaded_tts_files)

@app.route('/upload_tts/<video_filename>/<subtitle_filename>/<int:subtitle_index>', methods=['POST'])
def upload_tts(video_filename, subtitle_filename, subtitle_index):
    if 'tts_audio' not in request.files:
        return redirect(url_for('editor', video_filename=video_filename, subtitle_filename=subtitle_filename))
    tts_audio_file = request.files['tts_audio']
    if tts_audio_file.filename == '':
        return redirect(url_for('editor', video_filename=video_filename, subtitle_filename=subtitle_filename))
    if tts_audio_file:
        tts_filename = f"tts_{video_filename.rsplit('.', 1)[0]}_{subtitle_index}.mp3"
        tts_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], tts_filename)
        tts_audio_file.save(tts_audio_path)
    return redirect(url_for('editor', video_filename=video_filename, subtitle_filename=subtitle_filename))


@app.route('/generate_audio/<video_filename>/<subtitle_filename>', methods=['POST'])
def generate_audio(video_filename, subtitle_filename):
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    subtitle_path = os.path.join(app.config['UPLOAD_FOLDER'], subtitle_filename)

    # Get video duration
    try:
        video_clip = VideoFileClip(video_path)
        video_duration_ms = int(video_clip.duration * 1000)
        video_clip.close()
    except Exception as e:
        # Handle error
        return redirect(url_for('editor', video_filename=video_filename, subtitle_filename=subtitle_filename))

    # Create silent audio track
    final_audio = AudioSegment.silent(duration=video_duration_ms)

    # Parse subtitles
    subs = pysrt.open(subtitle_path)

    # Overlay TTS audio for each subtitle
    for sub in subs:
        tts_filename = f"tts_{video_filename.rsplit('.', 1)[0]}_{sub.index}.mp3"
        tts_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], tts_filename)

        if os.path.exists(tts_audio_path):
            tts_audio = AudioSegment.from_file(tts_audio_path)

            start_ms = sub.start.ordinal
            end_ms = sub.end.ordinal
            target_duration_ms = end_ms - start_ms

            if target_duration_ms > 0:
                original_duration_ms = len(tts_audio)
                if original_duration_ms > 0:
                    speed_ratio = original_duration_ms / target_duration_ms

                    adjusted_audio = tts_audio._spawn(tts_audio.raw_data, overrides={
                        "frame_rate": int(tts_audio.frame_rate * speed_ratio)
                    })

                    final_audio = final_audio.overlay(adjusted_audio, position=start_ms)

    # Export final audio
    final_audio_filename = f"final_{video_filename.rsplit('.', 1)[0]}.mp3"
    final_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], final_audio_filename)
    final_audio.export(final_audio_path, format="mp3")

    return redirect(url_for('download', filename=final_audio_filename))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
