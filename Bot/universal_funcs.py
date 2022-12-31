googleAPIkey = ''
searchEngineCX = ''
cookiebotTOKEN = ''
bombotTOKEN = ''
mekhyID = 780875868
import os, math, numpy, random, time, datetime, re, sys, traceback
import urllib, json, requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, Message
from telepot.delegate import (per_chat_id, create_open, pave_event_space, include_callback_query_chat_id)
from telepot.exception import *
import googletrans
translator = googletrans.Translator()
backendauth = json.loads(open('cookiebot_backendauth.json', 'r').read())
login_backend, password_backend, serverIP = backendauth['login'], backendauth['password'], backendauth['serverIP']

def GetRequestBackend(route, params=None):
    response = requests.get(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False)
    try:
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return ''

def PostRequestBackend(route, params=None):
    response = requests.post(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False)
    try:
        print("POST: ", response.text)
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return ''

def PutRequestBackend(route, params=None):
    response = requests.put(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False)
    try:
        print("PUT: ", response.text)
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return ''

def DeleteRequestBackend(route, params=None):
    response = requests.delete(f'{serverIP}/{route}', json=params, auth = HTTPBasicAuth(login_backend, password_backend), verify=False)
    try:
        print("DELETE: ", response.text)
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return ''

def Send(cookiebot, chat_id, text, msg_to_reply=None, language="pt"):
    cookiebot.sendChatAction(chat_id, 'typing')
    if language == 'eng':
        text = translator.translate(text, dest='en').text
    elif language == 'es':
        text = translator.translate(text, dest='es').text
    if msg_to_reply:
        reply_id = msg_to_reply['message_id']
        cookiebot.sendMessage(chat_id, text, reply_to_message_id=reply_id)
    else:
        cookiebot.sendMessage(chat_id, text)

def SetMyCommands(cookiebot, commands, scope_chat_id, isBombot=False, language="pt"):
    if isBombot:
        token = bombotTOKEN
    else:
        token = cookiebotTOKEN
    url = 'https://api.telegram.org/bot{}/setMyCommands'.format(token)
    data = {'commands': commands,
            'scope': {'type': 'chat', 'chat_id': scope_chat_id},
            'language_code': language[0:2].lower()}
    print(requests.get(url, json=data))

def Forward(cookiebot, chat_id, from_chat_id, message_id, thread_id=None, isBombot=False):
    cookiebot.sendChatAction(chat_id, 'typing')
    if isBombot:
        token = bombotTOKEN
    else:
        token = cookiebotTOKEN
    if thread_id:
        url_req = f"https://api.telegram.org/bot{token}/forwardMessage?chat_id={chat_id}&from_chat_id={from_chat_id}&message_id={message_id}&message_thread_id={thread_id}"
        print(requests.get(url_req))
    else:
        cookiebot.forwardMessage(chat_id, from_chat_id, message_id)

def BanAndBlacklist(cookiebot, chat_id, user_id):
    PostRequestBackend(f'blacklist/{user_id}')
    cookiebot.kickChatMember(chat_id, user_id)

def LeaveAndBlacklist(cookiebot, chat_id):
    PostRequestBackend(f'blacklist/{chat_id}')
    cookiebot.leaveChat(chat_id)

def wait_open(filename):
    if os.path.exists(filename):
        try:
            text = open(filename, 'r')
            text.close()
        except IOError:
            time.sleep(1)

def DeleteMessage(cookiebot, identifier):
    try:
        cookiebot.deleteMessage(identifier)
    except Exception as e:
        print(e)

def check_if_string_in_file(file_name, string_to_search):
    for line in file_name:
        if string_to_search in line:
            return True
    return False