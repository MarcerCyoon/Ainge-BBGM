import json

# updateExport() code copied entirely from DecisionMakerSLR.

# Update an existing export named "export.json" with Free Agency decisions found in a decisionArr.
# This should perfectly emulate actually signing them in the BBGM game.
def updateExport(isResign, decisionArr, exportName):
	print(decisionArr)

	with open(exportName, "r", encoding='utf-8-sig') as file:
	    export = json.load(file)

	# Generate dictionary of each team and their tids
	teamDict = dict()
	for team in export['teams']:
			teamName = team['region'] + " " + team['name']
			teamDict[teamName] = team['tid']

	text = export['meta']['phaseText']
	currentYear = int(text.split(" ")[0])
	phase = text.split(" ")[1]

	for decision in decisionArr:
		player = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == decision[0], export['players']))[0]
		tid = teamDict[decision[1]]
		player['tid'] = tid
		player['contract']['amount'] = decision[2] * 1000

		# If the current phase of the game is the "Regular Season" or the "Preseason",
		# then signing a contract will include the current year.
		# For example, if Isaiah Thomas signs a 1-year deal in 2020, it will expire at the end of 2020.
		# However, if you sign Isaiah Thomas in a 1-year deal in the 2020 offseason, it will expire at
		# the end of 2021. Thus, a distinction needs to be made depending on the current phase.
		if (phase == "regular" or phase == "preseason"):
			exp = decision[3] + currentYear - 1
			player['contract']['exp'] = exp
		else:
			exp = decision[3] + currentYear
			player['contract']['exp'] = exp

		# To fully emulate the way signings are worked in-game, we must also create a corresponding event
		# in the game's code that tells us that so-and-so signed with such-and-such team. This is important
		# not only for error-identification purposes, but also makes league history and transactions
		# be kept complete.
		event = dict()

		# For some reason, the text for events only necessitates the team code and "label name": we only need
		# Celtics, not Boston Celtics.
		code = list(filter(lambda team: team['tid'] == tid, export['teams']))[0]['abbrev']
		labelName = decision[1].split(" ")[-1]
		
		if (not isResign):
			event['type'] = 'reSigned'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> re-signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % decision[2], exp)

		else:
			event['type'] = 'freeAgent'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % decision[2], exp)
		
		event['pids'] = [player['pid']]
		event['tids'] = [tid]
		event['season'] = currentYear
		# The eid of the current event would have to be the next available eid.
		# That would just be the current amount of events, as each event has a corresponding
		# eid and they start at 0 instead of 1.
		event['eid'] = len(export['events'])

		export['events'].append(event)

	with open("updated.json", "w") as file:
		json.dump(export, file)
		print("New Export Created.")

def eventExists(eid, export):
	try:
		event = list(filter(lambda event: event['eid'] == int(eid), export['events']))[0]
	except IndexError:
		return 0

	return 1


def deleteTransaction(eid, exportName):
	with open(exportName, "r", encoding="utf-8-sig") as file:
		export = json.load(file)

	if (eventExists(eid, export)):
		event = list(filter(lambda event: event['eid'] == int(eid), export['events']))[0]
	else:
		print("No event with inputted EID exists!")
		return 0

	print("Removing following event: ")
	print(event)

	export['events'].remove(event)

	# Fixing all the eids so there isn't a random gap
	for i in range(int(eid), len(export['events'])):
		export['events'][i]['eid'] = i

	with open("updated.json", "w") as file:
		json.dump(export, file)
		print("New Export Created.")