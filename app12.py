import threading
import asyncio
from flask import Flask, jsonify, request, render_template
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Modify TranscriptCollector class
class TranscriptCollector:
    def __init__(self):
        self.full_transcript_list = []
        self.reset()

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript_list(self):
        return self.full_transcript_list

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

    def save_full_transcript(self):
        self.full_transcript_list.extend(self.transcript_parts)

transcript_collector = TranscriptCollector()
dg_connection = None

async def get_transcript():
    global dg_connection
    try:
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram: DeepgramClient = DeepgramClient("", config)

        dg_connection = deepgram.listen.asynclive.v("1")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if result.speech_final:
                transcript_collector.add_part(sentence)
                transcript_collector.save_full_transcript()
                full_transcript_list = transcript_collector.get_full_transcript_list()
                full_transcript = transcript_collector.get_full_transcript()
                print(f"speaker: {full_transcript}")
                transcript_collector.reset()

        async def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            endpointing=True
        )

        await dg_connection.start(options)

        microphone = Microphone(dg_connection.send)
        microphone.start()

        while True:
            if not microphone.is_active():
                break
            await asyncio.sleep(1)

        microphone.finish()
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

@app.route('/')
def index():
    return render_template('index12.html')

async def run_coroutine_in_loop(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    await coroutine

@app.route('/start_recording', methods=['POST'])
def start_recording():
    asyncio.run_coroutine_threadsafe(get_transcript(), loop=event_loop)
    return jsonify({'message': 'Recording started'})

@app.route('/stop_recording', methods=['POST'])
async def stop_recording():
    global dg_connection
    if dg_connection:
        try:
            await dg_connection.finish()
        except Exception as e:
            print(f"Error while finishing: {e}")

        full_transcript_list = transcript_collector.get_full_transcript_list()
        full_transcript_list = [sentence for sentence in full_transcript_list if sentence.strip()]
        full_transcript_list = [sentence.rstrip('.') for sentence in full_transcript_list]
        full_transcript = ' '.join(full_transcript_list)
        print(f"Full Transcript List: {full_transcript_list}")
        print(f"Full Transcript: {full_transcript}")

        output_file = 'static/output_{}.txt'.format(uuid.uuid4())
        with open(output_file, 'w') as file:
            file.write(f'interviewer: {full_transcript}')
        
        transcript_collector.reset()
        dg_connection = None
        return jsonify({'transcription': full_transcript})
    else:
        return jsonify({'message': 'No recording in progress'})

if __name__ == "__main__":
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    threading.Thread(target=event_loop.run_forever).start()
    app.run(host='0.0.0.0', port=port)
