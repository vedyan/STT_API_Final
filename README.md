Description:

This Flask application leverages Deepgram for real-time speech-to-text conversion. Users can interact with the application to record their speech, which is then transcribed into text.
The APIs used in the provided setup instructions follow a RESTful architecture.
Below are the setup steps and instructions on how to use the application:

STEPS for setup :
1. Clone repository
2. pip install -r requirements.txt
3. obtain DEEPGRAM_API_KEY and Create a ".env" file specifying values of DEEPGRAM_API_KEY
4. python app8.py
5. navigating to http://localhost:5000

Steps for how to use :
1. Click on start recording button 
2. Navigate to Code terminal
3. Speak your content - whatever you speak will be shown is terminal as "speaker:"
4. After finishing Click on Stop recording button - all your content will be listed in "Full Transcript List" and "Full Transcript" will be displayed in Terminal - also the "text" files will be saved inside "static" folder
6. Ctrl + c  to close the app
7. if want to continue follow up from step 1

Credits :
* this app uses Deepgram for Realtime Speech to Text Conversion.
