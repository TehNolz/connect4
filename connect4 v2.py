#By Niels van de Kerkhof
#0961007@hr.nl

import turtle
import socket
import logging
from ast import literal_eval
from random import randint
from multiprocessing import Process

logging.basicConfig(level=logging.NOTSET)
clientlog = logging.getLogger("CLIENT")
log = logging.getLogger("AI")

if __name__ == '__main__':
	#Create turtle
	t = turtle.Turtle()
	t.hideturtle()

	#Create screen
	ts = turtle.Screen()
	ts.title("Connect Four!")
	ts.tracer(0, 0) #Gotta go fast
	ts.screensize()
	ts.setup(width = 1.0, height = 1.0)

	#Create global vars
	gameBusy = False
	playerCount = 2
	width = 7
	height = 6
	AICount = 0
	winSeqLength = 4
	openMainMenu = False
	playerColors = ["White", "Red", "Blue", "chartreuse2", "Yellow", "Aqua", "Orange", "Gray", "Lightpink"]
moveHistory = []

#Main function
def main(clickx=-999, clicky=-999):
	global gameBusy
	global gameMode
	global playerCount
	global width
	global height
	global AICount
	global winSeqLength
	global currentPlayer
	global playerID
	global openMainMenu
	global c

	#Convert clickx and clicky to the better coordinate system
	clickx = int((clickx//50)+9)
	clicky = int((clicky//50)+4)

	if gameBusy == False:
		gameBusy = True

		if openMainMenu:
			mainMenu()
		elif currentScreen == "mainMenu":
			if -4 <= clickx <= -1 and clicky == 0:
				gameMode = "joingame"
				setup("player")

			if -4 <= clickx <= -1 and clicky == 2:
				gameMode = "hostgame"
				serverProcess = Process(name = "Connect4Server", target = server, args=(gameMode, width, height, playerCount, AICount, winSeqLength))
				serverProcess.start()
				setup("player")

			if -4 <= clickx <= -1 and clicky == 4:
				gameMode = "spectator"
				setup("spectator")

			if -4 <= clickx <= -1 and clicky == 6:
				gameMode = "singleplayer"
				serverProcess = Process(name = "Connect4Server", target = server, args=(gameMode, width, height, playerCount, AICount, winSeqLength))
				serverProcess.start()
				setup("player")

			if 4 <= clickx <= 8 and clicky == 0:
				width = promptInt("Please enter the width of the field.", 7, 7, 18)
				mainMenu()
			if 4 <= clickx <= 8 and clicky == 2:
				height = promptInt("Please enter the height of the field.", 6, 6, 10)
				mainMenu()
			if 4 <= clickx <= 8 and clicky == 4:
				playerCount = promptInt("How many players?", 2, 2, 8)
				if AICount > playerCount:
					AICount = playerCount
				mainMenu()
			if 4 <= clickx <= 8 and clicky == 6:
				AICount = promptInt("How many AI?", 0, 0, playerCount)
				mainMenu()
			if 4 <= clickx <= 8 and clicky == 8:
				winSeqLength = promptInt("How long should the winning sequence be?", 4, 2, min([width, height]))
				mainMenu()
		elif currentScreen == "gameBoard":
			if 0 <= clickx <= width-1 and 0 <= clicky <= height-1:
				if placeStone(clickx, currentPlayer):
					clientlog.info("Successfully placed stone at "+str(clickx)+" for player "+str(currentPlayer))
					sendData(c, {"MOVE"})
					sendData(c, clickx)
					waitForTurn()
			
			#Reset button
			elif -4 <= clickx <= -2 and clicky == 0:
				sendData(c, {"RESET"})
				waitForTurn()

			#Undo button
			elif -4 <= clickx <= -2 and clicky == 2:
				if len(moveHistory) > 0:
					sendData(c, {"UNDO"})
					waitForTurn()
				else:
					clientlog.info("Nothing left to undo.")

			elif -4 <= clickx <= -2 and clicky == 4:
				sendData(c, {"QUIT"})
				mainMenu()

		gameBusy = False

##############
#Main Menu
##############
def mainMenu():
	turtleMove("home")
	t.clear()

	global currentScreen
	currentScreen = "mainMenu"
	global playerCount
	global width
	global height
	global AICount
	global winSeqLength
	global openMainMenu
	openMainMenu = False

	##############
	#Draw buttons
	##############

	#Join Game
	turtleMove(x-4, y)
	drawSquare(4, 1, "white")
	turtleMove(x+0.5, y)
	t.write("Join Game", False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Host Game
	turtleMove(x-4, y+2)
	drawSquare(4, 1, "white")
	turtleMove(x+0.5, y)
	t.write("Host Game", False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Spectator mode
	turtleMove(x-4, y+4)
	drawSquare(4, 1, "white")
	turtleMove(x+0.5, y)
	t.write("Join as Spectator", False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Play Singleplayer
	turtleMove(x-4, y+6)
	drawSquare(4, 1, "white")
	turtleMove(x+0.5, y)
	t.write("Play Singleplayer", False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Change Width
	turtleMove(x+4, y)
	drawSquare(5)
	turtleMove(x+0.5, y)
	t.write("Change Field Width", False, align="left", font=("Arial", 16, "normal"))
	turtleMove(x+5, y)
	t.write("Current width: "+str(width), False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Change Height
	turtleMove(x+4, y+2)
	drawSquare(5)
	turtleMove(x+0.5, y)
	t.write("Change Field Height", False, align="left", font=("Arial", 16, "normal"))
	turtleMove(x+5, y)
	t.write("Current height: "+str(height), False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Change playercount
	turtleMove(x+4, y+4)
	drawSquare(5)
	turtleMove(x+0.5, y)
	t.write("Change Player Count", False, align="left", font=("Arial", 16, "normal"))
	turtleMove(x+5, y)
	t.write("Current Player Count: "+str(playerCount), False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Change AICount
	turtleMove(x+4, y+6)
	drawSquare(5)
	turtleMove(x+0.5, y)
	t.write("Change AI Count", False, align="left", font=("Arial", 16, "normal"))
	turtleMove(x+5, y)
	t.write("Current AI Count: "+str(AICount), False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

	#Change winSeqLength
	turtleMove(x+4, y+8)
	drawSquare(5)
	turtleMove(x+0.5, y)
	t.write("Change Win Length", False, align="left", font=("Arial", 16, "normal"))
	turtleMove(x+5, y)
	t.write("Current Length: "+str(winSeqLength), False, align="left", font=("Arial", 16, "normal"))
	turtleMove("home")

################################################
###Server stuff
################################################
def server(gameMode2, width, height, playerCount, AICount, winSeqLength):
	global log
	log = logging.getLogger("SERVER")
	global clients
	global playerData
	global board
	global currentPlayer
	global gameMode
	global gameData
	gameMode = gameMode2
	clients = {}
	playerData = {}
	moveHistory = []

	log.info("Starting server!")

	#Bind socket
	try:
		s = socket.socket()
		s.bind((socket.gethostname(), 12345))
		s.listen(5)
	except OSError:
		log.critical("Failed to bind port. There may already be server process running.")
		exit()

	#Figure out how many connections we need
	allowedConnections = playerCount
	if gameMode == "singleplayer" or playerCount == AICount:
		allowedConnections = AICount+1

	log.info("Waiting for "+str(allowedConnections)+" connections.")

	#Start AI processes
	for i in range(1, AICount+1):
		id = "AI-"+str(i)
		AIProcess = Process(name = "Connect4"+id, target = setup, args = ("AI", id))
		AIProcess.start()

	#Wait for players to connect. Whenever a player connects, add them as player
	counter = 0
	connectedSpectators = 0
	playerData = {}
	while counter != allowedConnections:
		client, addr = s.accept()
		log.info("Connected to "+str(addr))
		playerType = receiveData(client)
		playerType = playerType["playerType"]

		if playerType == "spectator":
			log.info("Connected client identified as a spectator")
			connectedSpectators+=1
			if gameMode == "singleplayer" or playerCount == AICount:
				counter+=1
			id = [connectedSpectators+1000]
		elif playerType == "AI":
			log.info("Connected client identified as an AI")
			counter+=1
			id = [counter]
		elif playerType == "player":
			log.info("Connected client identified as a player")
			counter+=1
			if gameMode == "singleplayer":
				id = []
				for i in range(1, (playerCount-AICount)+1):
					val = len(playerData)
					id.append(val+i)
			else:
				id = [counter]

		for i in id:
			playerData[i] = {
				"type": playerType,
			}
			clients[i] = (client, addr)

		log.info("Sending ID")
		sendData(client, id) #Send player ID
		remaining = {"remaining": allowedConnections-counter}
		broadcastData(remaining)
		log.info("Registered player "+str(id)+". Waiting for "+str(remaining["remaining"])+" client(s).")
	
	log.info("All players have connected. Sending game data.")
	gameData = {
		"playerCount": playerCount,
		"AICount": AICount,
		"width": width,
		"height": height,
		"playerData": playerData,
		"winSeqLength": winSeqLength,
	}
	broadcastData(gameData)
	
	board = createBoardDict()

	log.info("Starting game.")
	currentPlayer = randint(1, playerCount)
	broadcastData({"START"})

	global gameActive
	gameActive = True
	while gameActive:
		log.info("The current player is "+str(currentPlayer))
		broadcastData(currentPlayer)

		command = receiveData(clients[currentPlayer][0])
		log.info("Received command: "+str(command))
		if command == {"QUIT"}:
			log.info("Shutting down.")
			broadcastData({"QUIT"})
			broadcastData(currentPlayer)
			gameActive = False

		elif command == {"UNDO"}:
			log.info("Received undo command.")
			if len(moveHistory) == 0:
				log.info("No move left to undo.")
				broadcastData({"UNDO"})
			else:
				undomove = moveHistory[len(moveHistory)-1]
				moveHistory.pop()
				
				freeCell = findFreeCell(undomove)
				if freeCell == -1:
					freeCell = height
				board[undomove][freeCell-1] = 0

				broadcastData({"UNDO"})
				currentPlayer-=1
				if currentPlayer == 0:
					currentPlayer = playerCount
				broadcastData(currentPlayer)

		elif command == {"RESET"}:
			log.info("Received reset command.")
			board = {}
			x = 0
			while x < width:
				board[x] = {}
				y = 0
				while y < height:
					board[x][y] = 0
					y+=1
				x+=1
			currentPlayer = randint(1, playerCount)
			broadcastData({"RESET"})
			broadcastData(currentPlayer)

		elif command == {"MOVE"}:
			lastMove = receiveData(clients[currentPlayer][0])
			log.info("Received a move.")
			moveHistory.append(lastMove)
			for cell in board[lastMove]:
				if board[lastMove][cell] == 0:
					freeCell = cell
					break
			board[lastMove][freeCell] = currentPlayer

			log.info("Player "+str(currentPlayer)+" placed a stone at "+str(lastMove))
			broadcastData({"MOVE"})
			broadcastData(lastMove)

			victory = victoryCheck(board, currentPlayer, lastMove, width, height, winSeqLength)
			log.info("Victory check returned "+str(victory)+" for this move.")
			broadcastData(victory)
			if victory == 1:
				log.info(str(currentPlayer)+" is victorious.")
				broadcastData(currentPlayer)
				gameActive = False
				break
			elif victory == 2:
				log.info("The game is a draw.")
				broadcastData("DRAW")
				gameActive = False
				break
			elif victory == 3:
				log.info("The game continues.")
				currentPlayer+=1
				if currentPlayer > playerCount:
					currentPlayer = 1

#Check for victory
def victoryCheck(board, player, move, width, height, winSeqLength):
	freeCell = findFreeCell(move)
	if freeCell != -1:
		freeCell-=1

		#Check vertical
		counter = 0
		i = freeCell
		while i > -1:
			if board[move][i] == player:
				counter+=1
				i-=1
			else:
				break
		if counter >= winSeqLength:
			return 1
		
		#Check horizontal
		counter = 0
		i = move
		while i < width:
			if board[i][freeCell] == player:
				counter+=1
				i+=1
			else:
				break
		i = move-1
		while i >= 0:
			if board[i][freeCell] == player:
				counter+=1
				i-=1
			else:
				break
		if counter >= winSeqLength:
			return 1

		#Check diagonal /
		counter = 0
		row = freeCell
		column = move
		while row < height-1 and column < width-1:
			if board[column][row] == player:
				counter+=1
				row+=1
				column+=1
			else:
				break
		row = freeCell-1
		column = move-1
		while row >= 0 and column >= 0:
			if board[column][row] == player:
				counter+=1
				row-=1
				column-=1
			else:
				break
		if counter >= winSeqLength:
			return 1

		#Check diagonal \
		counter = 0
		row = freeCell
		column = move
		while row >= 0 and row < height and column < width and column >= 0:
			if board[column][row] == player:
				counter+=1
				row+=1
				column-=1
			else:
				break
		row = freeCell-1
		column = move+1
		while row < height and column >= 0 and column < width and row >= 0:
			if board[column][row] == player:
				counter+=1
				row-=1
				column+=1
			else:
				break
			
		if counter >= winSeqLength:
			return 1

	draw = True
	for column in board:
		if board[column][height-1] == 0:
			draw = False
	if draw:
		return 2

	return 3

################################################
###Client stuff
################################################
def setup(playerType2, id=0, gameMode2="joingame"):
	global log
	global openMainMenu
	global gameData
	global playerCount
	global AICount
	global board
	global playerID
	global c
	c = socket.socket()
	global currentScreen
	currentScreen = "gameBoard"
	global playerType
	playerType = playerType2
	global gameMode
	if playerType == "AI":
		gameMode = gameMode2

	if playerType == "AI":
		log = logging.getLogger(id)
	else:
		log = logging.getLogger("CLIENT")
		t.clear()
		writeSubText("Connecting to server...", 0, 1)
	log.info("Starting setup!")

	if playerType == "AI" or gameMode == "singleplayer" or gameMode == "hostgame":
		#If a singleplayer game consists of only AI players; switch to spectator mode.
		if gameMode == "singleplayer" and playerCount == AICount:
			gameMode = "spectator"
			playerType = "spectator"

		address = socket.gethostname()
	else:
		validAddress = False
		while validAddress == False:
			address = promptString("Please enter an IP address")
			if address == "localhost" or address == "127.0.0.1":
				address = socket.gethostname()
				validAddress = True
			else:
				if verifyIPv4(address):
					validAddress = True
				else:
					log.error("Invalid IP address: "+str(address))
	log.info("Got "+address+" as address. Attempting to connect.")

	i = 0
	connected = False
	while i < 5:
		try:
			c.connect((address, 12345))
			connected = True
			break
		except Exception as error:
			log.error("Attempt failed: " + str(error))
			i+=1
	if not(connected):
		if playerType == "player":
			openMainMenu = True
			log.error("Failed to connect to server.")
			writeSubText("An error occured. Click anywhere to return to the main menu.", 0, 1)
		elif playerType == "AI":
			log.critical("Failed to connect to server. Cannot proceed.")
	else:
		log.info("Connected to "+address)
		sendData(c, {"playerType": playerType})
		playerID = receiveData(c)
		log.info("PlayerID is "+str(playerID))

		remaining = {"remaining": -1}
		log.info("Waiting for all players to join.")
		while remaining != {"remaining": 0}:
			remaining = receiveData(c)
			log.info("Players remaining: "+str(remaining["remaining"]))
			if playerType != "AI":
				writeSubText("Waiting for "+str(remaining["remaining"])+" player(s) to join...", 0, 1)
		
		log.info("Waiting for game data.")
		gameData = receiveData(c)

		log.info("Setting up board.")
		if playerType == "AI":
			board = createBoardDict()
		elif playerType == "spectator":
			board = createBoard(False)
		elif playerType == "player":
			board = createBoard(True)

		log.info("Setup complete")

		startSignal = receiveData(c)
		if startSignal == {"START"}:
			log.info("Starting game!")
			if not(nextTurn()):
				waitForTurn()
			elif playerType == "AI":
				AITurn()

def waitForTurn():
	global playerID
	global playerType
	global log
	global currentPlayer
	global moveHistory
	global board
	global openMainMenu
	global c

	log.info("Waiting for turn.")
	while True:
		command = receiveData(c)
		log.info("Received command: "+str(command))

		if command == {"QUIT"}:
			log.info("A player has left the game.")
			player = receiveData(c)
			if playerType != "AI":
				writeSubText("Player "+str(player)+" has left the game. Click anywhere to return to the main menu.", player, 1)
				openMainMenu = True
			break

		elif command == {"UNDO"}:
			if len(moveHistory) == 0:
				log.info("No move left to undo.")
			else:
				undomove = moveHistory[len(moveHistory)-1]
				moveHistory.pop()

				freeCell = findFreeCell(undomove)
				if freeCell == -1:
					freeCell = height
				board[undomove][freeCell-1] = 0
				fillCell(undomove, freeCell-1, 0)
				log.info("Undid move at "+str(undomove)+", "+str(freeCell-1))
				if nextTurn():
					if playerType == "AI":
						AITurn()
					else:
						break
			
		elif command == {"RESET"}:
			if playerType == "AI":
				board = createBoardDict()
			else:
				if playerType == "player":
					board = createBoard(True)
				else:
					board = createBoard(False)

			log.info("Game reset!")
			if nextTurn():
				if playerType == "AI":
					AITurn()
				else:
					break

		elif command == {"MOVE"}:
			lastMove = receiveData(c)
			clientlog.info("Server says last move was "+str(lastMove)+" by "+str(currentPlayer))
			if not(currentPlayer in playerID):
				if playerType == "AI":
					board[lastMove][findFreeCell(lastMove)] = currentPlayer
				else:
					placeStone(lastMove, currentPlayer)

			victory = receiveData(c)
			clientlog.info("Server says returned victory was "+str(victory))
			if victory == 1:
				winner = receiveData(c)
				log.info("The game ends in a victory for "+str(winner))
				win(winner)
				break

			elif victory == 2:
				log.info("The game is a draw.")
				win("DRAW")
				break

			elif victory == 3:
				log.info("The game continues.")
				if nextTurn():
					if playerType == "AI":
						AITurn()
					else:
						break
					
def nextTurn():
	global currentPlayer
	global c
	global playerID
	global playerType

	currentPlayer = receiveData(c)
	log.info("The game continues with player "+str(currentPlayer)+"'s turn.")
	if currentPlayer in playerID:
		log.info("This is our turn. Waiting for move...")
		if playerType != "AI":
			writeSubText("Make a move, player "+str(currentPlayer), currentPlayer, 1)
		return True
	else:
		if playerType != "AI":
			writeSubText("Waiting for player "+str(currentPlayer)+" to make a move.", currentPlayer, 1)
		return False

def win(player):
	global openMainMenu
	global playerType
	global log
	openMainMenu = True
	log.info("The game ends.")

	if playerType != "AI":
		if player == "DRAW":
			writeSubText("It's a draw! Click anywhere to return to the main menu.", 0, 2)
		else:
			writeSubText("Player "+str(player)+" wins! Click anywhere to return to the main menu.", player, 1)

###########################
#AI stuff
###########################
def AITurn():
	global board
	global currentPlayer
	global playerData
	global log
	global gameData
	height = gameData["height"]
	width = gameData["width"]
	winSeqLength = gameData["winSeqLength"]
	playerCount = gameData["playerCount"]

	#Find all possible moves
	possibleMoves = []
	for cell in board:
		if board[cell][height-1] == 0:
			possibleMoves.append(cell)
	log.info("Possible moves: "+str(possibleMoves))

	#No point in finding best move if there's only one option.
	if len(possibleMoves) > 2:
		#Find best move
		for move in possibleMoves:
			log.info("Checking move "+str(move))
			freeCell = findFreeCell(move)
			board[move][freeCell] = currentPlayer
			victory = victoryCheck(board, currentPlayer, move, width, height, winSeqLength)
			board[move][freeCell] = 0

			if victory == 1:
				#The move results in a victory for us. The other moves are irrelevant; just go with this one.
				log.info("Move "+str(move)+" results in a win.")
				possibleMoves = [move]
				break
			elif victory == 3:
				#The move does not result in a win or draw. Figure out if it causes a win for an opponent
				log.info("Move "+str(move)+" does not result in a win or draw.")
				for player in range(1, playerCount+1):
					if player == currentPlayer:
						continue #No point in doing this for current player
					log.info("Checking for player "+str(player))
					board[move][freeCell] = player
					victory = victoryCheck(board, player, move, width, height, winSeqLength)
					board[move][freeCell] = 0
					if victory == 1:
						#Move would result in a win for another player
						possibleMoves = [move]
						log.info("Move "+str(move)+" will prevent a win for player "+str(player))
						break
					elif victory == 3:
						#Move would not result in a win for another player
						log.info("Move "+str(move)+" will not prevent an opponent win.")
						if freeCell+1 < height: #If no stone can be placed above this tile, checking if its suicidal is useless (and would throw an error)
							result = 0
							for player in range(1, playerCount+1):
								if player == currentPlayer:
									continue #No point in doing this for current player
								board[move][freeCell] = currentPlayer
								board[move][freeCell+1] = player
								victory = victoryCheck(board, player, move, width, height, winSeqLength)
								board[move][freeCell+1] = 0
								board[move][freeCell] = 0
								result = victory
								if result == 1 or result == 2:
									break

							if result == 1:
								#Move is suicidal
								log.info("Move "+str(move)+" is suicidal. It will be avoided, if possible.")
								possibleMoves.remove(move)
							elif result == 3:
								#Move is not suicidal and won't end in a draw. It's a very mediocre move.
								log.info("Move "+str(move)+" is not suicidal and won't cause a draw.")
						else:
							log.info("Opponent can't place a stone above this.")
			if len(possibleMoves) == 1:
				break
	else:
		log.info("Only one possible move is available.")
					
	log.info("Resulting moveset is; "+str(possibleMoves))
	if len(possibleMoves) == 0:
		log.info("Could not find a good move. A random one will be selected.")
		possibleMoves = []
		for cell in board:
			if board[cell][height-1] == 0:
				possibleMoves.append(cell)
	chosenMove = possibleMoves[randint(0, len(possibleMoves)-1)]
	log.info("Decided to go with "+str(chosenMove))
	board[chosenMove][findFreeCell(chosenMove)] = currentPlayer
	sendData(c, {"MOVE"})
	sendData(c, chosenMove)
	log.info("End of turn.")

###########################
#Misc Functions
###########################
#Server only; broadcast data to clients
def broadcastData(data):
	global playerData
	list = []
	for player in playerData:
		client = clients[player]
		if client not in list:
			list.append(client)
	for client in list:
		sendData(client[0], data)

#Send data to socket
def sendData(socket, data):
	length = len(str(data))
	if 9999 > length > 0:
		result = str(length)
		append = 4-len(result)
		for i in range(0, append):
			i #This is here so that VSCode won't complain about an unused var. It doesn't actually have a use.
			result = "0"+result
		length = bytes(result, "utf-8")
	else:
		raise ValueError("Data must be at least 0 and no more than 9999 characters in size.")

	socket.send(length)
	socket.send(bytes(str(data), "utf-8"))

#Receive data from socket
def receiveData(socket):
	length = socket.recv(4).decode()
	length = int(length)
	if 9999 > length > 0:
		data = socket.recv(length).decode()
		data = eval(data)
		return(data)
	else:
		raise ValueError("Received data with invalid size: "+str(length))

#Place a stone for player in column, if possible. Returns true if successful, otherwise returns false.
#clickx		-	The column to place a stone in
def placeStone(clickx, player):
	global board
	global moveHistory
	global playerData
	global c

	freeCell = findFreeCell(clickx)
	if freeCell == -1:
		return False

	moveHistory.append(clickx)
	fillCell(clickx, freeCell, player)
	return True

#Fill a cell
def fillCell(cellx, celly, player):
	global playerColors
	board[cellx][celly] = player
	turtleMove(cellx, celly)
	drawSquare(1, 1, playerColors[player])
	turtleMove("home")

#Find bottommost empty cell in column
def findFreeCell(column):
	freeCell = -1
	for cell in board[column]:
		if board[column][cell] == 0:
			freeCell = cell
			break
	return freeCell

##############
#Prompt user for an int, then returns this int.
def promptInt(text, default, min, max):
	while True:
		value = ts.numinput("Enter a number.", text, default, min, max)
		if type(value) != type(None):
			return(int(value))

##############
#Prompt user for a string, then return this string.
def promptString(text):
	while True:
		value = ts.textinput("Enter a string.", text)
		if type(value) != type(None):
			return(value)

#Move turtle to X, Y
def turtleMove(newx, newy=""):
	global x
	global y
	
	t.pen(pendown = False)
	if newx == "home":
		x = 0
		y = 0
		newx = 0
		newy = 0
	x = newx
	y = newy
	t.goto((x*50)-450, (y*50)-200)
	t.pen(pendown = True)
	t.setheading(0)

#Write text below the board
def writeSubText(text, player, line):
	global playerData
	global playerColors

	height = -0.5 - line

	turtleMove("home")
	turtleMove(x, height)
	t.color("black", "white")
	t.begin_fill()
	turtleMove(x+18, y)
	turtleMove(x, y+1)
	turtleMove(x-18, y)
	turtleMove(x, y-1)
	t.end_fill()
	t.write(text, False, align="left", font=("Arial", 16, "normal"))

	turtleMove(x-2, y)

	if player < 9:
		color = playerColors[player]
	else:
		color = playerColors[0]

	drawSquare(1, 1, color)

	turtleMove("home")

#Draw a square starting the turtle's current location.
def drawSquare(x=1, y=1, color="white"):
	t.color("black", color)
	t.begin_fill()
	t.forward(50*x)
	t.left(90)
	t.forward(50*y)
	t.left(90)
	t.forward(50*x)
	t.left(90)
	t.forward(50*y)
	t.left(90)
	t.end_fill()

#Draw a board, and create a dict for it
def createBoard(showButtons):
	global gameData
	global playerID
	t.clear()

	#Draw horinzontal lines
	global x
	global y
	x = 0
	y = 0

	width = gameData["width"]
	height = gameData["height"]

	i = 0
	while i < height+1:
		i+=1
		t.forward(50*width)
		turtleMove(0, i)
	turtleMove("home")

	#Draw vertical lines
	i = 0
	while i < width+1:
		i+=1
		t.left(90)
		t.forward(50*height)
		turtleMove(i, 0)
	turtleMove("home")

	if playerType == "player" and gameMode != "singleplayer":
		writeSubText("You are player "+str(playerID[0]), playerID[0], 2.5)

	board = createBoardDict()

	if showButtons:
		#Draw buttons
		#Reset
		turtleMove(x-4, y)
		drawSquare(3, 1, "white")
		turtleMove(x+3, y)
		t.write("Reset Game", False, align="right", font=("Arial", 16, "normal"))
		turtleMove("home")

		#Undo
		turtleMove(x-4, y+2)
		drawSquare(3, 1, "white")
		turtleMove(x+3, y)
		t.write("Undo", False, align="right", font=("Arial", 16, "normal"))
		turtleMove("home")

		#Quit
		turtleMove(x-4, y+4)
		drawSquare(3, 1, "white")
		turtleMove(x+3, y)
		t.write("Quit", False, align="right", font=("Arial", 16, "normal"))
		turtleMove("home")
	return board

#Create a new board dict
def createBoardDict():
	global gameData
	board = {}
	x = 0

	width = gameData["width"]
	height = gameData["height"]
	while x < width:
		board[x] = {}
		y = 0
		while y < height:
			board[x][y] = 0
			y+=1
		x+=1
	return board

#Check if an IP address is valid
def verifyIPv4(address):
	address = address.split(":")
	address = address[0]
	address = address.split(".")
	
	if len(address) != 4:
		return False
	for octet in address:
		try:
			if not(256 > int(octet) > -1):
				return False
		except:
			return False
	return True

if __name__ == '__main__':
	mainMenu()
	ts.onscreenclick(main,1)
	ts.mainloop()

#By Niels van de Kerkhof
#0961007@hr.nl