#Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
from itertools import product
from nltk.corpus import wordnet as wn

from steve import *

app = Flask(__name__)
ACCESS_TOKEN = '<redacted>'
VERIFY_TOKEN = '<redacted>'
bot = Bot(ACCESS_TOKEN)

follow_up = False
table_event = True
new_obj = None

class comm_event(object):
	def __init__(self, obj):
		self.action = obj['action']
		self.event = "Undefined"
		if obj['what']:
			self.event = obj['what'].lower()
		self.time = obj['when']
		self.location = "Undefined"
		if len(obj['where']):
			self.location = ' '.join(obj['where'])
		self.people = obj['people']
		self.question = obj['question']
		self.count = 1

	def similar(self, comm_obj):
		ac1, ac2 = self.action, comm_obj.action
		sem1, sem2 = wn.synsets(ac1), wn.synsets(ac2)

		maxscore = 0
		for i,j in list(product(*[sem1,sem2])):
			print(i)
			print(j)
			score = i.wup_similarity(j) # Wu-Palmer Similarity
			print(score)

			try:
				maxscore = score if maxscore < score else maxscore
			except TypeError as e:
				pass
			else:
				pass
			finally:
				pass

		if maxscore > 0.9:
			return True

		return False

class comm_concern(object):
	def __init__(self, obj):
		self.action = obj['action']
		self.event = obj['what'].lower()
		self.time = obj['when']
		self.location = "Undefined"
		if len(obj['where']):
			self.location = ' '.join(obj['where'])
		self.people = obj['people']
		self.question = obj['question']
		self.count = 1
	
	def similar(self, comm_obj):
		ac1, ac2 = self.event, comm_obj.event
		def jaccard(joinKey1, joinKey2):
			r = set(joinKey1.split())
			s = set(joinKey2.split())

			unionset = r.union(s)
			intersectionset = r.intersection(s)

			jaccard_ind = len(intersectionset) / len(unionset)

			return jaccard_ind

		if jaccard(ac1, ac2) > 0.9:
			return True

		return False

event_list = []
concern_list = []

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
						response_sent_text = get_message(message['message'].get('text'))
						send_message(recipient_id, response_sent_text)
	return "Message Processed"


def verify_fb_token(token_sent):
	#take token sent by facebook and verify it matches the verify token you sent
	#if they match, allow the request, else return an error 
	if token_sent == VERIFY_TOKEN:
		return request.args.get("hub.challenge")
	return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(sentence):

	global follow_up, table_event, new_obj

	if follow_up:
		if table_event:

			if "n" not in sentence.lower():
				event_list.append(new_obj)
				new_obj = None
				follow_up = False

				return "I have added your event to the list now! What else can I help you with?"

			else:
				new_obj = None
				follow_up = False
				return "Thanks for letting me know. What else can I help you with?"

		else:
			if "n" not in sentence.lower():
				concern_list.append(new_obj)
				new_obj = None
				follow_up = False

				return "I have added your concern to the list now! What else can I help you with?"

			else:
				new_obj = None
				follow_up = False
				return "Thanks for letting me know. What else can I help you with?"
	
	res, concern = detect_intent(sentence)
	res = res[0]

	if 'hello' in sentence.lower() or sentence.split()[0].lower() == 'hi':
		return "Hi! How can I help you today?"
	else:
		if concern:
			
			new_obj = comm_concern(res)

			possible = []

			for x in concern_list:
				if x.similar(new_obj):

					if not res['question']:

						x.count += 1
						new_obj = None

						resp = "I found the following similar concern ...\n\n"
						resp = "WHAT: "+x.action+" "+x.event+"\n"
						resp += "WHEN: "+x.time+"\n"
						resp += "WHERE: "+x.location+"\n"
						resp += "\n"
						resp += "I added your vote to the problem. What else can I help you with?"

					else:
						possible.append(x)

			if len(possible):

				resp = "I know of the following familiar issues out there:\n\n"

				for x in possible:
					new_pos = "WHAT: "+x.action+" "+x.event+"\n"
					new_pos += "WHEN: "+x.time+"\n"
					new_pos += "WHERE: "+x.location+"\n"
					new_pos += "\n"

					resp += new_pos

				return resp
			
			else:

				follow_up = True
				table_event = False

				return "This issue hasn't been raised before. Do you want me to add it?"

		else:
			new_obj = comm_event(res)

			possible = []

			for x in event_list:
				if x.similar(new_obj):
					possible.append(x)

			if len(possible):

				resp = "I know of the following familiar events out there:\n\n"

				for x in possible:
					new_pos = "WHAT: "+x.action+" "+x.event+"\n"
					new_pos += "WHEN: "+str(x.time)+"\n"
					new_pos += "WHERE: "+x.location+"\n"
					new_pos += "\n"

					resp += new_pos

				return resp
			
			else:

				follow_up = True
				table_event = True

				return "No such event exists. Do you want me to add it?"


#uses PyMessenger to send response to user
def send_message(recipient_id, response):
	#sends user the text message provided via input response parameter
	bot.send_text_message(recipient_id, response)
	return "success"

if __name__ == "__main__":
	app.run(debug=True)