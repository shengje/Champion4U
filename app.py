#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
from pymessenger import Element
import run

app = Flask(__name__)
ACCESS_TOKEN = 'EAAFWqaTorUsBAJwz6Na8ANSBDowBAUwYn4zCViUcZCv65EHXeRtvVtqpZCxc26ZAVDFlD4FRE8iXQ1nDMBbJEQ3bAMZCntzcpOP6inZAAxZCmsvY1lyvUEeJZBrhy8AaqZByK7LAPJvvHoG2K5tZCCOvLirSV3SZBtPguZCIg8ZBzq2jaf03CQYVcHIr'
VERIFY_TOKEN = 'VERIFY_TOKEN'
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        mode = message['message']['text']
                        if mode[:4] == '推薦英雄':
                            response_sent_text = get_recommend(mode[4:])
                        elif mode[:4] == '對戰選角':
                            response_sent_text = choose_champ(mode[4:])
                        elif mode[:4] == '查詢英雄':
                            send_url(recipient_id, mode[4:])
                            response_sent_text = 'Please check'
                        else:
                            response_sent_text = mode_select()
                        send_message(recipient_id, response_sent_text)
                        #send_message(recipient_id, message['message']['text'])
                    #if user sends us a GIF, photo,video, or any other non-text item
                    # if message['message'].get('attachments'):
                    #     response_sent_nontext = get_message()
                    #     send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_recommend(name):
    recommend = run.main(name, 'kda')
    if recommend == 'error':
        responses = 'Not found Your ID: '+name+'\nPleas enter\n推薦英雄+ID'
    else:
        responses = 'Recommend List\n#1 '+\
                    recommend[0]+'\n#2 '+\
                    recommend[1]+'\n#3 '+\
                    recommend[2]+'\n#4 '+\
                    recommend[3]+'\n#5 '+\
                    recommend[4]
    # if name == '閃電龍爪手郭峰':
    #     responses = 'Recommend List\n#1 Thresh\n#2 Alistar\n#3 Rakan\n#4 Pyke\n#5 Morgana'

    # return selected item to the user
    return responses

def send_url(recipient_id, champ):
    elements = []
    if run.champion_name(champ):
        element = Element(title="Champion", image_url="http://opgg-static.akamaized.net/images/lol/champion/"+champ+".png", subtitle=champ, item_url='http://tw.op.gg/champion/'+champ)
    else:
        element = Element(title="Champion", image_url="http://opgg-static.akamaized.net/images/logo/logo-lol.png", subtitle="Champion List", item_url='http://tw.op.gg/champion/statistics')
    elements.append(element)
    bot.send_generic_message(recipient_id, elements)

def choose_champ(road):
    if road == "Support":
        responses = 'Recommend List\n#1 Thresh\n#2 Alistar\n#3 Rakan\n#4 Pyke\n#5 Morgana'
    else:
        responses = 'Sorry, we still working on this function...'

    return responses

def mode_select():
    response = 'Choose Mode:\n(Please type)\n推薦英雄+ID\n對戰選角+road\n查詢英雄+name'
    return response

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()