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


def poda_Alpha_Beta():
    print("holi")

def minimax(position, depth, maximizingPlayer):
    print("Holi minimax")

infoGame = infoGame()
infoGame.username = input("User: \n")
infoGame.tournament_id = input("Tournament ID: \n")
host = input("Host address: \n")
sio.connect(host)