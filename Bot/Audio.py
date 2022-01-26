from universal_funcs import *
import ShazamAPI
from google.cloud import speech
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file('cookiebot_cloudserviceaccount.json')
client = speech.SpeechClient(credentials=credentials)
minimum_words_STT = 3
confidence_threshold = 0.5
fandom_related_words = ['furry', 'furries', 'fursuiter', 'fandom', 'fursona', 'commission', 'yiff', 'collab', 'trade', 'exposed']
fandom_related_words_boost = 50

def Identify_music(cookiebot, msg, chat_id, content):
    shazam = ShazamAPI.Shazam(content)
    recognize_generator = shazam.recognizeSong()
    response = next(recognize_generator)
    if('track' in response[1]):
        cookiebot.sendMessage(chat_id, "MÚSICA: 🎵 " + response[1]['track']['title'] + " - " + response[1]['track']['subtitle'] + " 🎵", reply_to_message_id=msg['message_id'])

def Speech_to_text(cookiebot, msg, chat_id, sfw):
    global minimum_words_STT
    global confidence_threshold
    r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True, timeout=10)
    try:
        cookiebot.sendChatAction(chat_id, 'typing')
        if sfw == 1:
            profanityFilter = True
        else:
            profanityFilter = False
        speechContexts = speech.SpeechContext(phrases=fandom_related_words, boost=fandom_related_words_boost)
        audio = speech.RecognitionAudio(content=r.content)
        config = speech.RecognitionConfig(encoding='OGG_OPUS', sample_rate_hertz=16000, language_code="pt-BR", alternative_language_codes=["en-US"], speech_contexts=[speechContexts], enable_word_confidence=True, enable_automatic_punctuation=True, profanity_filter=profanityFilter, enable_spoken_emojis=True, use_enhanced=True,)
        response = client.recognize(config=config, audio=audio)
        Text = ''
        for i, result in enumerate(response.results):
            alternative = result.alternatives[0]
            Paragraph = alternative.transcript.capitalize()
            for word in alternative.words:
                if word.confidence < confidence_threshold:
                    Paragraph = Paragraph.replace(word.word, '(?)')
            Text += Paragraph
            if i < len(response.results) - 1:
                Text += '\n'
        if len(Text.split()) >= minimum_words_STT:
            cookiebot.sendChatAction(chat_id, 'typing')
            cookiebot.sendMessage(chat_id, '(2.1) Texto:\n"{}"'.format(Text), reply_to_message_id=msg['message_id'])
    except Exception as e:
        print(e)
    Identify_music(cookiebot, msg, chat_id, r.content)