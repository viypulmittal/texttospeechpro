
from flask import Flask, render_template, request, send_file
import boto3
import tempfile
import re

app = Flask(__name__)

polly_client = boto3.client('polly')

SPEAKER_VOICE_MAP = {
    'Matthew': {'VoiceId': 'Matthew', 'Engine': 'neural'},
    'Amy': {'VoiceId': 'Amy', 'Engine': 'neural'},
    'Joanna': {'VoiceId': 'Joanna', 'Engine': 'neural'},
    'Justin': {'VoiceId': 'Justin', 'Engine': 'standard'}
}

def parse_script(text):
    parts = re.split(r'(\[speaker:\w+\])', text)
    segments = []
    current_voice = 'Matthew'
    for part in parts:
        if part.startswith('[speaker:'):
            current_voice = part[9:-1]
        elif part.strip():
            segments.append((current_voice, part.strip()))
    return segments

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        segments = parse_script(text)
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        for voice, segment in segments:
            voice_cfg = SPEAKER_VOICE_MAP.get(voice, SPEAKER_VOICE_MAP['Matthew'])
            response = polly_client.synthesize_speech(
                Text=segment,
                OutputFormat='mp3',
                VoiceId=voice_cfg['VoiceId'],
                Engine=voice_cfg['Engine']
            )
            temp_audio.write(response['AudioStream'].read())
        temp_audio.close()
        return send_file(temp_audio.name, as_attachment=True, download_name="tts_output.mp3")
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
