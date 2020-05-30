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
    tiroValido = False    
    Player_ID = server['player_turn_id']
    actualBoard = server['board']

    validating_point_method(actualBoard, Player_ID)

    #Para random playing
    while (tiroValido == False):
        #Para que escoja si es vertical u horizontal con 0 o 1
        tdl = np.random.randint(0,2)
        #Para que escoja la linea disponible a jugar
        ndl = np.random.randint(0,30)
        if(actualBoard[tdl][ndl]==99):
            tiroValido = True
        else:
            tiroValido = False
        
    for filas in actualBoard:
        for value in filas:
            if Player_ID == 1:
                #Un minimax donde se busque el mayor valor
                if (value>0):
                    infoGame.points += 1
                #print("As player 1 positive points: " + str(infoGame.points))                   
                pass
            else:
                if (value<0):
                    infoGame.points += 1
                #print("As player 2 negative points: " + str(infoGame.points))
                #un minimax donde se busque el menor valor
                pass

    sio.emit('play',{
        'player_turn_id':Player_ID,
        'tournament_id': infoGame.tournament_id,
        'game_id': server['game_id'],
        'movement': (tdl, ndl)
    })

def reset():
    row = np.ones(30) * 99
    infoGame.board = [np.ndarray.tolist(row), np.ndarray.tolist(row)]

@sio.on('finish')
def finish(server):
    reset()
    Player_ID = server['player_turn_id']
    board = server['board']

    draw_board(board)

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
    if (playerID == 1):
        print("Punteo Jugador 1: ", player1)
    if (playerID == 2):
        print("Punteo Jugador 2: ", player2)


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

def poda_Alpha_Beta():
    print("holi")

def minimax(position, depth, maximizingPlayer):
    print("Holi minimax")


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
#def miniMax(State, Ply_num): # Function for the minimax algorithm
#
#        for i in range(State.Current.dimY):
#            for j in range(State.Current.dimX):
#                if State.Current.Mat[i][j] == ' ' and (j, i) not in State.children:
#                    State.Make(j, i, True)
#                    if Ply_num < 2:
#                        return (i, j)
#
#        Minimum_Score = 1000
#        i = 0
#        j = 0
#        for k, z in State.children.items():
#            Result = Max(z, Ply_num - 1, Minimum_Score)
#            if Minimum_Score > Result:
#                Minimum_Score = Result
#                i = k[0]
#                j = k[1]
#
#        return (i, j)

infoGame = infoGame()
infoGame.username = input("User: \n")
infoGame.tournament_id = input("Tournament ID: \n")
host = input("Host address: \n")
sio.connect(host)