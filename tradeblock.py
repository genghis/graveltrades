import slack
import os
import json
import uuid
import boto3
import datetime
from flask import Flask, request

SLACK_TOKEN = os.environ['SLACK_OAUTH']
client = slack.WebClient(token=SLACK_TOKEN)
dynamodb = boto3.resource('dynamodb')
tradeblock = dynamodb.Table('tradeblock')

app = Flask(__name__)

def listblock():
	response_person = request.form.get('user_id')
	channel = request.form.get('channel_id')
	rows = tradeblock.scan(ProjectionExpression="username, available_players, needs")
	tradeblockblocks = [{"type": "section","text": {"type": "mrkdwn","text": "*The following players are on the block.*\n"}},{"type": "divider"}]
	
	for entry in rows['Items']:
		dealer = entry['username']
		available_players = entry['available_players']
		needs = entry['needs']
		blockjson = [
			{"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": f"{dealer} is willing to trade: \n{available_players} \n:wavy_dash::wavy_dash::wavy_dash:\n*He needs*: {needs}"
						}

			},
			{
			"type": "divider"
			},				
			{
			"type": "divider"
			},
			]
		tradeblockblocks.append(betjson[0])
		tradeblockblocks.append(betjson[1])
		tradeblockblocks.append(betjson[2])

	client.chat_postEphemeral(channel = channel, user = response_person, blocks = tradeblockblocks)

def firstdialog():
	trigger_id = request.form.get('trigger_id')

	dialogcontent = {
			"callback_id": "add",
			"title": "Gravelblock",
			"submit_label": "Add",
			"notify_on_cancel": False,
			"elements": [
			{
				"type": "text",
				"label": "Who do you want to add to your trade block?",
				"name": "tradable",
			},
			{
				"type": "select",
				"label": "What position do they play?",
				"name": "tradeableposition",
				"options": [
				{"label": "WR", "value": "WR"},
				{"label": "RB", "value": "RB"},
				{"label": "QB", "value": "QB"},
				{"label": "TE", "value": "TE"},
				{"label": "DST", "value": "DST"},
				{"label": "K", "value": "K"}
				]
			}
			{
				"type": "select",
				"label": "What positions do you need?",
				"name": "positionsofneed"
				"options": [
				{"label": "WR", "value": "WR"},
				{"label": "RB", "value": "RB"},
				{"label": "QB", "value": "QB"},
				{"label": "TE", "value": "TE"},
				{"label": "DST", "value": "DST"},
				{"label": "K", "value": "K"}
				]
			}
			]
			}

	client.dialog_open(dialog=dialogcontent,trigger_id=trigger_id)

def remove_player():
	response_person = request.form.get('user_id')
	channel = request.form.get('channel_id')
	username = request.form.get('user_name')
	trademaker = f"<@{response_person}|{username}>"
	
	mytradeblock = []
	myneeds = []

	tradeblocklist = tradeblock.get_item(Key={'username': trademaker})

	players = tradeblocklist['Items']['available_players']
	needs = tradeblocklist['Items']['needs']

	for player in players:
		mytradeblock.append({"label": player, "value": player})

	for need in needs:
		myneeds.append({"label": need, "value": need})

	dialogcontent = {
			"callback_id": "remove",
			"title": "Gravelblock",
			"submit_label": "Remove",
			"notify_on_cancel": False,
			"elements": [
			{
				"type": "select",
				"label": "Who do you want to remove from your trade block?",
				"name": "traderemove",
				"options": mytradeblock
			},
			{
				"type": "select",
				"label": "What position do you want to remove from needs?",
				"name": "needsremove",
				"options": myneeds
			}
			]
			}

	client.dialog_open(dialog=dialogcontent,trigger_id=trigger_id)

def add_to_block():
	userid = content['user']['id']
	username = content['user']['username']
	channelid = content['channel']['id']
	person = f"<@{challengedid}|{challengedname}>"
	slackaddress = content['response_url']
	available_player = content['submission']['tradable']
	position = content['submission']['tradeableposition']
	needs = content['submission']['positionsofneed']
	player = f"{available_player}, {position}"

	try:	
		tradeblock.put_item(
			Item={
				'username': username,
				'available_players': player,
				'needs': needs
			})
	except:
		tradeblock.update_item(
			Key={'username': username},
			UpdateExpression='set available_players = available_players + :val, needs = needs + :pon',
			ExpressionAttributeValues={
			':val': player,
			':pon': needs
			},
			ReturnValues="UPDATED_NEW")

@app.route('/dispatch')
def dispatch():
	raw = request.form.get('payload')
	content = json.loads(raw)
	if content['callback_id'] == "add":
		add_to_block(content)
	elif content['callback_id'] == "remove":
		remove_from_block(content)
	else:
		pass

	return '', 200

@app.route('/', methods=['POST'])
def lambda_handler():
	text = request.form.get('text')
	
	if text == 'list':
		listblock()
		return '', 200
	elif text == 'remove':
		removeplayer()
		return '', 200
	else:
		try:
			firstdialog()
		except:
			return "Whoops. Something went wrong. Tell Genghis what you tried to do and he'll tell you if you're an idiot"
		finally:
			return '', 200