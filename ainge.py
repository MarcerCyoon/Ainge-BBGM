import json

def fileExists(fileName):
	try:
		open(fileName.strip(), "r", encoding='utf-8-sig')
	except FileNotFoundError:
		return 0

	return 1

print("Welcome to the Ainge-BBGM CLI tool, made to make your BBGM multiplayer commissioner life just a bit easier.\n")
fileName = input("For starters, please tell us your export's name (include .json): ")

while True:
	if (fileExists(fileName)):
		with open(fileName.strip(), "r", encoding='utf-8-sig') as file:
			export = json.load(file)
		break
	else:
		print("No such file exists!")
		fileName = input("Please re-input your export's name (include .json): ")

while True:
	print("\nCurrently modifying " + fileName + "...\n")
	print("Edit Options:")
	print("U. Type U to Update Export with FAs")
	print("T. Type T to Eliminate Transaction / Event")
	print("H. Type H for Help")
	choice = input().strip()

	if (choice == "U"):
		print("Woop")
		break
	elif (choice == "T"):
		print("lol")
		break
	elif (choice == "H"):
		print("You can use Ainge-BBGM to update your export or eliminate a transaction at the current moment.\n")
		print("Update Export: by typing U, you can choose to update your export with FA signings that were made.")
		print("All you need to do is include a CSV file in the same directory as Ainge-BBGM and the export ")
		print("in the specified format and simply enter its name.")
		print("The specified format is as follows: the columns must be Player Name, Team Signed With, Offer AAV, Offer Years")
		print("in that order. Each player decision should be a row; keep in mind the program will skip row one, assuming")
		print("it will be used for headers.\n")
		print("Eliminate Transaction: by typing T, you can choose to eliminate an accidetanl transaction that occured")
		print("whether it be because of Ainge-BBGM or if you simply butterfingered a trade.")
		print("All you must do is provide Ainge-BBGM with the information about the transaction.\n")