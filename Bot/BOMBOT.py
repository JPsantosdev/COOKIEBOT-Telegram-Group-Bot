from universal_funcs import *
isBombot = True
from Configurations import *
from GroupShield import *
from UserRegisters import *
from Cooldowns import *
from NaturalLanguage import *
from SocialContent import *
from Audio import *
from Miscellaneous import *
from Publisher import *
import threading, gc
unnatended_threads = list()
gc.enable()

if isBombot:
    cookiebot = telepot.Bot(bombotTOKEN)
else:
    cookiebot = telepot.Bot(cookiebotTOKEN)
updates = cookiebot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    cookiebot.getUpdates(offset=last_update_id+1)

startPublisher(isBombot)
Send(cookiebot, mekhyID, 'I am online')

def thread_function(msg):
    try:
        if any(key in msg for key in ['dice', 'poll', 'voice_chat_started', 'voice_chat_ended', 
                                      'voice_chat_participants_invited', 'video_chat_participants_invited']):
            return
        if 'message_thread_id' in msg:
            thread_id = msg['message_thread_id']
        else:
            thread_id = None
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id, msg['message_id'])
        FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = 0, 1, 5, 600, 300, 1, 1, "pt", 0, 1, "9999", 9999, 0
        if chat_type == 'private' and 'reply_to_message' not in msg:
            if 'text' in msg:
                if msg['text'].startswith("/start"):
                    SetComandosPrivate(cookiebot, chat_id, isBombot=isBombot)
                if msg['text'].startswith(("/grupos", "/groups")) and 'from' in msg and msg['from']['id'] == mekhyID:
                    Grupos(cookiebot, msg, chat_id, 'eng')
                elif msg['text'].startswith(("/comandos", "/commands")):
                    Comandos(cookiebot, msg, chat_id, 'eng')
                elif msg['text'] == "/stop" and 'from' in msg and msg['from']['id'] == mekhyID:
                    os._exit(0)
                elif msg['text'] == "/restart" and 'from' in msg and msg['from']['id'] == mekhyID:
                    os.execl(sys.executable, sys.executable, *sys.argv)
                elif msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == mekhyID:
                    targetId = msg['text'].split()[1]
                    LeaveAndBlacklist(cookiebot, targetId)
                elif msg['text'].startswith("/broadcast") and 'from' in msg and msg['from']['id'] == mekhyID:
                    Broadcast(cookiebot, msg)
            PvDefaultMessage(cookiebot, msg, chat_id, isBombot)
        else:
            if chat_type != 'private':
                listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id)
                FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = GetConfig(chat_id)
                CheckNewName(msg, chat_id)
            if 'group_chat_created' in msg and msg['group_chat_created'] == True:
                isCreatorBlacklisted = GetRequestBackend(f"blacklist/{msg['from']['id']}")
                chatinfo = cookiebot.getChat(chat_id)
                if (not 'error' in isCreatorBlacklisted) or len(chatinfo['title']) < 3:
                    LeaveAndBlacklist(cookiebot, chat_id)
                    Send(cookiebot, mekhyID, f"Auto-left:\n{chat_id}")
                    return
            elif content_type == "new_chat_member":
                if 'username' in msg['new_chat_participant'] and msg['new_chat_participant']['username'] in ["MekhysBombot", "CookieMWbot"]:
                    isBlacklisted = GetRequestBackend(f"blacklist/{chat_id}")
                    chatinfo = cookiebot.getChat(chat_id)
                    if (not 'error' in isBlacklisted) or len(chatinfo['title']) < 3:
                        LeaveAndBlacklist(cookiebot, chat_id)
                        Send(cookiebot, mekhyID, f"Auto-left:\n{chat_id}")
                        return
                    Send(cookiebot, mekhyID, f"Added:\n{chatinfo}")
                    cookiebot.sendAnimation(chat_id, 'https://cdn.dribbble.com/users/4228736/screenshots/10874431/media/28ef00faa119065224429a0f94be21f3.gif',
                    caption="Obrigado por me adicionar!\nThanks for adding me!\n\n--> Use /comandos para ver todas as minhas funcionalidades\n--> /configurar para ligar/desligar funções ou alterar valores\n--> Não esqueça de me dar direitos administrativos para poder defender o grupo de raiders/spammers ou apagar mensagens\n--> Website, painel de controle e tutoriais virão em breve. Estou em crescimento!\n\nIf this chat is not in portuguese language, you can use /configure to change my lang.\nIf you have any questions or want something added, message @MekhyW")
                if msg['new_chat_participant']['id'] != cookiebot.getMe()['id'] and not CheckCAS(cookiebot, msg, chat_id, language) and not CheckRaider(cookiebot, msg, chat_id, language) and not CheckHumanFactor(cookiebot, msg, chat_id, language) and not CheckBlacklist(cookiebot, msg, chat_id, language):
                    if captchatimespan > 0 and ("CookieMWbot" in listaadmins or "MekhysBombot" in listaadmins):
                        Captcha(cookiebot, msg, chat_id, captchatimespan, language)
                    else:
                        Bemvindo(cookiebot, msg, chat_id, limbotimespan, language, isBombot=isBombot)
            elif content_type == "left_chat_member":
                left_chat_member(msg, chat_id)
            elif content_type == "voice":
                if utilityfunctions == True:
                    audio = GetVoiceMessage(cookiebot, msg, isBombot=isBombot)
                    #duration = int(msg['voice']['duration'])
                    #if duration >= 10 and duration <= 240:
                    #    Speech_to_text(cookiebot, msg, chat_id, sfw, audio, language)
                    Identify_music(cookiebot, msg, chat_id, audio, language)
            elif content_type == "audio":
                pass
            elif content_type in ["photo", "video", "document", "animation"] and all(key in msg for key in ['sender_chat', 'forward_from_chat', 'from', 'caption']) and msg['from']['first_name'] == 'Telegram' and publisherask == True:
                AskPublisher(cookiebot, msg, chat_id, language)
            elif content_type == "photo":
                if sfw == True and funfunctions == True:
                    photo_id = msg['photo'][-1]['file_id']
                    AddtoRandomDatabase(msg, chat_id, photo_id)
            elif content_type == "video":
                if sfw == True and funfunctions == True:
                    AddtoRandomDatabase(msg, chat_id)
            elif content_type == "document":
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and funfunctions == True:
                    ReplySticker(cookiebot, msg, chat_id)
            elif content_type == "animation":
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and funfunctions == True:
                    ReplySticker(cookiebot, msg, chat_id)
            elif content_type == "sticker":
                Sticker_anti_spam(cookiebot, msg, chat_id, stickerspamlimit, language)
                if sfw == True:
                    AddtoStickerDatabase(msg, chat_id)
                if 'reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and funfunctions == True:
                    ReplySticker(cookiebot, msg, chat_id)
            elif 'text' in msg:
                if msg['text'].startswith("/start@CookieMWbot") or msg['text'].startswith("/start@MekhysBombot"):
                    cookiebot.sendAnimation(chat_id, 'https://cdn.dribbble.com/users/4228736/screenshots/10874431/media/28ef00faa119065224429a0f94be21f3.gif',
                    caption="Obrigado por me adicionar!\nThanks for adding me!\n\n--> Use /comandos para ver todas as minhas funcionalidades\n--> /configurar para ligar/desligar funções ou alterar valores\n--> Não esqueça de me dar direitos administrativos para poder defender o grupo de raiders/spammers ou apagar mensagens\n--> Website, painel de controle e tutoriais virão em breve. Estou em crescimento!\n\nIf this chat is not in portuguese language, you can use /configure to change my lang.\nIf you have any questions or want something added, message @MekhyW",
                    reply_to_message_id=msg['message_id'])
                elif msg['text'].startswith("/leave") and 'from' in msg and msg['from']['id'] == mekhyID:
                    LeaveAndBlacklist(cookiebot, chat_id)
                elif msg['text'].startswith(("/reload", "/recarregar")):
                    listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id, ignorecache=True)
                    FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions, language, publisherpost, publisherask, threadPosts, maxPosts, publisherMembersOnly = GetConfig(chat_id, ignorecache=True)
                    Send(cookiebot, chat_id, "Memória recarregada com sucesso!", msg, language)
                elif msg['text'].startswith(("/analise", "/analisis", "/analysis")):
                    Analyze(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/repost", "/repostar", "/reenviar")):
                    listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id, ignorecache=True)
                    ScheduleAutopost(cookiebot, msg, chat_id, language, listaadmins_id)
                elif msg['text'].startswith(("/deletereposts", "/apagarreposts", "/apagarreenvios")):
                    listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id, ignorecache=True)
                    ClearAutoposts(cookiebot, msg, chat_id, language, listaadmins_id)
                elif msg['text'].startswith(("/pesquisaimagem", "/searchimage", "/buscarimagen")):
                    ReverseImageSearch(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/aleatorio", "/aleatório", "/random")):
                    if funfunctions:
                        ReplyAleatorio(cookiebot, msg, chat_id, thread_id=thread_id, isBombot=isBombot)
                    else:
                        NotifyFunOff(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith("/meme"):
                    if funfunctions:
                        Meme(cookiebot, msg, chat_id, language)
                    else:
                        NotifyFunOff(cookiebot, msg, chat_id, language)
                elif (msg['text'].startswith(("/dado", "/dice")) or (msg['text'].lower().startswith("/d") and msg['text'].replace("@CookieMWbot", '').split()[0][2:].isnumeric())):
                    if funfunctions:
                        Dado(cookiebot, msg, chat_id, language)
                    else:
                        NotifyFunOff(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/idade", "/age", "/edad")):
                    if funfunctions:
                        Idade(cookiebot, msg, chat_id, language)
                    else:
                        NotifyFunOff(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/genero", "/gender")):
                    if funfunctions:
                        Genero(cookiebot, msg, chat_id, language)
                    else:
                        NotifyFunOff(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/rojao", "/rojão", "/acende", "/fogos")):
                    if funfunctions:
                        Rojao(cookiebot, msg, chat_id, thread_id=thread_id, isBombot=isBombot)
                    else:
                        NotifyFunOff(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/shippar", "/ship")):
                    if funfunctions:
                        Shippar(cookiebot, msg, chat_id, language)
                    else:
                        NotifyFunOff(cookiebot, msg, chat_id, language)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone joins the group":
                    listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id, ignorecache=True)
                    AtualizaBemvindo(cookiebot, msg, chat_id, listaadmins_id)
                elif msg['text'].startswith(("/novobemvindo", "/newwelcome", "/nuevabienvenida")):
                    NovoBemvindo(cookiebot, msg, chat_id)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and msg['reply_to_message']['text'] == "If you are an admin, REPLY THIS MESSAGE with the message that will be displayed when someone asks for the rules":
                    listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id, ignorecache=True)
                    AtualizaRegras(cookiebot, msg, chat_id, listaadmins_id)
                elif msg['text'].startswith(("/novasregras", "/newrules", "/nuevasreglas")):
                    NovasRegras(cookiebot, msg, chat_id)
                elif msg['text'].startswith(("/regras", "/rules", "/reglas")):
                    if FurBots == False or "CookieMWbot" in msg['text'].split('@'):
                        Regras(cookiebot, msg, chat_id, language)
                    else:
                        return
                elif msg['text'].startswith(("/tavivo", "/isalive", "/estavivo")):
                    TaVivo(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith("/everyone"):
                    Everyone(cookiebot, msg, chat_id, listaadmins, language)
                elif msg['text'].startswith("/adm"):
                    AdmAsk(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/comandos", "/commands")):
                    Comandos(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/ideiadesenho", "/drawingidea", "/ideadibujo")) and utilityfunctions == True:
                    IdeiaDesenho(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/qualquercoisa", "/anything", "/cualquiercosa")) and utilityfunctions == True:
                    PromptQualquerCoisa(cookiebot, msg, chat_id, language)
                elif msg['text'].startswith(("/configurar", "/configure")):
                    listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id, ignorecache=True)
                    Configurar(cookiebot, msg, chat_id, listaadmins_id, language)
                elif 'reply_to_message' in msg and 'text' in msg['reply_to_message'] and "REPLY THIS MESSAGE with the new variable value" in msg['reply_to_message']['text']:
                    ConfigurarSettar(cookiebot, msg, chat_id, isBombot=isBombot)
                elif msg['text'].startswith("/") and " " not in msg['text'] and os.path.exists("Custom/"+msg['text'].replace('/', '').replace("@CookieMWbot", '')) and utilityfunctions == True:
                    CustomCommand(cookiebot, msg, chat_id)
                elif msg['text'].startswith("/") and "//" not in msg['text'] and (len(msg['text'].split('@')) < 2 or msg['text'].split('@')[1] in ['CookieMWbot', 'MekhysBombot']) and utilityfunctions == True:
                    if FurBots == True:
                        furbots_cmds = open("Static/FurBots_functions.txt", "r+", encoding='utf-8').readlines()
                        furbots_cmds = [x.strip() for x in furbots_cmds]
                        if msg['text'].split()[0].split('@')[0] in furbots_cmds:
                            return
                    QualquerCoisa(cookiebot, msg, chat_id, sfw, language)
                elif (msg['text'].lower().startswith("cookiebot") or ('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot')) and any(x in msg['text'].lower() for x in ['quem', 'who', 'quién', 'quien']) and ("?" in msg['text']) and funfunctions == True:
                    Quem(cookiebot, msg, chat_id, language)
                elif 'reply_to_message' in msg and 'photo' in msg['reply_to_message'] and 'caption' in msg['reply_to_message'] and str(round(captchatimespan/60)) in msg['reply_to_message']['caption']:
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan, language, isBombot=isBombot)
                elif (('reply_to_message' in msg and msg['reply_to_message']['from']['first_name'] == 'Cookiebot' and 'text' in msg['reply_to_message']) or "cookiebot" in msg['text'].lower() or "@CookieMWbot" in msg['text']) and funfunctions == True:
                    AnswerFinal = InteligenciaArtificial(cookiebot, msg, chat_id, language, sfw)
                    try:
                        Send(cookiebot, chat_id, AnswerFinal, msg_to_reply=msg)
                    except TelegramError:
                        pass
                else:
                    SolveCaptcha(cookiebot, msg, chat_id, False, limbotimespan, language, isBombot=isBombot)
                    CheckCaptcha(cookiebot, msg, chat_id, captchatimespan, language)
            if chat_type != 'private' and content_type != "sticker":
                StickerCooldownUpdates(msg, chat_id)
            run_unnatendedthreads()
    except (TooManyRequestsError, BotWasBlockedError, MigratedToSupergroupChatError, NotEnoughRightsError) as e:
        print(e)
    except Exception as e:
        errormsg = f"{traceback.format_exc()} {e}"
        if 'ConnectionResetError' in errormsg or 'RemoteDisconnected' in errormsg:
            handle(msg)
        else:
            Send(cookiebot, mekhyID, traceback.format_exc())
            Send(cookiebot, mekhyID, str(msg))
            Send(cookiebot, mekhyID, str(e))
    finally:
        if not isBombot:
            SchedulerPull(cookiebot, isBombot=isBombot)

def thread_function_query(msg):
    try:
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        print('Callback Query:', query_id, from_id, query_data)
        try:
            chat_id = msg['message']['reply_to_message']['chat']['id']
            listaadmins, listaadmins_id, listaadmins_status = GetAdmins(cookiebot, msg, chat_id)
        except Exception as e:
            print(e)
            chat_id = from_id
            listaadmins, listaadmins_id, listaadmins_status = [], [], []
        if 'CONFIG' in query_data:
            ConfigVariableButton(cookiebot, msg, query_data)
        elif 'Pub' in query_data:
            if 'creator' in listaadmins_status and str(from_id) not in listaadmins_id:
                cookiebot.answerCallbackQuery(query_id, text="Only admins can do this")
            else:
                if query_data.startswith('SendToApproval'):
                    AskApproval(cookiebot, query_data, from_id, isBombot=isBombot)
                elif query_data.startswith('Approve'):
                    SchedulePost(cookiebot, query_data)
                elif query_data.startswith('Deny'):
                    DenyPost(cookiebot, query_data)
                DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
        elif query_data == 'CAPTCHA' and (str(from_id) in listaadmins_id or str(from_id) == str(mekhyID)):
            SolveCaptcha(cookiebot, msg, chat_id, True, isBombot=isBombot)
            DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
        elif query_data.startswith('ADM'):
            yesno = query_data.split()[1]
            language = query_data.split()[2]
            if yesno == 'Yes':
                Adm(cookiebot, msg, chat_id, listaadmins, language)
            else:
                Send(cookiebot, chat_id, "Comando cancelado", language=language)
            DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
        run_unnatendedthreads()
    except Exception as e:
        errormsg = f"{traceback.format_exc()} {e}"
        if 'ConnectionResetError' in errormsg or 'RemoteDisconnected' in errormsg:
            handle_query(msg)
        else:
            Send(cookiebot, mekhyID, traceback.format_exc())
            Send(cookiebot, mekhyID, str(msg))
            Send(cookiebot, mekhyID, str(e))

def run_unnatendedthreads():
    num_running_threads = threading.active_count()
    num_max_threads = 15
    for unnatended_thread in unnatended_threads:
        if unnatended_thread.is_alive():
            unnatended_threads.remove(unnatended_thread)
        elif num_running_threads < num_max_threads:
            unnatended_thread.start()
            num_running_threads += 1
            try:
                unnatended_threads.remove(unnatended_thread)
            except ValueError:
                pass
    if len(unnatended_threads) > 4 * num_max_threads:
        os.execl(sys.executable, sys.executable, *sys.argv)
    elif len(unnatended_threads) > 0:
        print(f"{len(unnatended_threads)} threads are still unnatended")

def handle(msg):
    try:
        new_thread = threading.Thread(target=thread_function, args=(msg,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except:
        Send(cookiebot, mekhyID, traceback.format_exc())

def handle_query(msg):
    try:
        new_thread = threading.Thread(target=thread_function_query, args=(msg,))
        unnatended_threads.append(new_thread)
        run_unnatendedthreads()
    except:
        Send(cookiebot, mekhyID, traceback.format_exc())
        

MessageLoop(cookiebot, {'chat': handle, 'callback_query': handle_query}).run_forever()