from universal_funcs import *
from UserRegisters import *
import google_images_search, googleapiclient.discovery
from saucenao_api import SauceNao, errors
import cv2
import numpy as np
googleimagesearcher = google_images_search.GoogleImagesSearch(googleAPIkey, searchEngineCX, validate_images=False)
youtubesearcher = googleapiclient.discovery.build("youtube", "v3", developerKey=googleAPIkey)
reverseimagesearcher = SauceNao(saucenao_key)
templates_eng = os.listdir("Static/Meme/English")
templates_pt = os.listdir("Static/Meme/Portuguese")
fighters_eng = os.listdir("Static/Fight/English")
fighters_pt = os.listdir("Static/Fight/Portuguese")

with open('Static/avoid_search.txt', 'r') as f:
    avoid_search = f.readlines()
avoid_search = [x.strip() for x in avoid_search]

def fetchTempJpg(cookiebot, msg, only_return_url=False):
    try:
        path = cookiebot.getFile(msg['photo'][-1]['file_id'])['file_path']
        image_url = f'https://api.telegram.org/file/bot{cookiebotTOKEN}/{path}'
        if only_return_url:
            return image_url
        urllib.request.urlretrieve(image_url, 'temp.jpg')
    except KeyError:
        path = cookiebot.getFile(msg['document']['file_id'])['file_path']
        video_url = f'https://api.telegram.org/file/bot{cookiebotTOKEN}/{path}'
        if only_return_url:
            return video_url
        urllib.request.urlretrieve(video_url, 'temp.mp4')
        vidcap = cv2.VideoCapture('temp.mp4')
        success, image = vidcap.read()
        cv2.imwrite('temp.jpg', image)
        os.remove('temp.mp4')

def getMembersTagged(msg):
    members_tagged = []
    if '@' in msg['text']:
        for target in msg['text'].split("@")[1:]:
            if 'CookieMWbot' in target:
                continue
            members_tagged.append(target)
    return members_tagged

def ReverseSearch(cookiebot, msg, chat_id, language, isBombot=False):
    SendChatAction(cookiebot, chat_id, 'typing')
    if not 'reply_to_message' in msg:
        Send(cookiebot, chat_id, "Responda uma imagem com o comando para procurar a fonte (busca reversa)\n>\(Para busca direta, use o /qualquercoisa\)", msg, language)
        return
    url = fetchTempJpg(cookiebot, msg['reply_to_message'], only_return_url=True)
    try:
        results = reverseimagesearcher.from_url(url)
    except errors.ShortLimitReachedError:
        Send(cookiebot, chat_id, "Ainda estou processando outros resultados, aguarde e tente novamente", msg, language)
        return
    except errors.LongLimitReachedError:
        Send(cookiebot, chat_id, "Limite diário de busca atingido, aguarde e tente novamente", msg, language)
        return
    if results and results[0].urls and results[0].similarity > 80:
        best = results[0]
        answer = 'Melhor correspondência encontrada:\n\n'
        answer += f'"{best.title}"'
        if best.author:
            answer +=  f" - {best.author}"
        answer += f"\n{best.urls[0]}\n\n"
        ReactToMessage(msg, '🫡', is_big=False, isBombot=isBombot)
        Send(cookiebot, chat_id, answer, msg, language)
    else:
        ReactToMessage(msg, '🤷', is_big=False, isBombot=isBombot)
        Send(cookiebot, chat_id, "A busca não encontrou correspondência, parece ser uma imagem original!", msg, language)

def PromptQualquerCoisa(cookiebot, msg, chat_id, language):
    Send(cookiebot, chat_id, "Troque o 'qualquercoisa' por algo, vou mandar uma foto desse algo\n>EXEMPLO: /fennec", msg, language)

def QualquerCoisa(cookiebot, msg, chat_id, sfw, language, isBombot=False):
    searchterm = msg['text'].split("@")[0].replace("/", ' ').replace("@CookieMWbot", '')
    if searchterm.split()[0] in avoid_search:
        return
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    if sfw == 0:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'off', 'filetype':'jpg|gif|png'})
    else:
        googleimagesearcher.search({'q': searchterm, 'num': 10, 'safe':'medium', 'filetype':'jpg|gif|png'})
    images = googleimagesearcher.results()
    random.shuffle(images)
    for image in images:
        try:
            if 'gif' in image.url:
                cookiebot.sendAnimation(chat_id, image.url, reply_to_message_id=msg['message_id'], caption=image.referrer_url)
            else:
                cookiebot.sendPhoto(chat_id, image.url, reply_to_message_id=msg['message_id'], caption=image.referrer_url)
            return 1
        except Exception as e:
            print(e)
    ReactToMessage(msg, '🤷', is_big=False, isBombot=isBombot)
    Send(cookiebot, chat_id, "Não consegui achar uma imagem _\(ou era NSFW e eu filtrei\)_", msg, language)

def YoutubeSearch(cookiebot, msg, chat_id, language):
    if len(msg['text'].split()) == 1:
        Send(cookiebot, chat_id, "Você precisa digitar o nome do vídeo\n>EXEMPLO: /youtube batata assada", msg, language)
        return
    query = ' '.join(msg['text'].split()[1:])
    request = youtubesearcher.search().list(q=query, part="snippet", type="video", maxResults=10)
    response = request.execute()
    videos = response.get("items", [])
    if not videos:
        Send(cookiebot, chat_id, "Nenhum vídeo encontrado", msg, language)
        return
    random_video = random.choice(videos)
    video_url = f"https://www.youtube.com/watch?v={random_video['id']['videoId']}"
    video_description = random_video["snippet"]["description"]
    Send(cookiebot, chat_id, f"<i>{video_url}</i>\n\n<b>{video_description}</b>", msg, language, parse_mode='HTML')

def AddtoRandomDatabase(msg, chat_id, photo_id=''):
    if any(x in msg['chat']['title'].lower() for x in ['yiff', 'porn', '18+', '+18', 'nsfw', 'hentai', 'rule34', 'r34', 'nude', '🔞']):
        return
    if not 'forward_from' in msg and not 'forward_from_chat' in msg:
        PostRequestBackend('randomdatabase', {'id': chat_id, 'idMessage': str(msg['message_id']), 'idMedia': photo_id})

def ReplyAleatorio(cookiebot, msg, chat_id, thread_id=None, isBombot=False):
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    for attempt in range(50):
        try:
            target = GetRequestBackend("randomdatabase")
            Forward(cookiebot, chat_id, target['id'], target['idMessage'], thread_id=thread_id, isBombot=isBombot)
            break
        except Exception as e:
            print(e)

def AddtoStickerDatabase(msg, chat_id):
    if any(x in msg['chat']['title'].lower() for x in ['yiff', 'porn', '18+', '+18', 'nsfw', 'hentai', 'rule34', 'r34', 'nude', '🔞']):
        return
    if 'emoji' in msg['sticker'] and msg['sticker']['emoji'] in ['🍆', '🍑', '🥵', '💦', '🫦']:
        return
    stickerId = msg['sticker']['file_id']
    PostRequestBackend('stickerdatabase', {'id': stickerId})

def ReplySticker(cookiebot, msg, chat_id):
    sticker = GetRequestBackend("stickerdatabase")
    cookiebot.sendSticker(chat_id, sticker['id'], reply_to_message_id=msg['message_id'])

def Meme(cookiebot, msg, chat_id, language):
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    members = GetMembersChat(chat_id)
    members_tagged = getMembersTagged(msg)
    caption = ""
    for attempt in range(100):
        if 'pt' not in language.lower():
            template = "Static/Meme/English/" + random.choice(templates_eng)
        else:
            template_id = random.randint(0, len(templates_pt)+len(templates_eng)-1)
            if template_id > len(templates_eng)-1:
                template = "Static/Meme/Portuguese/" + templates_pt[template_id-len(templates_eng)]
            else:
                template = "Static/Meme/English/" + templates_eng[template_id]
        template_img = cv2.imread(template)
        mask_green = cv2.inRange(template_img, (0, 210, 0), (40, 255, 40))
        mask_red = cv2.inRange(template_img, (0, 0, 210), (40, 40, 255))
        contours_green, tree = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(members_tagged) <= len(contours_green):
            break
    for green in contours_green:
        x, y, w, h = cv2.boundingRect(green)
        for attempt in range(100):
            if len(members_tagged):
                chosen_member = random.choice(members_tagged)
                members_tagged.remove(chosen_member)
                members = [member for member in members if 'user' not in member or member['user'] != chosen_member]
            else:
                try:
                    chosen_member = random.choice(members)
                except IndexError:
                    return Meme(cookiebot, msg, chat_id, language)
                members.remove(chosen_member)
                if 'user' in chosen_member:
                    chosen_member = chosen_member['user']
                else:
                    continue
            try:
                url = f"https://telegram.me/{chosen_member}"
            except IndexError:
                continue
            req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"}) 
            html = urllib.request.urlopen(req)
            soup = BeautifulSoup(html, "html.parser")
            images = list(soup.findAll('img'))
            if len(images):
                break
        resp = urllib.request.urlopen(images[0]['src'])
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (w, h), interpolation=cv2.INTER_NEAREST)
        mask_green_copy = mask_green[y:y+h, x:x+w]
        for i in range(y, y+h):
            for j in range(x, x+w):
                if mask_green_copy[i-y, j-x] == 255:
                    template_img[i, j] = image[i-y, j-x]
        caption += f"@{chosen_member} "
    cv2.imwrite("meme.png", template_img)
    with open("meme.png", 'rb') as final_img:
        SendPhoto(cookiebot, chat_id, photo=final_img, caption=caption, msg_to_reply=msg)
    try:
        os.remove("meme.png")
    except FileNotFoundError:
        pass

def Batalha(cookiebot, msg, chat_id, language, isBombot=False):
    ReactToMessage(msg, '🔥', isBombot=isBombot)
    SendChatAction(cookiebot, chat_id, 'upload_photo')
    members_tagged = getMembersTagged(msg)
    if len(members_tagged):
        user = members_tagged[0]
        html = urllib.request.urlopen(urllib.request.Request(f"https://telegram.me/{user}", headers={'User-Agent' : "Magic Browser"}))
        soup = BeautifulSoup(html, "html.parser")
        images = list(soup.findAll('img'))
        if not len(images):
            Send(cookiebot, chat_id, "Não consegui extrair a foto de perfil desse usuário", msg, language)
            return
        resp = urllib.request.urlopen(images[0]['src'])
        user_image = cv2.imdecode(np.asarray(bytearray(resp.read()), dtype="uint8"), cv2.IMREAD_COLOR)
        cv2.imwrite("user.jpg", user_image)
        user_image = open("user.jpg", 'rb')
    else:
        if 'username' in msg['from']:
            user = msg['from']['username']
        else:
            user = msg['from']['first_name']
        try:
            user_image = cookiebot.getUserProfilePhotos(msg['from']['id'], limit=1)['photos'][0][-1]['file_id']
        except IndexError:
            Send(cookiebot, chat_id, "Você precisa ter uma foto de perfil _\(ou está privado\)_", msg, language)
            return
    if language == 'pt':
        fighters = [fighters_eng, fighters_pt]
        fighter = random.choice(random.choices(fighters, weights=map(len, fighters))[0])
        if fighter in fighters_eng:
            fighter_image = cv2.imread("Static/Fight/English/" + fighter)
        else:
            fighter_image = cv2.imread("Static/Fight/Portuguese/" + fighter)
        poll_title = "QUEM VENCE " + random.choice(["NO TAPA", "NO X1", "NO SOCO", "NA MÃO", "NA PORRADA", "NO ARGUMENTO", "NO DUELO", "NA VIDA"]) + "?"
    else:
        fighter = random.choice(fighters_eng)
        fighter_image = cv2.imread("Static/Fight/English/" + fighter)
        if language == 'es':
            poll_title = "¿QUIÉN GANA?"
        else:
            poll_title = "WHO WINS?"
    fighter = fighter.replace(".png", "").replace(".jpg", "").replace(".jpeg", "").replace("_", " ").capitalize()
    cv2.imwrite("fighter.jpg", fighter_image)
    with open("fighter.jpg", 'rb') as fighter_image_binary:
        medias, caption, choices = [{'type': 'photo', 'media': user_image}, {'type': 'photo', 'media': fighter_image_binary}], f"{user} VS {fighter}", [user, fighter]
        if random.choice([0, 1]):
            medias, caption, choices = [medias[1], medias[0]], f"{fighter} VS {user}", [fighter, user]
        medias[0]['caption'] = caption
        cookiebot.sendMediaGroup(chat_id, medias, reply_to_message_id=msg['message_id'])
        cookiebot.sendPoll(chat_id, poll_title, choices, is_anonymous=False, allows_multiple_answers=False, reply_to_message_id=msg['message_id'], open_period=600)