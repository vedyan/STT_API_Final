from flask import Flask, jsonify, request, render_template
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions, Microphone
import asyncio
import os

app = Flask(__name__)

os.environ["DEEPGRAM_API_KEY"] = "c575e6d5bf710b102f05d9af5e745d634b150975"

# Modify TranscriptCollector class
class TranscriptCollector:
    def __init__(self):
        self.reset()
        # self.last_processed_sentence = None

    def reset(self):
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript_list(self):
        return self.transcript_parts

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts)

transcript_collector = TranscriptCollector()
dg_connection = None  # Global variable to hold the connection

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
                full_transcript_list = transcript_collector.get_full_transcript_list()
                full_transcript = transcript_collector.get_full_transcript()
                print(f"speaker: {full_transcript}")
                # transcript_collector.reset()
                # Return full transcript list if needed elsewhere
                return full_transcript_list
        ...
        # async def on_message(self, result, **kwargs):
        #     sentence = result.channel.alternatives[0].transcript
        #     if result.speech_final:
        #         if sentence != self.last_processed_sentence:
        #             transcript_collector.add_part(sentence)
        #             full_transcript_list = transcript_collector.get_full_transcript_list()
        #             full_transcript = transcript_collector.get_full_transcript()
        #             print(f"speaker: {full_transcript}")
        #             self.last_processed_sentence = sentence
        #             return full_transcript_list



        ...

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
    return render_template('index7.html')
@app.route('/start_recording', methods=['POST'])
def start_recording():
    asyncio.run(get_transcript())
    return jsonify({'message': 'Recording started'})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global dg_connection
    if dg_connection:
        dg_connection.finish()
        full_transcript_list = transcript_collector.get_full_transcript_list()
        full_transcript = transcript_collector.get_full_transcript()
        print(f"Full Transcript List: {full_transcript_list}")
        print(f"Full Transcript: {full_transcript}")
        transcript_collector.reset()
        dg_connection = None
        
        return jsonify({'message': 'Recording stopped'})
    else:
        return jsonify({'message': 'No recording in progress'})
    

if __name__ == "__main__":
    app.run(debug=True)