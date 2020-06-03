#Universidad del Valle de Guatemala
#Juan Guillermo Sandoval Lacayo - 17577
#Inteligencia Artificial
#Proyecto

import socketio
import numpy as np
import time

sio = socketio.Client()

class infoGame:
    def __init__(self):
        self.username = ""
        self.tournament_id = ""
        self.game_id = ""
        self.points = 0
        self.gamesPlayed = 0
        self.maxDepth = 1

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

@sio.on('finish')
def finish(server):
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

@sio.on('ready')
def ready(server): 
    Player_ID = server['player_turn_id']
    actualBoard = server['board']

    #Throw minimax so the best play can be found
    #Sending the board I get from the server
    #Sending the depth and since it is "starting" maximizing is True
    #Sending the player ID for a multiplying factor
    startTime = time.time()

    bestMove = checkBestMove(actualBoard, Player_ID)

    actualBoard[bestMove[0]][bestMove[1]] = 0
    #nB = draw_board2(actualBoard)
    #print(nB)
    print("El mejor tiro es: ", bestMove)
    print("Tiempo para tirar: %s" % (time.time() - startTime))
    

    sio.emit('play',{
        'player_turn_id':Player_ID,
        'tournament_id': infoGame.tournament_id,
        'game_id': server['game_id'],
        'movement': (bestMove)
    })

def checkBestMove(playingBoard, playerID):
    bestScore = -1000
    tiedMoves = []
    for horVer in range(len(playingBoard)):
        for line in range(len(playingBoard[horVer])):
            if playingBoard[horVer][line] == 99:
                _, VerifySpotScore = tryMove(playingBoard, (horVer, line), playerID, True)
                playingBoard[horVer][line] = 99
                if (VerifySpotScore > 0):
                    score = minimax(playingBoard, (horVer, line), 0, True, playerID, -1000, 1000, VerifySpotScore, VerifySpotScore)
                else:
                    score = minimax(playingBoard, (horVer, line), 0, False, playerID, -1000, 1000, VerifySpotScore, VerifySpotScore)
                if (score > bestScore):
                    bestScore = score
                    tiedMoves.clear()
                if (score >= bestScore):
                    tiedMoves.append((horVer,line))
    
    return tiedMoves[np.random.randint(len(tiedMoves))]



def minimax(board, move, depth, isMaximizing, playerID, alpha, beta, pointsOnTurn, acumulativePoints):

    idPlayerPlaying = playerID if isMaximizing else (playerID % 2) + 1
    if(playerID == idPlayerPlaying):
        IPlay = True
    else:
        IPlay = False

    if playerID == 1:
        multiplyingFactor = 1
    else:
        multiplyingFactor = -1

    if (depth == infoGame.maxDepth or 99 not in np.asarray(board).reshape(-1)):
        scoreOnBoardPlay = pointsOnTurn + acumulativePoints
        if (scoreOnBoardPlay > 0):
            print("I SCORED:" , scoreOnBoardPlay)
        if (scoreOnBoardPlay < 0):
            print("YOU SCORED:" , scoreOnBoardPlay)
        return scoreOnBoardPlay

    board, _ = tryMove(board, (move[0], move[1]), idPlayerPlaying, IPlay)
    if (isMaximizing):
        bestScore = -1000
        for horVer in range(len(board)):
            for line in range(len(board[horVer])):
                if board[horVer][line] == 99:
                    _, VerifySpotScore = tryMove(board, (horVer, line), idPlayerPlaying, IPlay)                                        
                    if (VerifySpotScore>0):                
                        #print("PREVIOUS MOVE:  ", move,"  NOW I MOVE:   ", (horVer, line), "  I  SCORE   ", VerifySpotScore) 
                        score = minimax(board, (horVer, line), depth + 1, True, idPlayerPlaying, alpha, beta, VerifySpotScore, acumulativePoints+VerifySpotScore)
                    else:                       
                        score = minimax(board, (horVer, line), depth + 1, False, idPlayerPlaying, alpha, beta, VerifySpotScore, acumulativePoints+VerifySpotScore)
                    bestScore = max(score, bestScore)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break

        return bestScore

    if (not isMaximizing):
        bestScore = 1000
        for horVer in range(len(board)):
            for line in range(len(board[horVer])):
                if board[horVer][line] == 99:
                    _, VerifySpotScore = tryMove(board, (horVer, line), idPlayerPlaying, IPlay)
                    VerifySpotScore = VerifySpotScore
                    if (VerifySpotScore>0):
                        #print("I MOVED", move, "YOU SCORED", VerifySpotScore)                        
                        score = minimax(board, (horVer, line), depth + 1, False, idPlayerPlaying, alpha, beta, VerifySpotScore, acumulativePoints-VerifySpotScore)
                    else:
                        score = minimax(board, (horVer, line), depth + 1, True, idPlayerPlaying, alpha, beta, VerifySpotScore, acumulativePoints+VerifySpotScore)
                    bestScore = min(score, bestScore)
                    beta = min(beta, score)
                    if beta <= alpha:
                        break

        return bestScore

def tryMove(board, move, playerID, playerPoints):
    N=6
    EMPTY = 99
    acumulador = 0
    contador = 0
    
    pointBeforeMove = 0
    pointMoved = 0

    player1 = 0
    player2 = 0

    FILLEDP11 = 1
    FILLEDP12 = 2
    FILLEDP21 = -1
    FILLEDP22 = -2

    newBoard = list(map(list, board))

    for i in range(len(board[0])):
        if ((i + 1) % N) != 0:
            if board[0][i] != EMPTY and board[0][i + 1] != EMPTY and board[1][contador + acumulador] != EMPTY and board[1][contador + acumulador + 1] != EMPTY:
                pointBeforeMove = pointBeforeMove + 1
            acumulador = acumulador + N
        else:
            contador = contador + 1
            acumulador = 0    

    acumulador = 0
    contador = 0
    newBoard[move[0]][move[1]] = 0

    for i in range(len(newBoard[0])):
        if ((i + 1) % N) != 0:
            if newBoard[0][i] != EMPTY and newBoard[0][i + 1] != EMPTY and newBoard[1][contador + acumulador] != EMPTY and newBoard[1][contador + acumulador + 1] != EMPTY:
                pointMoved = pointMoved + 1
            acumulador = acumulador + N
        else:
            contador = contador + 1
            acumulador = 0  

    if  pointMoved > pointBeforeMove:
        if playerID == 1:
            if (pointMoved - pointBeforeMove) == 2:
                board[move[0]][move[1]] = FILLEDP12
                player1 = player1 + 2
            elif (pointMoved - pointBeforeMove) == 1:
                board[move[0]][move[1]] = FILLEDP11
                player1 = player1 + 1
        elif playerID == 2:
            if (pointMoved - pointBeforeMove) == 2:
                board[move[0]][move[1]] = FILLEDP22
                player2 = player2 + 2
            elif (pointMoved - pointBeforeMove) == 1:
                board[move[0]][move[1]] = FILLEDP21
                player2 = player2 + 1


    points = pointMoved - pointBeforeMove

    if(not playerPoints):        
        point = points * -1
        print("O    POINTS BEFORE:", pointBeforeMove)
        print("O    POINTS AFTER:", pointMoved)
        print("O    PLAYER1:", player1)
        print("O    PLAYER2:", player2)
        print("O    POINTS:", points)


    if(playerPoints):
        print("POINTS BEFORE:", pointBeforeMove)
        print("POINTS AFTER:", pointMoved)
        print("PLAYER1:", player1)
        print("PLAYER2:", player2)
        print("POINTS:", points)

    return newBoard, points




































































































































#def checkBestMove(server_board, Player_ID):
#    bestScore = -10000
#    tiedMoves = {}
#    for typeOfPlay in range(len(server_board)):
#        for line in range(len(server_board[typeOfPlay])):
#            if (server_board[typeOfPlay][line] == 99):
#                #AI player                
#                score = minimax(server_board, (typeOfPlay, line), 0, False, Player_ID, -1000, 1000)
#
#
#                if (score > bestScore):
#                    bestScore = score
#                    tiedMoves.clear()
#                if (score == bestScore):
#                    bestMove = (typeOfPlay, line)
#                    tiedMoves[bestMove] = [bestScore]
#
#    keys = list(tiedMoves.keys())
#    bestMove = keys[np.random.randint(0, len(keys))]
#    bestScore = tiedMoves[bestMove]
#    print("BESTMOVE:     ", bestMove)
#    print("BESTSCORE:    ", bestScore)
#    return bestMove
















































































































































































#def minimax(board, move,  depth, isMaximizing, Player_ID, alpha, beta):
#
#    currentPlayerPlayingID = Player_ID if isMaximizing else (Player_ID%2) + 1
#    _, point = movement_points(board, move, currentPlayerPlayingID, not isMaximizing)
#
#    if (depth == infoGame.maxDepth or 99 not in np.asarray(board).reshape(-1)):
#        _, score = movement_points(board, move, Player_ID, isMaximizing)
#        return score
#
#    board, _ = movement_points(board, move, currentPlayerPlayingID, isMaximizing)
#
#    if (isMaximizing):
#        bestScore = -10000
#        for typeOfPlay in range(len(board)):
#            for line in range(len(board[typeOfPlay])):
#                if (board[typeOfPlay][line] == 99):
#                    score = minimax(board, (typeOfPlay, line), depth + 1, False, currentPlayerPlayingID, alpha, beta)
#                    bestScore = max(score, bestScore)
#                    alpha = max(alpha, score)
#
#                    if beta <= alpha:
#                        break
#
#        board[move[0]][move[1]] = 99
#        return bestScore
#
#
#
#    else:
#        bestScore = 10000
#        for typeOfPlay in range(len(board)):
#            for line in range(len(board[typeOfPlay])):
#                if (board[typeOfPlay][line] == 99):
#                    score = minimax(board, (typeOfPlay, line), depth + 1, True, currentPlayerPlayingID, alpha, beta)                    
#                    bestScore = min(score, bestScore)
#                    beta = min(beta, score)
#                    if beta <= alpha:
#                        break
#
#        board[move[0]][move[1]] = 99
#        return bestScore
#
#
#
#
#
#
#
#def movement_points(board, move, playerID, isMaximizing):
#    N=6
#    EMPTY = 99
#    acumulador = 0
#    contador = 0
#    
#    pointBeforeMove = 0
#    pointMoved = 0
#
#    player1 = 0
#    player2 = 0
#    FILLEDP11 = 1
#    FILLEDP12 = 2
#    FILLEDP21 = -1
#    FILLEDP22 = -2
#
#    newBoard = list(map(list, board))
#
#    for i in range(len(board[0])):
#        if ((i + 1) % N) != 0:
#            if board[0][i] != EMPTY and board[0][i + 1] != EMPTY and board[1][contador + acumulador] != EMPTY and board[1][contador + acumulador + 1] != EMPTY:
#                pointBeforeMove = pointBeforeMove + 1
#            acumulador = acumulador + N
#        else:
#            contador = contador + 1
#            acumulador = 0    
#
#    acumulador = 0
#    contador = 0
#    newBoard[move[0]][move[1]] = 0
#
#    for i in range(len(newBoard[0])):
#        if ((i + 1) % N) != 0:
#            if newBoard[0][i] != EMPTY and newBoard[0][i + 1] != EMPTY and newBoard[1][contador + acumulador] != EMPTY and newBoard[1][contador + acumulador + 1] != EMPTY:
#                pointMoved = pointMoved + 1
#            acumulador = acumulador + N
#        else:
#            contador = contador + 1
#            acumulador = 0  
#
#    if pointMoved > pointBeforeMove:
#        if playerID == 1:
#            if (pointMoved - pointBeforeMove) == 2:
#                board[move[0]][move[1]] = FILLEDP12
#            elif (pointMoved - pointBeforeMove) == 1:
#                board[move[0]][move[1]] = FILLEDP11
#        elif playerID == 2:
#            if (pointMoved - pointBeforeMove) == 2:
#                board[move[0]][move[1]] = FILLEDP22
#            elif (pointMoved - pointBeforeMove) == 1:
#                board[move[0]][move[1]] = FILLEDP21
#
#    pointsMade = pointMoved-pointBeforeMove
#
#    return (board, pointsMade) if isMaximizing else (board, (-1) * (pointsMade))
#
#
#
#def draw_board2(board):
#    resultado = ''
#    acumulador = 0
#
#    for i in range(int(len(board[0])/5)):
#        if board[0][i] == 99:
#            resultado = resultado + '*   '
#        else:
#            resultado = resultado + '* - '
#        if board[0][i+6] == 99:
#            resultado = resultado + '*   '
#        else:
#            resultado = resultado + '* - '
#        if board[0][i+12] == 99:
#            resultado = resultado + '*   '
#        else:
#            resultado = resultado + '* - '
#        if board[0][i+18] == 99:
#            resultado = resultado + '*   '
#        else:
#            resultado = resultado + '* - '
#        if board[0][i+24] == 99:
#            resultado = resultado + '*   *\n'
#        else:
#            resultado = resultado + '* - *\n'
#
#        if i != 5:
#            for j in range(int(len(board[1])/5)):
#                if board[1][j + acumulador] == 99:
#                    resultado = resultado + '    '
#                else:
#                    resultado = resultado + '|   '
#            acumulador = acumulador + 6
#            resultado = resultado + '\n'
#
#    return resultado
#
#
#def CheckPlayersScore(board):
#    N=6
#    EMPTY = 99
#    acumulador = 0
#    contador = 0
#    contadorPuntos = 0
#
#    for i in range(len(board[0])):
#        if ((i + 1) % N) != 0:
#            if board[0][i] != EMPTY and board[0][i + 1] != EMPTY and board[1][contador + acumulador] != EMPTY and board[1][contador + acumulador + 1] != EMPTY:
#                contadorPuntos = contadorPuntos + 1
#            acumulador = acumulador + N
#        else:
#            contador = contador + 1
#            acumulador = 0
#
#    player1 = 0
#    player2 = 0
#    FILLEDP11 = 1
#    FILLEDP12 = 2
#    FILLEDP21 = -1
#    FILLEDP22 = -2
#
#    for i in range(len(board)):
#        for j in range(len(board[i])):
#            if board[i][j] == FILLEDP12:
#                player1 = player1 + 2
#            elif board[i][j] == FILLEDP11:
#                player1 = player1 + 1
#            elif board[i][j] == FILLEDP22:
#                player2 = player2 + 2
#            elif board[i][j] == FILLEDP21:
#                player2 = player2 + 1
#
#    # Aqui imprimimos los punteos de cada jugador
#    print("Punteo Jugador 1: ", player1, "    ", contadorPuntos)
#    print("Punteo Jugador 2: ", player2, "    ", contadorPuntos)    






#def checkBestMove(board, Player_ID):
#    bestScore = -1000
#    tiedMoves = {}
#    tied = False
#    for typeOfLine in range(len(board)):
#        for line in range(len(board[typeOfLine])):
#            #If its available
#            #Try to play and apply minimax
#            if (board[typeOfLine][line] == 99):
#                #Call to fun minimax
#                board[typeOfLine][line] = 0
#                score = minimax(board, 0, False, Player_ID, -1000, 1000, 0)
#                board[typeOfLine][line] = 99
#                print("EXITING MINIMAX:    ", score)
#                if(score > bestScore):
#                    print("NEW BEST SCORE:  ", score)
#                    bestScore = score
#                    bestMove = (typeOfLine, line)
#                    print("NEW BEST MOVE:  ", bestMove)
#                    tiedMoves.clear()
#                    print("CLEARED:   \n", tiedMoves)
#                    tied = False
#                if(score == bestScore):
#                    bestMove = (typeOfLine, line)
#                    tiedMoves[bestMove] = [bestScore]
#                    print("NEW BEST SCORE(TIED):  ", bestScore)
#                    print("NEW BEST MOVE(TIED):  ", bestMove)
#                    tied = True
#    if (tied):
#        keys = list(tiedMoves.keys())
#        bestMove = keys[np.random.randint(0, len(keys))]
#        print("NEW BEST SCORE(ANS TIED):  ", bestScore)
#        print("NEW BEST MOVE(ANS TIED):  ", bestMove)
#        return bestScore, bestMove
#    else:
#        print("NEW BEST SCORE(ANSWER):  ", bestScore)
#        print("NEW BEST MOVE(ANSWER):  ", bestMove)
#        return bestScore, bestMove









































#def validating_point_method(board):
#    N=6
#    EMPTY = 99
#    FILL = 0
#    acumulador = 0
#    contador = 0
#    contadorPuntos = 0
#    player1 = 0
#    player2 = 0
#    FILLEDP11 = 1
#    FILLEDP12 = 2
#    FILLEDP21 = -1
#    FILLEDP22 = -2
#
#    for i in range(len(board[0])):
#        if ((i + 1) % N) != 0:
#            if board[0][i] != EMPTY and board[0][i + 1] != EMPTY and board[1][contador + acumulador] != EMPTY and board[1][contador + acumulador + 1] != EMPTY:
#                contadorPuntos = contadorPuntos + 1
#            acumulador = acumulador + N
#        else:
#            contador = contador + 1
#            acumulador = 0    
#
#    for i in range(len(board[0])):
#        if board[0][i] == FILLEDP12:
#            player1 = player1 + 2
#        elif board[0][i] == FILLEDP11:
#            player1 = player1 + 1
#        elif board[0][i] == FILLEDP22:
#            player2 = player2 + 2
#        elif board[0][i] == FILLEDP21:
#            player2 = player2 + 1
#
#    for j in range(len(board[1])):
#        if board[1][j] == FILLEDP12:
#            player1 = player1 + 2
#        elif board[1][j] == FILLEDP11:
#            player1 = player1 + 1
#        elif board[1][j] == FILLEDP22:
#            player2 = player2 + 2
#        elif board[1][j] == FILLEDP21:
#            player2 = player2 + 1
#
#    return contadorPuntos






















































#def minimax(board, depth, maximizingPlayer, Player_ID, alpha, beta, acumulativePoints):
#    #scores = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
#    #Exit Condition
#    keepGoing = True
#    #print("DEPTH:  ", depth)
#    if (depth == infoGame.maxDepth):
#        score = validating_point_method(board)
#        if(score>0):
#            print("ANOTE   ", score)
#        #acumulativePoints = acumulativePoints + score
#        #print("ACUMULATIVE:   ", acumulativePoints, "   RECENT SCORE:    ", score)
#        keepGoing = False
#        return acumulativePoints
#
#    #New board to check results
#    Changedboard = list(map(list,board))
#    isScoring = False
#
#    if (Player_ID == 1):
#        multiplyingFactor = 1
#    elif (Player_ID == 2):
#        #If player No. 2 as the values are negative
#        #We multiply -1 so negatives becomes positive for minimax
#        #and positives become negatives
#        multiplyingFactor = -1
#
#    if (maximizingPlayer and keepGoing):
#        print("ENTERING MAXIMAZING")
#        bestScore = -1000
#        #Checking every element of the board
#        for typeOfLine in range(len(board)):      
#            #line is the actual value of the line  
#            for line in range(len(board[typeOfLine])):
#                if (Changedboard[typeOfLine][line] == 99):
#                    Changedboard, Myscore = move_And_Points(Changedboard, (typeOfLine, line))
#                    #print("AFTER BOARD: \n", Changedboard)
#                    #print("POINTS: \n", Myscore)
#                    Myscore = Myscore * multiplyingFactor
#                    if (Myscore > 0):
#                        #print("I FUCKING SCORED AGAIN  ", Myscore)
#                        Myscore = Myscore + acumulativePoints
#                        Myscore = minimax(Changedboard, depth + 1, True, Player_ID, alpha, beta, Myscore)
#                    elif (Myscore <= 0):
#                        #print("OPONENT FUCKING SCORED    ", Myscore)
#                        Myscore = acumulativePoints + Myscore
#                        Myscore = minimax(Changedboard, depth + 1, False, Player_ID, alpha, beta, Myscore)                    
#                    Changedboard[typeOfLine][line] = 99
#                    bestScore = max(Myscore, bestScore)
#                    alpha = max(alpha, Myscore)
#                    if (beta <= alpha):
#                        break
#        return bestScore
#                    
#    elif (maximizingPlayer != True and keepGoing):
#        print("ENTERING MINIMAZING")
#        bestScore = 1000
#        #Checking every element of the board
#        for typeOfLine in range(len(Changedboard)):      
#            #line is the actual value of the line  
#            for line in range(len(Changedboard[typeOfLine])):
#                if (Changedboard[typeOfLine][line] == 99):
#                    Changedboard, Myscore = move_And_Points(board, (typeOfLine, line))
#                    #Change TOTALPOINT NO LONGER EXISTS
#                    Opscore = totalPoint(board, Changedboard) * multiplyingFactor
#                    #print(Opscore)
#                    if (Opscore < 0):
#                        Opscore = acumulativePoints + Opscore
#                        Opscore = minimax(Changedboard, depth + 1, False, Player_ID, alpha, beta, Opscore)
#                    else:
#                        Opscore = Opscore + acumulativePoints
#                        Opscore = minimax(Changedboard, depth + 1, True, Player_ID, alpha, beta, Opscore)
#                    Changedboard[typeOfLine][line] = 99
#                    bestScore = min(Opscore, bestScore)
#                    beta = min(beta, Opscore)
#                    if (beta <= alpha):
#                        break
#        return bestScore
































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



#def draw_board(board):
#    standard_board = [
#        ['.', '.', '.', '.', '.', '.'],
#        [' ', ' ', ' ', ' ', ' ', ' '],
#        ['.', '.', '.', '.', '.', '.'],
#        [' ', ' ', ' ', ' ', ' ', ' '],
#        ['.', '.', '.', '.', '.', '.'],
#        [' ', ' ', ' ', ' ', ' ', ' '],
#        ['.', '.', '.', '.', '.', '.'],
#        [' ', ' ', ' ', ' ', ' ', ' '],
#        ['.', '.', '.', '.', '.', '.'],
#        [' ', ' ', ' ', ' ', ' ', ' '],
#        ['.', '.', '.', '.', '.', '.'],
#    ]
#
#    for i in range(0,len(board)):
#        if (i==0): 
#            acumulador = 0   
#            start = 0
#            end = len(board[i])      
#            N = 6
#            for j in board[i]:
#                if (j != 99):
#                    if (((board[i].index(j, start, end)) % N) == 0) & (board[i].index(j, start, end) != 0):
#                        acumulador +=1
#                    try:
#                        standard_board[acumulador*2][(board[i].index(j, start, end)) % N] = '._'
#                    except:
#                        pass                    
#                start += 1
#        if (i==1):
#            acumulador = 0   
#            start = 0
#            end = len(board[i])      
#            N = 6
#            for j in board[i]:
#                if (j != 99):
#                    if (((board[i].index(j, start, end)) % N) == 0) & (board[i].index(j, start, end) != 0):
#                        acumulador +=1
#                    try:
#                        standard_board[(acumulador*2)+1][(board[i].index(j, start, end) +1) % N] = '|'
#                    except:
#                        pass
#                start += 1
#    print(standard_board)
        







infoGame = infoGame()
#infoGame.username = input("User: \n")
#infoGame.tournament_id = input("Tournament ID: \n")
#host = input("Host address: \n")
infoGame.username = "GuilleAI"
infoGame.tournament_id = "7"
host = "http://localhost:4000"
sio.connect(host)