from universal_funcs import *

def GetAdmins(cookiebot, msg, chat_id):
    listaadmins, listaadmins_id = [], []
    if not os.path.exists("GranularAdmins/GranularAdmins_" + str(chat_id) + ".txt"):
        text = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'w').close()
    wait_open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt")
    text_file = open("GranularAdmins/GranularAdmins_" + str(chat_id)+".txt", 'r', encoding='utf-8')
    lines = text_file.readlines()
    text_file.close()
    if lines != []:
        for username in lines:
            listaadmins.append(username.replace("\n", ''))
    else:
        for admin in cookiebot.getChatAdministrators(chat_id):
            if 'username' in admin['user']:
                listaadmins.append(str(admin['user']['username']))
            listaadmins_id.append(str(admin['user']['id']))
    return listaadmins, listaadmins_id

def GetConfig(chat_id):
    publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions = 1, 0, 1, 5, 600, 300, 1, 1
    if not os.path.isfile("Configs/Config_"+str(chat_id)+".txt"):
        open("Configs/Config_"+str(chat_id)+".txt", 'a', encoding='utf-8').close()
        text_file = open("Configs/Config_"+str(chat_id)+".txt", "w", encoding='utf-8')
        text_file.write("Publicador: 1\nFurBots: 0\nSticker_Spam_Limit: 15\nTempo_sem_poder_mandar_imagem: 600\nTempo_Captcha: 300\nFunções_Diversão: 1\nFunções_Utilidade: 1\nSFW: 1")
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
    return publisher, FurBots, sfw, stickerspamlimit, limbotimespan, captchatimespan, funfunctions, utilityfunctions

def Configurar(cookiebot, msg, chat_id, listaadmins):
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

def ConfigurarSettar(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    if msg['text'].isdigit():
        variable_to_be_altered = ""
        if "Use 1 para permitir que eu encaminhe publicações de artistas e avisos no grupo, ou 0 para impedir isso." in msg['reply_to_message']['text']:
            variable_to_be_altered = "Publicador"
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
                DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))
                DeleteMessage(cookiebot, telepot.message_identifier(msg))
            elif len(line.split()) > 1:
                text_file.write(line)
        text_file.close()
    else:
        cookiebot.sendMessage(chat_id, "Apenas números naturais são aceitos!", reply_to_message_id=msg['message_id'])

def ConfigVariableButton(cookiebot, msg, query_data):
    DeleteMessage(cookiebot, telepot.message_identifier(msg['message']))
    if query_data.startswith('k'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nUse 1 para permitir que eu encaminhe publicações de artistas e avisos no grupo, ou 0 para impedir isso.\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável'.format(query_data.split()[2]))
    if query_data.startswith('a'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nUse 1 para não interferir com outros furbots caso eles estejam no grupo, ou 0 se eu for o único.\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('b'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o limite máximo de stickers permitidos em uma sequência pelo bot. Os próximos além desse serão deletados para evitar spam. Vale para todo mundo.\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('c'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o tempo pelo qual novos usuários no grupo não poderão mandar imagens (o bot apaga automaticamente).\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('d'):
        cookiebot.sendMessage(msg['message']['chat']['id'], 'Chat = {}\nEste é o tempo que novos usuários dispõem para resolver o Captcha. USE 0 PARA DESLIGAR O CAPTCHA!\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável'.format(query_data.split()[2]))
    elif query_data.startswith('h'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 para permitir comandos e funcionalidades de diversão, ou 0 para apenas as funções de controle/gerenciamento.\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável".format(query_data.split()[2]))
    elif query_data.startswith('i'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 para permitir comandos e funcionalidades de utilidade, ou 0 para desligá-las.\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável".format(query_data.split()[2]))
    elif query_data.startswith('j'):
        cookiebot.sendMessage(msg['message']['chat']['id'], "Chat = {}\nUse 1 para indicar que o chat é SFW, ou 0 para NSFW.\nDÊ REPLY NESTA MENSAGEM com o novo valor da variável".format(query_data.split()[2]))

def AtualizaBemvindo(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Welcome/Welcome_" + str(chat_id)+".txt")
    text_file = open("Welcome/Welcome_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de Boas Vindas atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def NovoBemvindo(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida quando alguém entrar no grupo", reply_to_message_id=msg['message_id'])

def AtualizaRegras(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    text_file = open("Rules/Regras_" + str(chat_id)+".txt", 'w', encoding='utf-8')
    text_file.write(msg['text'])
    cookiebot.sendMessage(chat_id, "Mensagem de regras atualizada! ✅", reply_to_message_id=msg['message_id'])
    text_file.close()
    DeleteMessage(cookiebot, telepot.message_identifier(msg['reply_to_message']))

def NovasRegras(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    cookiebot.sendMessage(chat_id, "Se vc é um admin, DÊ REPLY NESTA MENSAGEM com a mensagem que será exibida com o /regras", reply_to_message_id=msg['message_id'])

def Regras(cookiebot, msg, chat_id):
    cookiebot.sendChatAction(chat_id, 'typing')
    wait_open("Rules/Regras_" + str(chat_id)+".txt")
    if os.path.exists("Rules/Regras_" + str(chat_id)+".txt"):
        with open("Rules/Regras_" + str(chat_id)+".txt", encoding='utf-8') as file:
            regras = file.read()
        cookiebot.sendMessage(chat_id, regras+"\n\nDúvidas em relação ao bot? Mande para @MekhyW", reply_to_message_id=msg['message_id'])
    else:    
        cookiebot.sendMessage(chat_id, "Ainda não há regras colocadas para esse grupo\nPara tal, use o /novasregras", reply_to_message_id=msg['message_id'])