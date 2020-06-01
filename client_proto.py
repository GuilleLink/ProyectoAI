#Universidad del Valle de Guatemala
#Juan Guillermo Sandoval Lacayo - 17577
#Inteligencia Artificial
#Proyecto

import socketio
import numpy as np

sio = socketio.Client()

class infoGame:
    def __init__(self):
        self.username = ""
        self.tournament_id = ""
        self.game_id = ""
        self.board = []
        self.fboard = []
        self.points = 0
        self.gamesPlayed = 0
        self.maxDepth = 2
        #self.boardM = np.matrix()

@sio.on('connect')
def onConnect():
    print("Connected")
    sio.emit('signin',{
        'user_name': infoGame.username,
        'tournament_id': infoGame.tournament_id,
        'user_role': 'player'
    })

@sio.event
def conn_error():
    print("Connection failed")

@sio.event
def disconnect():
    print("Disconnected")

@sio.on('ready')
def ready(server): 
    Player_ID = server['player_turn_id']
    actualBoard = server['board']

    #Throw minimax so the best play can be found
    #Sending the board I get from the server
    #Sending the depth and since it is "starting" maximizing is True
    #Sending the player ID for a multiplying factor
    bestScore, bestMove = checkBestMove(actualBoard, Player_ID)

    print("El mejor tiro es: ", bestMove)
    print("Puntos realizados en este tiro = ", bestScore)    
    

    sio.emit('play',{
        'player_turn_id':Player_ID,
        'tournament_id': infoGame.tournament_id,
        'game_id': server['game_id'],
        #'movement': (tdl, ndl)
        'movement': (bestMove)
    })

def reset():
    row = np.ones(30) * 99
    infoGame.board = [np.ndarray.tolist(row), np.ndarray.tolist(row)]

def checkWinner(server):
    if Player_ID == server['winner_turn_id']:
        return 1
    else:
        return -1

@sio.on('finish')
def finish(server):
    reset()
    Player_ID = server['player_turn_id']
    board = server['board']

    

    if Player_ID == server['winner_turn_id']:
        print("Eres el ganador")
    else:
        print("Perdiste")

    infoGame.gamesPlayed += 1
    infoGame.points = 0

    print("Juegos jugados: " + str(infoGame.gamesPlayed))

    sio.emit('player_ready',{
        'tournament_id': infoGame.tournament_id,
        'game_id': server['game_id'],
        'player_turn_id': Player_ID
    })

def validating_point_method(board, playerID):
    N=6
    EMPTY = 99
    acumulador = 0
    contador = 0
    contadorPuntos = 0

    for i in range(len(board[0])):
        if ((i + 1) % N) != 0:
            if board[0][i] != EMPTY and board[0][i + 1] != EMPTY and board[1][contador + acumulador] != EMPTY and board[1][contador + acumulador + 1] != EMPTY:
                contadorPuntos = contadorPuntos + 1
            acumulador = acumulador + N
        else:
            contador = contador + 1
            acumulador = 0

    player1 = 0
    player2 = 0
    FILLEDP11 = 1
    FILLEDP12 = 2
    FILLEDP21 = -1
    FILLEDP22 = -2

    for i in range(len(board[0])):
        if board[0][i] == FILLEDP12:
            player1 = player1 + 2
        elif board[0][i] == FILLEDP11:
            player1 = player1 + 1
        elif board[0][i] == FILLEDP22:
            player2 = player2 + 2
        elif board[0][i] == FILLEDP21:
            player2 = player2 + 1

    for j in range(len(board[1])):
        if board[1][j] == FILLEDP12:
            player1 = player1 + 2
        elif board[1][j] == FILLEDP11:
            player1 = player1 + 1
        elif board[1][j] == FILLEDP22:
            player2 = player2 + 2
        elif board[1][j] == FILLEDP21:
            player2 = player2 + 1

    ## Aqui imprimimos los punteos de cada jugador
    #if (playerID == 1):
    #    print("Punteo Jugador 1: ", player1, "    ", contadorPuntos)
    #if (playerID == 2):
    #    print("Punteo Jugador 2: ", player2, "    ", contadorPuntos)    
    return contadorPuntos


def draw_board(board):
    standard_board = [
        ['.', '.', '.', '.', '.', '.'],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['.', '.', '.', '.', '.', '.'],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['.', '.', '.', '.', '.', '.'],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['.', '.', '.', '.', '.', '.'],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['.', '.', '.', '.', '.', '.'],
        [' ', ' ', ' ', ' ', ' ', ' '],
        ['.', '.', '.', '.', '.', '.'],
    ]

    for i in range(0,len(board)):
        if (i==0): 
            acumulador = 0   
            start = 0
            end = len(board[i])      
            N = 6
            for j in board[i]:
                if (j != 99):
                    if (((board[i].index(j, start, end)) % N) == 0) & (board[i].index(j, start, end) != 0):
                        acumulador +=1
                    try:
                        standard_board[acumulador*2][(board[i].index(j, start, end)) % N] = '._'
                    except:
                        pass                    
                start += 1
        if (i==1):
            acumulador = 0   
            start = 0
            end = len(board[i])      
            N = 6
            for j in board[i]:
                if (j != 99):
                    if (((board[i].index(j, start, end)) % N) == 0) & (board[i].index(j, start, end) != 0):
                        acumulador +=1
                    try:
                        standard_board[(acumulador*2)+1][(board[i].index(j, start, end) +1) % N] = '|'
                    except:
                        pass
                start += 1
    print(standard_board)
        


def checkBestMove(board, Player_ID):
    bestScore = -1000
    alpha = -1000
    beta = 1000
    for typeOfLine in range(len(board)):      
        #line is the actual value of the line  
        for line in range(len(board[typeOfLine])):
            #If its available
            if (board[typeOfLine][line] == 99):
                board[typeOfLine][line] = 0
                #Call to fun minimax
                score = minimax(board, 0, True, Player_ID, alpha, beta)
                board[typeOfLine][line] = 99                                    
                if(score >= bestScore):
                    bestScore = score
                    bestMove = (typeOfLine, line)
    return bestScore, bestMove




def minimax(board, depth, maximizingPlayer, Player_ID, alpha, beta):
    if (depth >= infoGame.maxDepth):
        return board
    #New board to check results
    Changedboard = board
    isScoring = False

    if (Player_ID == 1):
        multiplyingFactor = 1
    elif (Player_ID == 2):
        #If player No. 2 as the values are negative
        #We multiply -1 so negatives becomes positive for minimax
        #and positives become negatives
        multiplyingFactor = -1

    if (maximizingPlayer):
        bestScore = -1000
        #Checking every element of the board
        for typeOfLine in range(len(Changedboard)):      
            #line is the actual value of the line  
            for line in range(len(Changedboard[typeOfLine])):
                if (Changedboard[typeOfLine][line] == 99):
                    pointsBefore = validating_point_method(Changedboard, Player_ID)
                    Changedboard[typeOfLine][line] = 0
                    pointsAfter = validating_point_method(Changedboard, Player_ID)                    
                    score = (pointsAfter-pointsBefore) * multiplyingFactor
                    if (score > 0 & score < 10):
                        minimax(Changedboard, depth + 1, True, Player_ID, alpha, beta)   
                    else:
                        minimax(Changedboard, depth + 1, False, Player_ID, alpha, beta)                              
                    Changedboard[typeOfLine][line] = 99                    
                    bestScore = max(score, bestScore)
                    alpha = max(alpha, score)
                    if (beta <= alpha):
                        break
        return bestScore
                    
    elif (maximizingPlayer != True):
        bestScore = 1000
        #Checking every element of the board
        for typeOfLine in range(len(Changedboard)):      
            #line is the actual value of the line  
            for line in range(len(Changedboard[typeOfLine])):
                if (Changedboard[typeOfLine][line] == 99):
                    pointsBefore = validating_point_method(Changedboard, Player_ID)
                    Changedboard[typeOfLine][line] = 0
                    pointsAfter = validating_point_method(Changedboard, Player_ID)                    
                    minimax(Changedboard, depth + 1, True, Player_ID, alpha, beta)
                    score = (pointsAfter-pointsBefore) * multiplyingFactor                    
                    Changedboard[typeOfLine][line] = 99
                    bestScore = min(score, bestScore)
                    beta = min(beta, score)
                    if (beta <= alpha):
                        break
        return bestScore
































    #Starting with depth 0 at first iteration, if the depth of the tree
    #reaches or surpasses this depth then it should return the best play
    #or best move posible
    #actualDepth = 0
    #bestMove = board
    #if (actualDepth >= depth):
    #    print("Depth = ", actualDepth)
    #    print(bestMove)
    #    return bestMove
#
    #if (Player_ID == 1):
    #    multiplyingFactor = 1
    #elif (Player_ID == 2):
    #    #If player No. 2 as the values are negative
    #    #We multiply -1 so negatives becomes positive for minimax
    #    #and positives become negatives
    #    multiplyingFactor = -1
#
    ##Si es Max hace Max, sino hace Min
    #if (maximizingPlayer):
    #    Maximize(bestMove, depth + 1, False)
#
    ##elif (maximizingPlayer == False):
#
#
    #pointsBefore = validating_point_method(board, Player_ID)
    #difPoint = (validating_point_method(board, Player_ID) - pointsBefore)
    ##Cierro un cuadro, o dos o el oponente cierra uno o dos
    ##Posibilidad de agregar un score de +5 dependiendo cuantos turnos extra de o -5 dependiendo cuantos obtenga el rival
    ##Con SM 13 V
    ##If scoring you get another turn so you play again
    ##Also check fot all the points you acumulate
    #scoring = False
    #acumulativePoints = 0
    #acumulativeTurns = 0
    #possibleScores = [1, 2, -1, -2, 0]
    #if (maximizingPlayer):
    #    maxScore = -10000
    #    #for


#def Maximum(State, Ply_num, Alpha): # Alpha-beta pruning function for taking care of Alpha values
#        if Ply_num == 0:
#            return State.CurrentScore
#
#        for i in range(State.Current.dimY):
#            for j in range(State.Current.dimX):
#                if State.Current.Mat[i][j] == ' ' and (j, i) not in State.children:
#                    State.Make(j, i, False)
#
#        Maximum_Score = -1000
#        i = 0
#        j = 0
#        for k, z in State.children.items():
#            Result = Algo.Minimum(z, Ply_num - 1, Maximum_Score)
#            if Maximum_Score < Result:
#                Maximum_Score = Result
#            if Result > Alpha:
#                return Result
#
#        return Maximum_Score
#
#
#    def Minimum(State, Ply_num, Beta): # Alpha-beta pruning function for taking care of Beta values
#        if Ply_num == 0:
#            return State.CurrentScore
#
#        for i in range(State.Current.dimY):
#            for j in range(State.Current.dimX):
#                if State.Current.Mat[i][j] == ' ' and (j, i) not in State.children:
#                    State.Make(j, i, True)
#
#        Minimum_Score = 1000
#        i = 0
#        j = 0
#        for k, z in State.children.items():
#            Result = Algo.Maximum(z, Ply_num - 1, Minimum_Score)
#            if Minimum_Score > Result:
#                Minimum_Score = Result
#            if Result < Beta:
#                return Result
#
#        return Minimum_Score
#
#

infoGame = infoGame()
infoGame.username = input("User: \n")
infoGame.tournament_id = input("Tournament ID: \n")
host = input("Host address: \n")
sio.connect(host)