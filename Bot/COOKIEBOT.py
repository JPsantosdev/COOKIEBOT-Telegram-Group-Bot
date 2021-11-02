WolframAPP_ID = ''
googleAPIkey = ''
searchEngineCX = ''
cookiebotTOKEN = ''
#bombotTOKEN = ''
import math, os, subprocess, sys, random, json, requests, datetime, time, re, threading, traceback
from captcha.image import ImageCaptcha
import googletrans
import google_images_search, io, PIL
import speech_recognition, ShazamAPI, wolframalpha, unidecode
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
#install telepota instead of telepot, googletrans==3.1.0a0 instead of googletrans
captcha = ImageCaptcha()
translator = googletrans.Translator()
googleimagesearcher = google_images_search.GoogleImagesSearch(googleAPIkey, searchEngineCX, validate_images=False)
recognizer = speech_recognition.Recognizer()
WolframCLIENT = wolframalpha.Client(WolframAPP_ID)
cookiebot = telepot.Bot(cookiebotTOKEN)
mekhyID = 780875868
threads = list()
lastmessagedate, lastmessagetime = "1-1-1", "0"
sentcooldownmessage = False
publisher_threads, publisher_minimum_msggap = {}, 100
publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions = 1, 0, 1, 5, 600, 300, 1, 1
listaadmins, listaadmins_id = [], []

#IGNORE UPDATES PRIOR TO BOT ACTIVATION
updates = cookiebot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    cookiebot.getUpdates(offset=last_update_id+1)

#WAIT FOR ANOTHER THREAD/SCRIPT TO FINISH USING FILE
def wait_open(filename):
    if os.path.exists(filename):
        while True:
            try:
                text = open(filename, 'r')
                text.close()
                break
            except IOError:
                pass

#STRING IN FILE CHECKER
def check_if_string_in_file(file_name, string_to_search):
    for line in file_name:
        if string_to_search in line:
            return True
    return False
    

def PublishPublisher(msg_id, chat_id, sender_id):
    publisher_threads[chat_id].remove(msg_id)
    if chat_id == -1001499400382:
        cookiebot.forwardMessage(chat_id, sender_id, msg_id)
        cookiebot.sendMessage(sender_id, "--Mensagem {} enviada para grupo {}--".format(msg_id, chat_id))

def ReceivePublisher(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Por quantos dias vc gostaria que a sua messagem fosse enviada?\nCertifique-se de que o seu contato está na mensagem!", reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text="0 (É URGENTE!)",callback_data='0 PUBLISHER {}'.format(str(msg['message_id'])))], 
                                   [InlineKeyboardButton(text="1 Dia (Amanhã)",callback_data='1 PUBLISHER {}'.format(str(msg['message_id'])))],
                                   [InlineKeyboardButton(text="3 Dias",callback_data='3 PUBLISHER {}'.format(str(msg['message_id'])))], 
                                   [InlineKeyboardButton(text="5 Dias",callback_data='5 PUBLISHER {}'.format(str(msg['message_id'])))],
                                   [InlineKeyboardButton(text="Uma Semana",callback_data='7 PUBLISHER {}'.format(str(msg['message_id'])))]
                               ]))

def SpawnThreadsPublisher(chat_id):
    wait_open("Publish_Queue.txt")
    wait_open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt")
    with open("Publish_Queue.txt", 'r') as publish_queue:
        with open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt", 'r') as yesterdaytext:
            messages_yesterday = yesterdaytext.readlines()
            posts_in_queue = publish_queue.readlines()[1:]
            number_posts = math.floor(len(messages_yesterday)/publisher_minimum_msggap) - 1
            if number_posts <= 0 and len(messages_yesterday) > 0:
                number_posts = 1
            for n in range(min(number_posts, len(posts_in_queue))):
                msg_id = int(posts_in_queue[n].split()[0])
                sender_id = int(posts_in_queue[n].split()[1])
                x = datetime.datetime.now()
                y = datetime.datetime.strptime(messages_yesterday[round((n + 1) * (math.floor(len(messages_yesterday)/(number_posts+1))))], "%Y-%m-%d %H:%M:%S.%f\n")
                y = y + datetime.timedelta(days=1)
                delta_t = (y - x).seconds
                publisher_threads[chat_id].append(msg_id)
                threading.Timer(delta_t, PublishPublisher, args=(msg_id, chat_id, sender_id)).start()
                print("Publisher thread on group {} set to {} seconds from now".format(chat_id, delta_t))
        yesterdaytext.close()
    publish_queue.close()

def CheckCAS(msg, chat_id):
    r = requests.get("https://api.cas.chat/check?user_id={}".format(msg['new_chat_participant']['id']))
    in_banlist = json.loads(r.text)['ok']
    if in_banlist == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        cookiebot.sendMessage(chat_id, "Bani o usuário recém-chegado por ser flagrado pelo sistema anti-ban CAS https://cas.chat/")
        return True
    return False


def CheckRaider(msg, chat_id):
    r = requests.post('https://burrbot.xyz/noraid.php', data={'id': '{}'.format(msg['new_chat_participant']['id'])})
    is_raider = json.loads(r.text)['raider']
    if is_raider == True:
        cookiebot.kickChatMember(chat_id, msg['new_chat_participant']['id'])
        cookiebot.sendMessage(chat_id, "Bani o usuário recém-chegado por ser flagrado como raider em outros chats\n\nSe isso foi um erro, favor entrar em contato com um administrador do grupo.")
        return True
    return False

def Captcha(msg, chat_id):
    caracters = ['0', '2', '3', '4', '5', '6', '8', '9']
    password = random.choice(caracters)+random.choice(caracters)+random.choice(caracters)+random.choice(caracters)
    captcha.write(password, 'CAPTCHA.png')
    photo = open('CAPTCHA.png', 'rb')
    captchaspawnID = cookiebot.sendPhoto(chat_id, photo, caption="Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo te removerei do chat\n(OBS: Se não aparecem 4 digitos, abra a foto completa)".format(str(round(captchatimespan/60))), reply_to_message_id=msg['message_id'], reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ADMINS: Aprovar",callback_data='CAPTCHA')]]))['message_id']
    photo.close()
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + " " + password + " " + str(captchaspawnID) + "\n")
    text.close()

def CheckCaptcha(msg, chat_id):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            #CHATID userID 2021-05-13 11:45:29.027116 password captcha_id
            year = int(line.split()[2].split("-")[0])
            month = int(line.split()[2].split("-")[1])
            day = int(line.split()[2].split("-")[2])
            hour = int(line.split()[3].split(":")[0])
            minute = int(line.split()[3].split(":")[1])
            second = float(line.split()[3].split(":")[2])
            captchasettime = (hour*3600) + (minute*60) + (second)
            chat = int(line.split()[0])
            user = int(line.split()[1])
            if chat == chat_id and captchasettime+captchatimespan <= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                cookiebot.kickChatMember(chat, user)
                cookiebot.sendMessage(chat, "Bani o usuário com id {} por não solucionar o captcha a tempo.\nSe isso foi um erro, peça para um staff adicioná-lo de volta".format(user))
                cookiebot.deleteMessage((line.split()[0], line.split()[5]))
            elif chat == chat_id and user == msg['from']['id']:
                text.write(line)
                try:
                    cookiebot.deleteMessage(telepot.message_identifier(msg))
                except Exception as e:
                    print(e)
            else:    
                text.write(line)
        else:
            pass
    text.close()

def SolveCaptcha(msg, chat_id, button):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Captcha.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 5:
            if str(chat_id) == line.split()[0] and button == True:
                cookiebot.sendChatAction(chat_id, 'typing')
                cookiebot.sendMessage(chat_id, "Parabéns, você não é um robô!\nDivirta-se no chat!!\nUse o /regras para ver as regras do grupo")
                Bemvindo(msg, chat_id)
                cookiebot.deleteMessage((line.split()[0], line.split()[5]))
            elif str(chat_id) == line.split()[0] and str(msg['from']['id']) == line.split()[1]:
                cookiebot.sendChatAction(chat_id, 'typing')
                if "".join(msg['text'].upper().split()) == line.split()[4]:
                    cookiebot.sendMessage(chat_id, "Parabéns, você não é um robô!\nDivirta-se no chat!!\nUse o /regras para ver as regras do grupo")
                    Bemvindo(msg, chat_id)
                    try:
                        cookiebot.deleteMessage((line.split()[0], line.split()[5]))
                        cookiebot.deleteMessage(telepot.message_identifier(msg))
                    except Exception as e:
                        print(e)
                else:
                    cookiebot.sendMessage(chat_id, "Senha incorreta, por favor tente novamente.")
                    text.write(line)
                    try:
                        cookiebot.deleteMessage(telepot.message_identifier(msg))
                    except Exception as e:
                        print(e)
            else:
                text.write(line)
    text.close()

def Limbo(msg, chat_id):
    wait_open("Limbo.txt")
    text = open("Limbo.txt", 'a+', encoding='utf-8')
    text.write(str(chat_id) + " " + str(msg['new_chat_participant']['id']) + " " + str(datetime.datetime.now()) + "\n")
    text.close()

def CheckLimbo(msg, chat_id):
    wait_open("Limbo.txt")
    text = open("Limbo.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Limbo.txt", 'w+', encoding='utf-8')
    for line in lines:
        if len(line.split()) >= 4:
            #CHATID userID 2021-05-13 11:45:29.027116
            year = int(line.split()[2].split("-")[0])
            month = int(line.split()[2].split("-")[1])
            day = int(line.split()[2].split("-")[2])
            hour = int(line.split()[3].split(":")[0])
            minute = int(line.split()[3].split(":")[1])
            second = float(line.split()[3].split(":")[2])
            limbosettime = (hour*3600) + (minute*60) + (second)
            if str(chat_id) != line.split()[0] or str(msg['from']['id']) != line.split()[1]:
                text.write(line)
            elif datetime.date.today() == datetime.date(year, month, day) and limbosettime+limbotimespan >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                cookiebot.deleteMessage(telepot.message_identifier(msg))
                text.write(line)
            else:
                pass
        else:
            pass
    text.close()

def left_chat_member(msg, chat_id):
    wait_open("Captcha.txt")
    text = open("Captcha.txt", 'r', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Limbo.txt", 'w+', encoding='utf-8')
    for line in lines:
        if line.split()[0] != str(chat_id) or line.split()[1] != msg['left_chat_member']['id']:
            text.write(line)
    text.close()


def Sticker_anti_spam(msg, chat_id):
    wait_open("Stickers.txt")
    text_file = open("Stickers.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    if any(str(chat_id) in string for string in lines):
        pass
    else:
        lines.append("\n"+str(chat_id)+" 0")
    text_file.close()
    counter_new = 0
    for line in lines:
        if str(chat_id) in line:
            counter_new = int(line.split()[1])+1
            break
    text_file = open("Stickers.txt", "w", encoding='utf8')
    for line in lines:
        if str(chat_id) in line:
            text_file.write(line.split()[0] + " " + str(int(line.split()[1])+1) + "\n")
        else:
            text_file.write(line)
    text_file.close()
    if counter_new == stickerspamlimit:
        cookiebot.sendMessage(chat_id, "Cuidado com o flood de stickers.\nMantenham o chat com textos!")
    if counter_new > stickerspamlimit:
        cookiebot.deleteMessage(telepot.message_identifier(msg))

def Identify_music(msg, chat_id, AUDIO_FILE):
    shazam = ShazamAPI.Shazam(open(AUDIO_FILE, 'rb').read())
    recognize_generator = shazam.recognizeSong()
    response = next(recognize_generator)
    if('track' in response[1]):
        cookiebot.sendMessage(chat_id, "MÚSICA: 🎵 " + response[1]['track']['title'] + " - " + response[1]['track']['subtitle'] + " 🎵", reply_to_message_id=msg['message_id'])

def Speech_to_text(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    r = requests.get("https://api.telegram.org/file/bot{}/{}".format(cookiebotTOKEN, cookiebot.getFile(msg['voice']['file_id'])['file_path']), allow_redirects=True)
    open('VOICEMESSAGE.oga', 'wb').write(r.content)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', 'VOICEMESSAGE.oga', "VOICEMESSAGE.wav", '-y'])
    AUDIO_FILE = "VOICEMESSAGE.wav"
    try:
        with speech_recognition.AudioFile(AUDIO_FILE) as source:
            audio = recognizer.record(source)
        voicetext_ptbr = recognizer.recognize_google(audio, language="pt-BR", show_all=True)['alternative'][0]
        #voicetext_enus = recognizer.recognize_google(audio, language="en-US", show_all=True)['alternative'][0]
        Text = voicetext_ptbr['transcript'].capitalize()
        cookiebot.sendMessage(chat_id, "Texto: \n"+'"'+Text+'"', reply_to_message_id=msg['message_id'])
    except Exception as e:
        print(e)
    Identify_music(msg, chat_id, AUDIO_FILE)

def CooldownAction(msg, chat_id):
    global sentcooldownmessage
    if sentcooldownmessage == False:
        cookiebot.sendMessage(chat_id, "Você está em Cooldown!\nApenas use um comando '/' por minuto\nIsso é feito como medida de anti-spam :c\n(OBS: o cooldown foi resetado agora)", reply_to_message_id=msg['message_id'])
        sentcooldownmessage = True
    elif sentcooldownmessage == True:
        cookiebot.deleteMessage(telepot.message_identifier(msg))

def Dado(msg, chat_id):
    if msg['text'].startswith("/dado"):
        cookiebot.sendMessage(chat_id, "Rodo um dado de 1 até x, n vezes\nEXEMPLO: /d20 5\n(Roda um d20 5 vezes)")
    else:
        if len(msg['text'].split()) == 1:
            vezes = 1
        else:
            vezes = int(msg['text'].replace("@CookieMWbot", '').split()[1])
            vezes = max(min(20, vezes), 1)
        limite = int(msg['text'].replace("@CookieMWbot", '').split()[0][2:])
        resposta = "(d{}) ".format(limite)
        if vezes == 1:
            resposta += "🎲 -> {}".format(random.randint(1, limite))
        else:
            for vez in range(vezes):
                resposta += "\n{}º Lançamento: 🎲 -> {}".format(vez+1, random.randint(1, limite))
        cookiebot.sendMessage(chat_id, resposta, reply_to_message_id=msg['message_id'])

def Idade(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not " " in msg['text']:
        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer a sua idade!\n\nEx: '/idade Mekhy'\n(obs: só o primeiro nome conta)", reply_to_message_id=msg['message_id'])
    else:
        Nome = msg['text'].replace("/idade ", '').split()[0]
        response = json.loads(requests.get("https://api.agify.io?name={}".format(Nome)).text)
        Idade = response['age']
        Contagem = response['count']
        if Contagem == 0:
            cookiebot.sendMessage(chat_id, "Não conheço esse nome!", reply_to_message_id=msg['message_id'])
        else:
            cookiebot.sendMessage(chat_id, "Sua idade é {} anos! 👴\nRegistrado {} vezes".format(Idade, Contagem), reply_to_message_id=msg['message_id'])

def Genero(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if not " " in msg['text']:
        cookiebot.sendMessage(chat_id, "Digite um nome, vou dizer o seu gênero!\n\nEx: '/genero Mekhy'\n(obs: só o primeiro nome conta)\n(obs 2: POR FAVOR NÃO LEVAR ISSO A SÉRIO, É ZUERA)", reply_to_message_id=msg['message_id'])
    else:
        Nome = msg['text'].replace("/genero ", '').split()[0]
        response = json.loads(requests.get("https://api.genderize.io?name={}".format(Nome)).text)
        Genero = response['gender']
        Probabilidade = response['probability']
        Contagem = response['count']
        if Contagem == 0:
            cookiebot.sendMessage(chat_id, "Não conheço esse nome!", reply_to_message_id=msg['message_id'])
        elif Genero == 'male':
            cookiebot.sendMessage(chat_id, "É um menino! 👨\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])
        elif Genero == 'female':
            cookiebot.sendMessage(chat_id, "É uma menina! 👩\n\nProbabilidade --> {}%\nRegistrado {} vezes".format(Probabilidade*100, Contagem), reply_to_message_id=msg['message_id'])


def AtualizaBemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Welcome/Welcome_" + str(chat_id)+".txt")
    text_file = open("Welcome/Welcome_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de Boas Vindas atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    cookiebot.deleteMessage(telepot.message_identifier(msg['reply_to_message']))

def NovoBemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida quando alguém entrar no grupo", reply_to_message_id=msg['message_id'])

def Bemvindo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Welcome/Welcome_" + str(chat_id)+".txt")
    if os.path.exists("Welcome/Welcome_" + str(chat_id)+".txt"):
        with open("Welcome/Welcome_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        cookiebot.sendMessage(chat_id, regras + "\n\nATENÇÃO! Você está com funções limitadas por pelo menos {} minutos. As restrições poderão ser removidas após esse tempo se você se apresentar e se enturmar na conversa com os demais membros.".format(str(round(limbotimespan/60))))
    else:    
        cookiebot.sendMessage(chat_id, "Seja bem-vindo(a)!\n\nATENÇÃO! Você está com funções limitadas por pelo menos {} minutos. As restrições poderão ser removidas após esse tempo se você se apresentar e se enturmar na conversa com os demais membros.".format(str(round(limbotimespan/60))))

def AtualizaRegras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    text_file = open("Rules/Regras_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de regras atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    cookiebot.deleteMessage(telepot.message_identifier(msg['reply_to_message']))

def NovasRegras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida com o /regras", reply_to_message_id=msg['message_id'])

def Regras(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    if os.path.exists("Rules/Regras_" + str(chat_id)+".txt"):
        with open("Rules/Regras_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        cookiebot.sendMessage(chat_id, regras+"\n\nDúvidas em relação ao bot? Mande para @MekhyW", reply_to_message_id=msg['message_id'])
    else:    
        cookiebot.sendMessage(chat_id, "Ainda não há regras colocadas para esse grupo\nPara tal, use o /novasregras", reply_to_message_id=msg['message_id'])

def TaVivo(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Estou vivo\n\nPing enviado em:\n" + str(datetime.datetime.now()))

def Everyone(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) not in listaadmins:
        cookiebot.sendMessage(chat_id, "Você não tem permissão para chamar todos os membros do grupo.", reply_to_message_id=msg['message_id'])
    else:
        wait_open("Registers/"+str(chat_id)+".txt")
        text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf8')
        lines = text_file.readlines()
        result = ""
        for line in lines:
            username = line.split()[0]
            result += ("@"+username+" ")
        text_file.close()
        cookiebot.sendMessage(chat_id, result, reply_to_message_id=msg['message_id'])

def Adm(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    response = ""
    for admin in listaadmins:
        response += ("@" + admin + " ")
    cookiebot.sendMessage(chat_id, response, reply_to_message_id=msg['message_id'])

def Comandos(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Cookiebot functions.txt")
    text_file = open("Cookiebot functions.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    string = ""
    for line in lines:
        if len(line.split()) != 3:
            string += str(line)
    cookiebot.sendMessage(chat_id, string, reply_to_message_id=msg['message_id'])

def Hoje(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Hoje.txt")
    text_file = open("Hoje.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "Hoje pra você é dia de "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def Cheiro(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Cheiro.txt")
    text_file = open("Cheiro.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "*sniff* *sniff*\nHmmmmmm\n\nVocê está com um cheirin de "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def QqEuFaço(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Hoje.txt")
    text_file = open("Hoje.txt", "r+", encoding='utf8')
    lines = text_file.readlines()
    target = lines[random.randint(0, len(lines)-1)].replace("\\n","\n")
    cookiebot.sendMessage(chat_id, "Vai "+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def IdeiaDesenho(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    ideiasdesenho = os.listdir('IdeiaDesenho')
    ideiaID = random.randint(0, len(ideiasdesenho)-1)
    photo = open('IdeiaDesenho'+'/'+ideiasdesenho[ideiaID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, caption="Referência com ID {}\n\nNão trace sem dar créditos! (use a busca reversa do google images)".format(ideiaID), reply_to_message_id=msg['message_id'])
    photo.close()

def Contato(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, '💌 Email: felipe_catapano@yahoo.com.br\n🔵 Telegram: @MekhyW\n🟦 LinkedIn: https://www.linkedin.com/in/felipe-catapano/\n⚛️ GitHub: https://github.com/MekhyW')

def PromptQualquerCoisa(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n\nEXEMPLO: /fennec\n(acentos, letras maiusculas e espaços não funcionam)", reply_to_message_id=msg['message_id'])

def CustomCommand(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    images = os.listdir("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", ''))
    imageID = random.randint(0, len(images)-1)
    photo = open("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')+'/'+images[imageID], 'rb')
    cookiebot.sendPhoto(chat_id, photo, reply_to_message_id=msg['message_id'])
    photo.close()

def QualquerCoisa(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    searchterm = msg['text'].split("@")[0].replace("/", '').replace("@CookieMWbot", '')
    if sfw == 0:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'off', 'filetype':'jpg|png'})
    else:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'medium', 'filetype':'jpg|png'})
    for attempt in range(10):
        try:
            image = googleimagesearcher.results()[random.randint(0, len(googleimagesearcher.results())-1)]
            my_bytes_io = io.BytesIO()
            image.copy_to(my_bytes_io)
            my_bytes_io.seek(0)
            temp_img = PIL.Image.open(my_bytes_io)
            try:
                temp_img.save(my_bytes_io, format="png")
                my_bytes_io.flush()
                my_bytes_io.seek(0)
                cookiebot.sendPhoto(chat_id, ('x.png', my_bytes_io), reply_to_message_id=msg['message_id'])
            except:
                temp_img.save(my_bytes_io, format="jpg")
                my_bytes_io.flush()
                my_bytes_io.seek(0)
                cookiebot.sendPhoto(chat_id, ('x.jpg', my_bytes_io), reply_to_message_id=msg['message_id'])
            return 1
        except Exception as e:
            print(e)
    cookiebot.sendMessage(chat_id, "Não consegui achar uma imagem (ou era NSFW e eu filtrei)", reply_to_message_id=msg['message_id'])

def Quem(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    LocucaoAdverbial = random.choice(["Com certeza o(a) ", "Sem sombra de dúvidas o(a) ", "Suponho que o(a) ", "Aposto que o(a) ", "Talvez o(a) ", "Quem sabe o(a) ", "Aparentemente o(a) "])
    wait_open("Registers/"+str(chat_id)+".txt")
    text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf-8')
    lines = text_file.readlines()
    target = None
    while len(lines)>1 and target in (None, ''):
        target = lines[random.randint(0, len(lines)-1)].replace("\n", '')
        target = target.split()[0]
    cookiebot.sendMessage(chat_id, LocucaoAdverbial+"@"+target, reply_to_message_id=msg['message_id'])
    text_file.close()

def OnSay(msg, chat_id):
    if len(msg['text'].split()) > 3:
        keyword_texts = []
        for word in msg['text'].split():
            keyword_texts.append(unidecode.unidecode(''.join(filter(str.isalnum, word.lower()))))
        print(keyword_texts)
        wait_open("Onsay_Dictionary.txt")
        text_file = open("Onsay_Dictionary.txt", 'r', encoding='utf8')
        lines = text_file.readlines()
        text_file.close()
        for line in lines:
            if len(line.split(" > ")) == 2:
                queries = json.loads(line.split(" > ")[0])
                answer = line.split(" > ")[1]
                if set(queries).issubset(keyword_texts):
                    cookiebot.sendChatAction(chat_id, 'typing')
                    cookiebot.sendMessage(chat_id, answer, reply_to_message_id=msg['message_id'])
                    return True
    return False

def InteligenciaArtificial(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    message = ""
    Answer = ""
    if "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']:
        message = msg['text'].replace("Cookiebot", '').replace("cookiebot", '').replace("@CookieMWbot", '').replace("COOKIEBOT", '').replace("CookieBot", '').replace("\n", '').capitalize()
    else:
        message = msg['text'].replace("\n", '').capitalize()
    try:
        r = WolframCLIENT.query(translator.translate(message, dest='en').text)
        Answer = translator.translate(next(r.results).text, dest='pt').text.capitalize()
        if len(Answer) > 200:
            raise "Flood"
        else:
            cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])
    except:
        r = requests.get('https://api.simsimi.net/v2/?text={}&lc=pt&cf=true'.format(message))
        try:
            Answer = json.loads(r.text)['messages'][0]['response'].capitalize()
        except:
            cookiebot.sendMessage(mekhyID, str(r.text))
            if len(str(r.text).split("{")) > 1:
                Answer = str(r.text).split("{")[1]
                Answer = "{" + Answer
                Answer = json.loads(Answer)['messages'][0]['response'].capitalize()
        Answer = translator.translate(Answer, dest='pt').text
        cookiebot.sendMessage(chat_id, Answer, reply_to_message_id=msg['message_id'])


def AddtoRandomDatabase(msg, chat_id):
    wait_open("Random_Database.txt")
    text = open("Random_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Random_Database.txt", 'w', encoding='utf-8')
    if len(lines) > 1000:
        i = len(lines) - 1000
    else:
        i = 0
    while i < len(lines):
        if not lines[i] == "\n":
            text.write(lines[i])
        i += 1
    i = 0
    text.write(str(chat_id) + " " + str(msg['message_id']) + "\n")
    text.close()

def ReplyAleatorio(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'upload_photo')
    wait_open("Random_Database.txt")
    text = open("Random_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    while True:
        try:
            target = random.choice(lines).replace("\n", '')
            cookiebot.forwardMessage(chat_id, int(target.split()[0]), int(target.split()[1]))
            break
        except Exception as e:
            print(str(e))
        

def AddtoStickerDatabase(msg, chat_id):
    wait_open("Sticker_Database.txt")
    text = open("Sticker_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    text = open("Sticker_Database.txt", 'w', encoding='utf-8')
    if len(lines) > 1000:
        i = len(lines) - 1000
    else:
        i = 0
    while i < len(lines):
        if not lines[i] == "\n":
            text.write(lines[i])
        i += 1
    i = 0
    text.write(msg['sticker']['file_id'] + "\n")
    text.close()

def ReplySticker(msg, chat_id):
    wait_open("Sticker_Database.txt")
    text = open("Sticker_Database.txt", 'r+', encoding='utf-8')
    lines = text.readlines()
    text.close()
    cookiebot.sendSticker(chat_id, random.choice(lines).replace("\n", ''), reply_to_message_id=msg['message_id'])

def Configurar(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if str(msg['from']['username']) in listaadmins or str(msg['from']['username']) == "MekhyW":
        wait_open("Configs/Config_"+str(chat_id)+".txt")
        text = open("Configs/Config_"+str(chat_id)+".txt", 'r', encoding='utf-8')
        variables = text.read()
        text.close()
        cookiebot.sendMessage(msg['from']['id'],"Configuração atual:\n\n" + variables + '\n\nEscolha a variável que vc gostaria de alterar', reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                   [InlineKeyboardButton(text="Compartilhamento de Posts",callback_data='k CONFIG {}'.format(str(chat_id)))],
                                   [InlineKeyboardButton(text="FurBots",callback_data='a CONFIG {}'.format(str(chat_id)))], 
                                   [InlineKeyboardButton(text="Limite Stickers",callback_data='b CONFIG {}'.format(str(chat_id)))],
                                   [InlineKeyboardButton(text="🕒 Limbo",callback_data='c CONFIG {}'.format(str(chat_id)))], 
                                   [InlineKeyboardButton(text="🕒 CAPTCHA",callback_data='d CONFIG {}'.format(str(chat_id)))],
                                   [InlineKeyboardButton(text="Funções Diversão",callback_data='h CONFIG {}'.format(str(chat_id)))],
                                   [InlineKeyboardButton(text="Funções Utilidade",callback_data='i CONFIG {}'.format(str(chat_id)))],
                                   [InlineKeyboardButton(text="Chat SFW",callback_data='j CONFIG {}'.format(str(chat_id)))]
                               ]
                           ))
        cookiebot.sendMessage(chat_id,"Te mandei uma mensagem no chat privado para configurar" , reply_to_message_id=msg['message_id'])
    else:
        cookiebot.sendMessage(chat_id, "Você não tem permissão para configurar o bot!", reply_to_message_id=msg['message_id'])

def ConfigurarSettar(msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if msg['text'].isdigit():
        variable_to_be_altered = ""
        if "Use 1 para permitir que eu encaminhe publicações de artistas e avisos no grupo, ou 0 para impedir isso." in msg['reply_to_message']['text']:
            variable_to_be_altered = publisher
        elif "Use 1 para não interferir com outros furbots caso eles estejam no grupo, ou 0 se eu for o único." in msg['reply_to_message']['text']:
            variable_to_be_altered = "FurBots"
        elif "Este é o limite máximo de stickers permitidos em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Sticker_Spam_Limit"
        elif "Este é o tempo pelo qual novos usuários no grupo não poderão mandar imagens (o bot apaga automaticamente)." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Tempo_sem_poder_mandar_imagem"
        elif "Este é o tempo que novos usuários dispõem para resolver o Captcha. USE 0 PARA DESLIGAR O CAPTCHA!" in msg['reply_to_message']['text']:
            variable_to_be_altered = "Tempo_Captcha"
        elif "Use 1 para permitir comandos e funcionalidades de diversão, ou 0 para apenas as funções de controle/gerenciamento." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Funções_Diversão"
        elif "Use 1 para permitir comandos e funcionalidades de utilidade, ou 0 para desligá-las." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Funções_Utilidade"
        elif "Use 1 para indicar que o chat é SFW, ou 0 para NSFW." in msg['reply_to_message']['text']:
            variable_to_be_altered = "SFW"
        chat_to_alter = msg['reply_to_message']['text'].split("\n")[0].split("= ")[1]
        wait_open("Configs/Config_"+str(chat_to_alter)+".txt")
        text_file = open("Configs/Config_"+str(chat_to_alter)+".txt", 'r', encoding='utf-8')
        lines = text_file.readlines()
        text_file.close()
        text_file = open("Configs/Config_"+str(chat_to_alter)+".txt", 'w', encoding='utf-8')
        for line in lines:
            if variable_to_be_altered in line:
                text_file.write(variable_to_be_altered + ": " + msg['text'] + "\n")
                cookiebot.sendMessage(chat_id, "Variável configurada! ✔️\nPode retornar ao chat")
                cookiebot.deleteMessage(telepot.message_identifier(msg['reply_to_message']))
                cookiebot.deleteMessage(telepot.message_identifier(msg))
            elif len(line.split()) > 1:
                text_file.write(line)
        text_file.close()
    else:
        cookiebot.sendMessage(chat_id, "Apenas números naturais são aceitos!", reply_to_message_id=msg['message_id'])




#MAIN THREAD FUNCTION
def thread_function(msg):
    try:
        if any(key in msg for key in ['dice', 'poll', 'voice_chat_started', 'voice_chat_ended']) or 'from' not in msg:
            return
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id, msg['message_id'])
        if chat_type == 'private' and 'reply_to_message' not in msg:
            if 'text' in msg and msg['text'] == "/stop" and msg['from']['id'] == mekhyID:
                os._exit(0)
            elif content_type in ['photo', 'video', 'document']:
                ReceivePublisher(msg, chat_id)
            else:
                cookiebot.sendMessage(chat_id, "Olá, sou o CookieBot!\n\n**Para agendar uma postagem, envie a sua mensagem por aqui (lembrando que deve conter uma foto, vídeo, gif ou documento)**\n\nSou um bot com IA de conversa, conteúdo infinito, conteúdo customizado e speech-to-text.\nSe quiser me adicionar no seu chat ou obter a lista de comandos comentada, mande uma mensagem para o @MekhyW")
        else:
            global listaadmins, listaadmins_id, publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions
            if chat_type != 'private':
                #BEGGINING OF ADMINISTRATORS GATHERING
                if not os.path.exists("GranularAdmins/GranularAdmins_" + str(chat_id) + ".txt"):
                    text = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'w').close()
                wait_open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt")
                text_file = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'r', encoding='utf-8')
                lines = text_file.readlines()
                text_file.close()
                if lines != []:
                    listaadmins = []
                    for username in lines:
                        listaadmins.append(username.replace("\n", ''))
                else:
                    listaadmins = []
                    listaadmins_id = []
                    for admin in cookiebot.getChatAdministrators(chat_id):
                        if 'username' in admin['user']:
                            listaadmins.append(str(admin['user']['username']))
                        listaadmins_id.append(str(admin['user']['id']))
                #END OF ADMINISTRATORS GATHERING
                #BEGGINING OF NEW NAME GATHERING
                if not os.path.isfile("Registers/"+str(chat_id)+".txt"):
                    open("Registers/"+str(chat_id)+".txt", 'a', encoding='utf-8').close() 
                wait_open("Registers/"+str(chat_id)+".txt")
                text_file = open("Registers/"+str(chat_id)+".txt", "r+", encoding='utf-8')
                if 'username' in msg['from'] and (check_if_string_in_file(text_file, msg['from']['username']) == False):
                    text_file.write("\n"+msg['from']['username'])
                text_file.close()
                #END OF NEW NAME GATHERING
                #BEGGINNING OF CONFIG GATHERING
                if not os.path.isfile("Configs/Config_"+str(chat_id)+".txt"):
                    open("Configs/Config_"+str(chat_id)+".txt", 'a', encoding='utf-8').close()
                    text_file = open("Configs/Config_"+str(chat_id)+".txt", "w", encoding='utf-8')
                    text_file.write("Publicador: 1\nFurBots: 0\nSticker_Spam_Limit: 5\nTempo_sem_poder_mandar_imagem: 600\nTempo_Captcha: 300\nFunções_Diversão: 1\nFunções_Utilidade: 1\nSFW: 1")
                    text_file.close()
                wait_open("Configs/Config_"+str(chat_id)+".txt")
                text_file = open("Configs/Config_"+str(chat_id)+".txt", "r", encoding='utf-8')
                lines = text_file.readlines()
                text_file.close()
                for line in lines:
                    if line.split()[0] == "Publicador:":
                        publisher = int(line.split()[1])
                    elif line.split()[0] == "FurBots:":
                        FurBots = int(line.split()[1])
                    elif line.split()[0] == "Sticker_Spam_Limit:":
                        stickerspamlimit = int(line.split()[1])
                    elif line.split()[0] == "Tempo_sem_poder_mandar_imagem:":
                        limbotimespan = int(line.split()[1])
                    elif line.split()[0] == "Tempo_Captcha:":
                        captchatimespan = int(line.split()[1])
                    elif line.split()[0] == "Funções_Diversão:":
                        funfunctions = int(line.split()[1])
                    elif line.split()[0] == "Funções_Utilidade:":
                        utilityfunctions = int(line.split()[1])
                    elif line.split()[0] == "SFW:":
                        sfw = int(line.split()[1])
                #END OF CONFIG GATHERING
                #BEGGINING OF GROUP ACTIVITY GATHERING
                wait_open("GroupActivity/Activity_today_" + str(chat_id) + ".txt")
                wait_open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt")
                open("GroupActivity/Activity_today_" + str(chat_id) + ".txt", 'a').close()
                open("GroupActivity/Activity_yesterday_" + str(chat_id) + ".txt", 'a').close()
                todaytext = open("GroupActivity/Activity_today_" + str(chat_id) + ".txt", 'r')
                lines = todaytext.readlines()
                todaytext.close()
                if len(lines) > 0 and lines[0].split()[0] != str(datetime.date.today()):
                    with open("GroupActivity/Activity_yesterday_" + str(chat_id)+".txt", 'w') as yesterdaytext:
                        for line in lines:
                            yesterdaytext.write(line)
                    yesterdaytext.close()
                    todaytext = open("GroupActivity/Activity_today_" + str(chat_id)+".txt", 'w')
                    todaytext.close()
                with open("GroupActivity/Activity_today_" + str(chat_id)+".txt", 'a') as todaytext:
                    todaytext.write(str(datetime.datetime.now()) + "\n")
                todaytext.close()
                #END OF GROUP ACTIVITY GATHERING
                #BEGINNING OF PUBLISHER SETUP
                wait_open("Publish_Queue.txt")
                publishqueue = open("Publish_Queue.txt", 'r')
                publishqueue_lines = publishqueue.readlines()
                publishqueue.close()
                if publishqueue_lines[0] != str(datetime.date.today())+"\n":
                    with open("Publish_Queue.txt", 'w') as publishqueue:
                        publishqueue.write(str(datetime.date.today()) + "\n")
                        if len(publishqueue_lines) > 1:
                            for line in publishqueue_lines[1:]:
                                if len(line.split()) > 1 and int(line.split()[1]) > 1:
                                    publishqueue.write(line.split()[0] + " " + line.split()[1] + str(int(line.split()[2]) - 1) + "\n")
                    publishqueue.close()
                global publisher_threads
                if chat_id not in publisher_threads:
                    publisher_threads[chat_id] = []
                if publisher == True and len(publisher_threads[chat_id]) == 0:
                    SpawnThreadsPublisher(chat_id)
                #END OF PUBLISHER SETUP
                #BEGINNING OF CALENDAR SYNC AND FURBOTS CHECK
                wait_open("Registers/"+str(chat_id)+".txt")
                text_file = open("Registers/"+str(chat_id)+".txt", "r", encoding='utf-8')
                lines = text_file.read().split("\n")
                text_file.close()
                text_file = open("Registers/"+str(chat_id)+".txt", "w", encoding='utf-8')
                for line in lines:
                    if line == '':
                        pass
                    elif 'username' in msg['from'] and line.startswith(msg['from']['username']):
                        global lastmessagedate
                        global lastmessagetime
                        global sentcooldownmessage
                        entry = line.split()
                        if 'text' in msg:
                            if msg['text'].startswith("/"):
                                if len(entry) == 3:
                                    now = entry[2].split(":")
                                    lastmessagedate = entry[1]
                                    lastmessagetime = (float(now[0])*3600)+(float(now[1])*60)+(float(now[2])*1)
                                else:
                                    lastmessagedate = "1-1-1"
                                    lastmessagedate = "0"
                                if lines.index(line) == len(lines)-1:
                                    text_file.write(entry[0]+" "+str(datetime.datetime.now()))
                                else:
                                    text_file.write(entry[0]+" "+str(datetime.datetime.now())+"\n")
                            else:
                                if lines.index(line) == len(lines)-1:
                                    text_file.write(line)
                                else:
                                    text_file.write(line+"\n")
                    elif lines.index(line) == len(lines)-1:
                        text_file.write(line)
                    else:
                        text_file.write(line+"\n")
                text_file.close()
                #END OF CALENDAR SYNC AND FURBOTS CHECK
            if content_type == "new_chat_member":
                if CheckCAS(msg, chat_id) == False and CheckRaider(msg, chat_id) == False:
                    Limbo(msg, chat_id)
                    if captchatimespan > 0 and ("CookieMWbot" in listaadmins or "MekhysBombot" in listaadmins):
                        Captcha(msg, chat_id)
                    else:
                        Bemvindo(msg, chat_id)
            elif content_type == "left_chat_member":
                left_chat_member(msg, chat_id)
            elif content_type == "voice":
                if utilityfunctions == True:
                    Speech_to_text(msg, chat_id)
            elif content_type == "audio":
                pass
            elif content_type == "photo":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
                CheckLimbo(msg, chat_id)
            elif content_type == "video":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
                CheckLimbo(msg, chat_id)
            elif content_type == "document":
                if sfw == 1:
                    AddtoRandomDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                    ReplySticker(msg, chat_id)
            elif content_type == "sticker":
                CheckLimbo(msg, chat_id)
                Sticker_anti_spam(msg, chat_id)
                if sfw == 1:
                    AddtoStickerDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot':
                    ReplySticker(msg, chat_id)
            #elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and str(datetime.date.today()) == lastmessagedate and float(lastmessagetime)+60 >= ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
            #    CooldownAction(msg, chat_id)
            elif 'text' in msg and (msg['text'].startswith("/aleatorio") or msg['text'].startswith("/aleatório")) and funfunctions == True:
                ReplyAleatorio(msg, chat_id)
            elif 'text' in msg and (msg['text'].startswith("/dado") or (msg['text'].lower().startswith("/d") and msg['text'].replace("@CookieMWbot", '').split()[0][2:].isnumeric())) and funfunctions == True:
                Dado(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/idade") and funfunctions == True:
                Idade(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/genero") and funfunctions == True:
                Genero(msg, chat_id)
            elif 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida quando alguém entrar no grupo" and str(msg['from']['username']) in listaadmins:
                AtualizaBemvindo(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/novobemvindo"):
                NovoBemvindo(msg, chat_id)
            elif FurBots == False and 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "Se vc é um admin, responda ESTA mensagem com a mensagem que será exibida com o /regras" and str(msg['from']['username']) in listaadmins:
                AtualizaRegras(msg, chat_id)
            elif FurBots == False and 'text' in msg and msg['text'].startswith("/novasregras"):
                NovasRegras(msg, chat_id)
            elif FurBots == False and 'text' in msg and msg['text'].startswith("/regras"):
                Regras(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/tavivo"):
                TaVivo(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/everyone"):
                Everyone(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/adm"):
                Adm(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/comandos"):
                Comandos(msg, chat_id)
            elif FurBots == False and 'text' in msg and (msg['text'].startswith("/hoje") or msg['text'].startswith("/today")) and funfunctions == True:
                Hoje(msg, chat_id)
            elif FurBots == False and 'text' in msg and (msg['text'].startswith("/cheiro") or msg['text'].startswith("/smell")) and funfunctions == True:
                Cheiro(msg, chat_id)
            elif FurBots == False and 'text' in msg and ('eu faço' in msg['text'] or 'eu faco' in msg['text']) and '?' in msg['text'] and funfunctions == True:
                QqEuFaço(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/ideiadesenho") and utilityfunctions == True:
                IdeiaDesenho(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/contato"):
                Contato(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/qualquercoisa") and utilityfunctions == True:
                PromptQualquerCoisa(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/configurar"):
                Configurar(msg, chat_id)
            elif 'text' in msg and 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "Responda ESTA mensagem com o novo valor da variável" in msg['reply_to_message']['text']:
                ConfigurarSettar(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')) and utilityfunctions == True:
                CustomCommand(msg, chat_id)
            elif 'text' in msg and msg['text'].startswith("/") and " " not in msg['text'] and (FurBots==False or msg['text'] not in open("FurBots functions.txt", "r+", encoding='utf-8').read()) and utilityfunctions == True:
                QualquerCoisa(msg, chat_id)
            elif 'text' in msg and (msg['text'].startswith("Cookiebot") or msg['text'].startswith("cookiebot") or 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') and ("quem" in msg['text'] or "Quem" in msg['text']) and ("?" in msg['text']):
                Quem(msg, chat_id)
            elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and msg['reply_to_message']['caption'] == "Digite o código acima para provar que você não é um robô\nVocê tem {} minutos, se não resolver nesse tempo te removerei do chat\n(OBS: Se não aparecem 4 digitos, abra a foto completa)".format(str(round(captchatimespan/60))):
                SolveCaptcha(msg, chat_id, False)
            elif 'text' in msg and (('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot') or "Cookiebot" in msg['text'] or "cookiebot" in msg['text'] or "@CookieMWbot" in msg['text'] or "COOKIEBOT" in msg['text'] or "CookieBot" in msg['text']) and funfunctions == True:
                if not OnSay(msg, chat_id):
                    InteligenciaArtificial(msg, chat_id)
            elif 'text' in msg:
                SolveCaptcha(msg, chat_id, False)
                CheckCaptcha(msg, chat_id)
                OnSay(msg, chat_id)
            #BEGGINNING OF COOLDOWN UPDATES
            if 'text' in msg:
                if float(lastmessagetime)+60 < ((datetime.datetime.now().hour*3600)+(datetime.datetime.now().minute*60)+(datetime.datetime.now().second)):
                    sentcooldownmessage = False
                wait_open("Stickers.txt")
                text_file = open("Stickers.txt", "r+", encoding='utf8')
                lines = text_file.readlines()
                text_file.close()
                text_file = open("Stickers.txt", "w", encoding='utf8')
                for line in lines:
                    if str(chat_id) in line:
                        text_file.write(line.split()[0] + " " + "0" + "\n")
                    else:
                        text_file.write(line)
                text_file.close()
            #END OF COOLDOWN UPDATES
    except:
        if 'ConnectionResetError' not in traceback.format_exc():
            cookiebot.sendMessage(mekhyID, traceback.format_exc())
            cookiebot.sendMessage(mekhyID, str(msg))

#MESSAGE HANDLER
def handle(msg):
    try:
        global threads
        messagehandle = threading.Thread(target=thread_function, args=(msg,))
        threads.append(messagehandle)
        messagehandle.start()
        time.sleep(0.01)
    except:
        cookiebot.sendMessage(mekhyID, traceback.format_exc())

def handle_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    if 'CONFIG' in query_data:
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        if query_data.startswith('k'):
            cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nUse 1 para permitir que eu encaminhe publicações de artistas e avisos no grupo, ou 0 para impedir isso.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
        if query_data.startswith('a'):
            cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nUse 1 para não interferir com outros furbots caso eles estejam no grupo, ou 0 se eu for o único.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
        elif query_data.startswith('b'):
            cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o limite máximo de stickers permitidos em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo.\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
        elif query_data.startswith('c'):
            cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o tempo pelo qual novos usuários no grupo não poderão mandar imagens (o bot apaga automaticamente).\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
        elif query_data.startswith('d'):
            cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o tempo que novos usuários dispõem para resolver o Captcha. USE 0 PARA DESLIGAR O CAPTCHA!\nResponda ESTA mensagem com o novo valor da variável'.format(query_data.split()[2]))
        elif query_data.startswith('h'):
            cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 para permitir comandos e funcionalidades de diversão, ou 0 para apenas as funções de controle/gerenciamento.\nResponda ESTA mensagem com o novo valor da variável".format(query_data.split()[2]))
        elif query_data.startswith('i'):
            cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 para permitir comandos e funcionalidades de utilidade, ou 0 para desligá-las.\nResponda ESTA mensagem com o novo valor da variável".format(query_data.split()[2]))
        elif query_data.startswith('j'):
            cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 para indicar que o chat é SFW, ou 0 para NSFW.\nResponda ESTA mensagem com o novo valor da variável".format(query_data.split()[2]))
    elif 'PUBLISHER' in query_data:
        forwarded = cookiebot.forwardMessage(mekhyID, msg['message']['chat']['id'], query_data.split()[2])
        cookiebot.sendMessage(mekhyID, "Group post - Days: {}".format(query_data.split()[0]), reply_to_message_id=forwarded, reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Aprovar", callback_data='Approve PUBLISH {} {} {}'.format(query_data.split()[2], msg['message']['chat']['id'], query_data.split()[0]).replace("(", '').replace(",", '').replace(")", ''))], [InlineKeyboardButton(text="Recusar", callback_data='Refuse PUBLISH')]]))
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendChatAction(msg['message']['chat']['id'], 'typing')
        cookiebot.sendMessage(msg['message']['chat']['id'], "➡️ Sua mensagem foi enviada para aprovação ➡️\n\n--> Isto é feito para evitar conteúdo NSFW em chats SFW e abuso do sistema\n--> Por favor NÃO APAGUE a sua mensagem", reply_to_message_id=query_data.split()[2])
    elif 'PUBLISH' in query_data:
        if query_data.startswith('Approve'):
            wait_open("Publish_Queue.txt")
            text = open("Publish_Queue.txt", 'a+', encoding='utf-8')
            text.write(query_data.split()[2] + " " + query_data.split()[3] + " " + query_data.split()[4] + "\n")
            text.close()
            cookiebot.sendMessage(query_data.split()[3], "✅ Sua mensagem foi Aprovada! ✅\nDeixe ela aqui e pode relaxar, eu vou divulgar por vc :)")
        cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        cookiebot.sendMessage(msg['message']['chat']['id'], query_data)
    else:
        global listaadmins_id
        listaadmins_id = []
        for admin in cookiebot.getChatAdministrators(msg['message']['reply_to_message']['chat']['id']):
            listaadmins_id.append(str(admin['user']['id']))
        if query_data == 'CAPTCHA' and str(from_id) in listaadmins_id:
            SolveCaptcha(msg, msg['message']['reply_to_message']['chat']['id'], True)
            cookiebot.deleteMessage(telepot.message_identifier(msg['message']))
        

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()