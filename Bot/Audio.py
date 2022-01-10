from universal_funcs import *
import subprocess
import ShazamAPI
from google.cloud import speech
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file('cookiebot_cloudserviceaccount.json')
client = speech.SpeechClient(credentials=credentials)
minimum_words_STT = 4
confidence_threshold = 0.75

def Identify_music(cookiebot, msg, chat_id, AUDIO_FILE):
    shazam = ShazamAPI.Shazam(open(AUDIO_FILE, 'rb').read())
    recognize_generator = shazam.recognizeSong()
    response = next(recognize_generator)
    if('track' in response[1]):
        cookiebot.sendMessage(chat_id, "MÚSICA: 🎵 " + response[1]['track']['title'] + " - " + response[1]['track']['subtitle'] + " 🎵", reply_to_message_id=msg['message_id'])

def Speech_to_text(cookiebot, msg, chat_id):
    global minimum_words_STT
    global confidence_threshold
    r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True)
    open('VOICEMESSAGE.oga', 'wb').write(r.content)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', 'VOICEMESSAGE.oga', "VOICEMESSAGE.wav", '-y'])
    AUDIO_FILE = "VOICEMESSAGE.wav"
    try:
        cookiebot.sendChatAction(chat_id, 'typing')
        with open('VOICEMESSAGE.wav', "rb") as audio_file:
            content = audio_file.read()
            audio_file.close()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(language_code="pt-BR", enable_automatic_punctuation=True)
        response = client.recognize(config=config, audio=audio)
        Text = ''
        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            if alternative.confidence < confidence_threshold:
                return
            Text += alternative.transcript.capitalize()
            if i < len(response.results) - 1:
                Text += '\n'
        if len(Text.split()) >= minimum_words_STT:
            cookiebot.sendChatAction(chat_id, 'typing')
            cookiebot.sendMessage(chat_id, 'Texto:\n"{}"'.format(Text), reply_to_message_id=msg['message_id'])
    except Exception as e:
        print(e)
    Identify_music(cookiebot, msg, chat_id, AUDIO_FILE)