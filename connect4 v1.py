import turtle
from random import randint

#Create turtle
t = turtle.Turtle()
t.speed(0)
t.hideturtle()

#Create screen?
ts = turtle.Screen()
ts.title("Connect Four!")
ts.tracer(0, 0)

#Create global vars
gameActive = False
gameBusy = False
moveHistory = []

#Main function
def main(clickx, clicky):
	global gameActive
	global gameBusy
	global board
	global width
	global height

	if gameBusy == False:
		gameBusy = True
		#Convert clickx and clicky to the better coordinate system
		clickx = int((clickx//50)+9)
		clicky = int((clicky//50)+4)

		#Run setup if it hasn't been ran already
		if gameActive == False:
			setup()
			nextPlayer()
			gameActive = True
			turn()
		else:
			#Board click
			if 0 <= clickx <= width-1 and 0 <= clicky <= height-1:
				turn(clickx)
			
			#Reset button
			elif -4 <= clickx <= -2 and clicky == 0:
				gameActive = False
				main(clickx, clicky)

			#Undo button
			elif -4 <= clickx <= -2 and clicky == 3:
				if len(moveHistory) > 0:
					undo()

		gameBusy = False

	
#Setup
def setup():
	t.clear()

	#Get user input
	global width
	width = promptInt("Please enter the width of the field.", 7, 7, 18)
	global height
	height = promptInt("Please enter the height of the field.", 6, 6, 10)
	global players 
	players = promptInt("How many players?", 2, 2, 8)
	global AICount
	AICount = promptInt("How many AI?", 0, 0, players)
	global winSeqLength
	winSeqLength = promptInt("How long should the winning sequence be?", 4, 2, min([width, height]))

	global playerData
	playerData = {}
	for player in range(players):
		if player >= players-AICount:
			playerType = "AI"
		else:
			playerType = "Player"
		playerColors = ["White", "Red", "Blue", "chartreuse2", "Yellow", "Aqua", "Orange", "Gray", "Lightpink"]
		playerData[player+1] = {
			"color": playerColors[player+1],
			"type": playerType
		}
	global x
	global y
	x = 0
	y = 0

	#Draw horinzontal lines
	i = 0
	while i < height+1:
		i+=1
		t.forward(50*width)
		move(0, i)
	move("home")

	#Draw vertical lines
	i = 0
	while i < width+1:
		i+=1
		t.left(90)
		t.forward(50*height)
		move(i, 0)
	move("home")

	#Create board dict
	global board
	board = {}
	
	while x < width:
		board[x] = {}
		y = 0
		while y < height:
			board[x][y] = 0
			y+=1
		x+=1
	move("home")

	#Draw buttons
	#Reset
	move(x-4, y)
	drawSquare(3)
	move(x+3, y)
	t.write("Reset Game", False, align="right", font=("Arial", 16, "normal"))
	move("home")

	#Undo
	move(x-4, y+3)
	drawSquare(3)
	move(x+3, y)
	t.write("Undo", False, align="right", font=("Arial", 16, "normal"))
	move("home")

	global currentPlayer
	currentPlayer = randint(1, players)
	
#Go to next turn
def turn(clickx=-1):
	global currentPlayer
	global playerData
	global gameActive

	while playerData[currentPlayer]["type"] == "AI" and gameActive:
		AITurn()
		if gameActive:
			nextPlayer()
	if playerData[currentPlayer]["type"] == "Player" and clickx != -1:
		if placeStone(clickx):
			nextPlayer()
			turn(-1)

#Increment currentPlayer and subtext
def nextPlayer():
	global currentPlayer
	currentPlayer+=1
	if currentPlayer > players:
		currentPlayer = 1
	writeSubText("Player "+str(currentPlayer)+"'s turn!", True)

#The AI does its thing
def AITurn():
	global board
	global currentPlayer
	global height
	global players

	#Find all possible moves
	possibleMoves = []
	for cell in board:
		if board[cell][height-1] == 0:
			possibleMoves.append(cell)
	print(currentPlayer, ":", "Possible moves are;", possibleMoves)

	#No point in finding best move if there's only one option.
	if len(possibleMoves) > 2:
		#Find best move
		for move in possibleMoves:
			freeCell = -1
			for cell in board[move]:
				if board[move][cell] == 0:
					freeCell = cell
					break
			board[move][freeCell] = currentPlayer
			victory = victoryCheck(move, freeCell, currentPlayer)
			board[move][freeCell] = 0

			if victory == 1:
				#The move results in a victory for us. The other moves are irrelevant; just go with this one.
				print(currentPlayer, ":", move, "is a win!")
				possibleMoves = [move]
				break
			elif victory == 2:
				#The move does not result in a win or draw. Figure out if it causes a win for an opponent
				print(currentPlayer, ":", move, "is not a win or draw!")
				for player in range(1, players+1):
					if player == currentPlayer:
						continue #No point in doing this for current player
					print(currentPlayer, ":", "Checking for player", player)
					board[move][freeCell] = player
					victory = victoryCheck(move, freeCell, player)
					board[move][freeCell] = 0
					if victory == 1:
						#Move would result in a win for another player
						possibleMoves = [move]
						print(currentPlayer, ":", move, "will prevent", player, "'s win!")
						break
					elif victory == 2:
						#Move would not result in a win for another player
						print(currentPlayer, ":", move, "will not prevent an opponent win.")
						if freeCell+1 < height: #If no stone can be placed above this tile, checking if its suicidal is useless (and would throw an error)
							result = 0
							for player in range(1, players+1):
								if player == currentPlayer:
									continue #No point in doing this for current player
								board[move][freeCell] = currentPlayer
								board[move][freeCell+1] = player
								victory = victoryCheck(move, freeCell, player)
								board[move][freeCell+1] = 0
								board[move][freeCell] = 0
								result = victory
								if result == 1 or result == 2:
									break

							if result == 1:
								#Move is suicidal
								print(currentPlayer, ":", move, "is suicidal!")
								possibleMoves.remove(move)
							elif result == 2:
								#Move is not suicidal and won't end in a draw. It's a very mediocre move.
								print(currentPlayer, ":", move, "is not suicidal and is not a draw!")
						else:
							print(currentPlayer, ":", "Opponent can't place stone above this!")
			if len(possibleMoves) == 1:
				break
	else:
		print(currentPlayer, ":", "There's only one option!")
					
	print(currentPlayer, ":", "Resulting moveset is", possibleMoves)
	if len(possibleMoves) == 0:
		print(currentPlayer, ":", "Couldn't find a good move!")
		possibleMoves = []
		for cell in board:
			if board[cell][height-1] == 0:
				possibleMoves.append(cell)
	chosenmove = possibleMoves[randint(0, len(possibleMoves)-1)]
	print(currentPlayer, ":", "Decided to go with", chosenmove)
	placeStone(chosenmove)
	print(currentPlayer, ":", "End of turn")
	print("---------------------")

#Undo last move
def undo():
	global board
	global currentPlayer
	global moveHistory
	global playerData

	lastmove = moveHistory[len(moveHistory)-1]
	moveHistory.pop()

	board[lastmove[0]][lastmove[1]] = 0
	move(lastmove[0], lastmove[1])
	drawSquare(1, 1, "white")
	move("home")

	currentPlayer-=1
	if currentPlayer == 0:
		currentPlayer = players
	writeSubText("Player "+str(currentPlayer)+"'s turn!", True)

	if playerData[currentPlayer]["type"] == "AI":
		turn()

#Place a stone in column, if possible. Returns true if successful, otherwise returns false.
#clickx		-	The column to place a stone in
def placeStone(clickx):
	global board
	global currentPlayer
	global moveHistory

	freeCell = -1
	for cell in board[clickx]:
		if board[clickx][cell] == 0:
			freeCell = cell
			break
	if freeCell == -1:
		return False
	
	board[clickx][freeCell] = currentPlayer
	move(clickx, freeCell)
	drawSquare(1, 1, playerData[currentPlayer]["color"])
	move("home")
	
	moveHistory.append((clickx, freeCell))

	victory = victoryCheck(clickx, freeCell, currentPlayer)
	if victory == 1:
		win(currentPlayer)
		return False
	elif victory == 3:
		win("DRAW")
		return False

	return True

#Check if the last move resulted in a victory for someone.
#Returns;
#1	-	Victory
#2	-	No victory
#3	-	Draw
def victoryCheck(clickx, clicky, player):
	global height
	global width
	global board
	global winSeqLength

	#Check vertical
	counter = 0
	i = clicky
	while i > -1:
		if board[clickx][i] == player:
			counter+=1
			i-=1
		else:
			break
	if counter >= winSeqLength:
		return 1
	
	#Check horizontal
	counter = 0
	i = clickx
	while i < width:
		if board[i][clicky] == player:
			counter+=1
			i+=1
		else:
			break
	i = clickx-1
	while i >= 0:
		if board[i][clicky] == player:
			counter+=1
			i-=1
		else:
			break
	if counter >= winSeqLength:
		return 1

	#Check diagonal /
	counter = 0
	row = clicky
	column = clickx
	while row < height-1 and column < width-1:
		if board[column][row] == player:
			counter+=1
			row+=1
			column+=1
		else:
			break
	row = clicky-1
	column = clickx-1
	while row >= 0 and column >= 0:
		if board[column][row] == player:
			counter+=1
			row-=1
			column-=1
		else:
			break
	if counter >= winSeqLength:
		return True

	#Check diagonal \
	counter = 0
	row = clicky
	column = clickx
	while row >= 0 and row < height and column < width and column >= 0:
		if board[column][row] == player:
			counter+=1
			row+=1
			column-=1
		else:
			break
	row = clicky-1
	column = clickx+1
	while row < height and column >= 0 and column < width and row >= 0:
		if board[column][row] == player:
			counter+=1
			row-=1
			column+=1
		else:
			break
		
	if counter >= winSeqLength:
		return True

	draw = True
	for column in board:
		if board[column][height-1] == 0:
			draw = False
	if draw:
		return 3

	return 2

#Show win message for `player`, or show a draw message
def win(player):
	global gameActive
	if player == "DRAW":
		writeSubText("It's a draw! Click anywhere to restart.", False)
	else:
		writeSubText("Player "+str(player)+" wins! Click anywhere to restart.", True)
	gameActive = False

#Prompt user for an int, then returns this int.
#text	   -   The message that will be shown
#default	-   Default value
#min		-   Min value
#max		-   Max value
def promptInt(text, default, min, max):
	while True:
		value = ts.numinput("Enter a number.", text, default, min, max)
		if type(value) != type(None):
			value = int(value)
			return(int(value))

#Move turtle to X, Y
def move(newx, newy=""):
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
def writeSubText(text, showCurrentPlayer):
	global playerData
	global currentPlayer

	move("home")
	move(x, y-1.5)
	t.color("black", "white")
	t.begin_fill()
	move(x+18, y)
	move(x, y+1)
	move(x-18, y)
	move(x, y-1)
	t.end_fill()
	t.write(text, False, align="left", font=("Arial", 16, "normal"))

	if showCurrentPlayer:
		move(x-2, y)
		drawSquare(1, 1, playerData[currentPlayer]["color"])

	move("home")

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

move("home")
writeSubText("Click anywhere to get started", False)
ts.onscreenclick(main,1)
ts.mainloop()

#By Niels van de Kerkhof
#0961007@hr.nl