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

	currentYear = export['gameAttributes']['season']
	phase = export['gameAttributes']['phase']

	for decision in decisionArr:
		print(decision[0])
		player = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == decision[0] and player['tid'] == -1, export['players']))[-1]
		tid = teamDict[decision[1]]
		player['tid'] = tid
		player['contract']['amount'] = float(decision[2]) * 1000

		if "Player Option" in decision[4] or "PO" in decision[4]:
			player['lastName'] = player['lastName'].strip()
			player['lastName'] += " (PO)"
			# Do this line so that for players having no last name, there aren't two weird spaces
			player['lastName'] = player['lastName'].strip()

		elif "Team Option" in decision[4] or "TO" in decision[4]:
			player['lastName'] = player['lastName'].strip()
			player['lastName'] += " (TO)"
			# Do this line so that for players having no last name, there aren't two weird spaces
			player['lastName'] = player['lastName'].strip()

		# If the current phase of the game is the "Regular Season" or the "Preseason",
		# then signing a contract will include the current year.
		# For example, if Isaiah Thomas signs a 1-year deal in 2020, it will expire at the end of 2020.
		# However, if you sign Isaiah Thomas in a 1-year deal in the 2020 offseason, it will expire at
		# the end of 2021. Thus, a distinction needs to be made depending on the current phase.
		if (phase < 4):
			firstYearOfContract = currentYear

		else:
			firstYearOfContract = currentYear + 1

		exp = int(decision[3]) + firstYearOfContract - 1
		player['contract']['exp'] = exp

		# Second, we must also correct every player's salary info and add the new contract amount
		# such that their career earnings are updated.
		for i in range(firstYearOfContract, exp + 1):
			salaryInfo = dict()
			salaryInfo['season'] = i
			salaryInfo['amount'] = float(decision[2]) * 1000
			player['salaries'].append(salaryInfo)

		# To fully emulate the way signings are worked in-game, we must also create a corresponding event
		# in the game's code that tells us that so-and-so signed with such-and-such team. This is important
		# not only for error-identification purposes, but also makes league history and transactions
		# be kept complete.
		event = dict()

		# For some reason, the text for events only necessitates the team code and "label name": we only need
		# Celtics, not Boston Celtics.
		code = list(filter(lambda team: team['tid'] == tid, export['teams']))[0]['abbrev']
		labelName = list(filter(lambda team: team['tid'] == tid, export['teams']))[0]['name']
		
		if int(isResign):
			event['type'] = 'reSigned'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> re-signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % float(decision[2]), exp)

		else:
			event['type'] = 'freeAgent'
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> signed <a href=\"/l/1/player/{}\">{}</a> for ${}M/year through {}.".format(code, currentYear, labelName, player['pid'], decision[0], "%0.2f" % float(decision[2]), exp)
		
		event['pids'] = [player['pid']]
		event['tids'] = [tid]
		event['season'] = currentYear
		# The eid of the current event would have to be the next available eid.
		# That would just be the current amount of events, as each event has a corresponding
		# eid and they start at 0 instead of 1.
		event['eid'] = len(export['events'])

		export['events'].append(event)

		# We must also create a transaction dictionary for the player if it is not a re-signing.
		if not int(isResign):
			gamePhase = export['gameAttributes']['phase']
			transaction = {
				"season": currentYear,
				"phase": gamePhase,
				"tid": tid,
				"type": "freeAgent"
			}
			try:
				player['transactions'].append(transaction)
			except KeyError:
				player['transactions'] = []
				player['transactions'].append(transaction)

	newFile = exportName.replace(".json", "") + "_updated.json"

	with open(newFile, "w") as file:
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

	newFile = exportName.replace(".json", "") + "_updated.json"

	with open(newFile, "w") as file:
		json.dump(export, file)
		print("New Export Created.")

# Print Current Standings in Export, with some additional features for Discord support
def printStandings(exportName, useEmojis=False, useAts=False):
	with open(exportName, "r", encoding="utf-8-sig") as file:
		export = json.load(file)

	teams = export['teams']
	currentYear = export['gameAttributes']['season']

	eastArr = []
	westArr = []

	for team in teams:
		teamName = team['region'].strip() + " " + team['name'].strip()
		wins = team['seasons'][-1]['won']
		losses = team['seasons'][-1]['lost']
		win_per = wins / team['seasons'][-1]['gp']

		if (team['cid'] == 0):
			eastArr.append([teamName, wins, losses, win_per])
		else:
			westArr.append([teamName, wins, losses, win_per])

	eastArr = sorted(eastArr, key=lambda i:i[3], reverse=True)
	westArr = sorted(westArr, key=lambda i:i[3], reverse=True)

	print("__**" + currentYear + " STANDINGS **__")
	print("**EASTERN CONFERENCE**")
	for i in range(0, len(eastArr)):
		standing = i + 1
		emoji_text = ":" + list(filter(lambda team: (team['region'].strip() + " " + team['name'].strip() == eastArr[i][0]), export['teams']))[0]['name'].lower().replace(" ", "") + ": "
		print("{}) {}{} {}{}-{}".format(standing, "@" if useAts else "", eastArr[i][0], emoji_text if useEmojis else "", eastArr[i][1], eastArr[i][2]))
		if (i == 7):
			print("")

	print("")
	print("**WESTERN CONFERENCE**")
	for i in range(0, len(westArr)):
		standing = i + 1
		emoji_text = ":" + list(filter(lambda team: (team['region'].strip() + " " + team['name'].strip() == westArr[i][0]), export['teams']))[0]['name'].lower().replace(" ", "") + ": "
		print("{}) {}{} {}{}-{}".format(standing, "@" if useAts else "", westArr[i][0], emoji_text if useEmojis else "", westArr[i][1], westArr[i][2]))
		if (i == 7):
			print("")

# Pick up options based on a CSV of specified format.
def pickupOptions(optionsArr, exportName):
	print(optionsArr)
	with open(exportName, "r", encoding="utf-8-sig") as file:
		export = json.load(file)

	# Generate dictionary of each team and their tids
	teamDict = dict()
	for team in export['teams']:
			teamName = team['region'] + " " + team['name']
			teamDict[teamName] = team['tid']

	currentYear = export['gameAttributes']['season']

	for option in optionsArr:
		print(option[0])
		player = list(filter(lambda player: (player['firstName'].strip() + " " + player['lastName'].strip()) == option[0], export['players']))[-1]
		tid = teamDict[option[1]]
		player['tid'] = tid
		optionAmount = player['salaries'][-1]['amount']
		# Options are always during re-signings / off-season
		optionExp = currentYear + 1
		player['contract']['amount'] = optionAmount
		player['contract']['exp'] = optionExp
		player['salaries'].append({'season': optionExp, 'amount': optionAmount})

		if "(TO)" in player['lastName']:
			player['lastName'] = player['lastName'].replace("(TO)", "")

		elif "(PO)" in player['lastName']:
			player['lastName'] = player['lastName'].replace("(PO)", "")

		player['lastName'] = player['lastName'].strip()

		# Time to instantiate the custom event.
		event = dict()

		# For some reason, the text for events only necessitates the team code and "label name": we only need
		# Celtics, not Boston Celtics.
		code = list(filter(lambda team: team['tid'] == tid, export['teams']))[0]['abbrev']
		labelName = list(filter(lambda team: team['tid'] == tid, export['teams']))[0]['name']

		event['type'] = 'reSigned'

		if "Team Option" in option[2] or "TO" in option[2]:
			event['text'] = "The <a href=\"/l/1/roster/{}/{}\">{}</a> picked up <a href=\"/l/1/player/{}\">{}</a>'s team option.".format(code, currentYear, labelName, player['pid'], option[0])

		elif "Player Option" in option[2] or "PO" in option[2]:
			event['text'] = "<a href=\"/l/1/player/{}\">{}</a> picked up their player option with the <a href=\"/l/1/roster/{}/{}\">{}</a>.".format(player['pid'], option[0], code, currentYear, labelName)

		else:
			print("Error!")
			return

		event['pids'] = [player['pid']]
		event['tids'] = [tid]
		event['season'] = currentYear
		# The eid of the current event would have to be the next available eid.
		# That would just be the current amount of events, as each event has a corresponding
		# eid and they start at 0 instead of 1.
		event['eid'] = len(export['events'])

		export['events'].append(event)

	newFile = exportName.replace(".json", "") + "_updated.json"

	with open(newFile, "w") as file:
		json.dump(export, file)
		print("New Export Created.")

def updateFinances(financesArr, exportName):
	print(financesArr)
	with open(exportName, "r", encoding="utf-8-sig") as file:
		export = json.load(file)

	# Keeps track of teams that did finances
	teamsWithFinances = []

	# Rows go following — team name, coaching, health, facilities
	for finances in financesArr:
		team = list(filter(lambda team: team['region'] + " " + team['name'] == finances[0], export['teams']))[0]
		teamsWithFinances.append(team['region'])

		# Check if finances add up to 100.
		if not (int(finances[1]) + int(finances[2]) + int(finances[3]) == 100):
			print("Uh oh! {}'s finances do not add up to 100!".format(team['region']))
			return

		team['budget']['coaching']['amount'] = int(finances[1]) * 1000
		team['budget']['health']['amount'] = int(finances[2]) * 1000
		team['budget']['facilities']['amount'] = int(finances[3]) * 1000

	for team in export['teams']:
		if team['region'] not in teamsWithFinances:
			team['budget']['coaching']['amount'] = 33000
			team['budget']['health']['amount'] = 33000
			team['budget']['facilities']['amount'] = 33000

		# Delete keys to force them to auto-update and correct rank
		del team['budget']['coaching']['rank']
		del team['budget']['health']['rank']
		del team['budget']['facilities']['rank']

	newFile = exportName.replace(".json", "") + "_updated.json"

	with open(newFile, "w") as file:
		json.dump(export, file)
		print("New Export Created.")
		print("Remember to press 'Save Revenue and Expenses Settings' once on any team to get rank to display correctly!")

 