from universal_funcs import *
import ShazamAPI
import openai
openai_client = openai.OpenAI(api_key=openai_key)

def Identify_music(cookiebot, msg, chat_id, content, language):
    shazam = ShazamAPI.Shazam(content)
    recognize_generator = shazam.recognizeSong()
    try:
        response = next(recognize_generator)
    except StopIteration:
        return
    if('track' in response[1]):
        title = response[1]['track']['title']
        subtitle = response[1]['track']['subtitle']
        if language in ['pt', 'es']:
            Send(cookiebot, chat_id, f"MÚSICA: 🎵 _{title}_ \- _{subtitle}_ 🎵", msg, language)
        else:
            Send(cookiebot, chat_id, f"SONG: 🎵 _{title}_ \- _{subtitle}_ 🎵", msg, language)

def Speech_to_text(content):
    with open('stt.ogg', 'wb') as audio_file:
        audio_file.write(content)
    with open('stt.ogg', 'rb') as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
    transcript = transcript.text.capitalize()
    return transcript