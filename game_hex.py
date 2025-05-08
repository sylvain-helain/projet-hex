import numpy as np
import random as rd
import time
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
CASES_ADJ = [(0,-1), (1,-1), (1,0), (-1,0), (-1,1), (0,1)] # (dx,dy)
# . O O                      -->    . O O
# O X O   (vue matrice)      -->     O X O   (vue plateau hexagonal)
# O O .                      -->      O O .

CASES_ADJ_MINIMAX = CASES_ADJ + [(-1,-1), (1,1), (-2,1), (-1,2), (1,-2), (2,-1)]
# . . . O .                  -->    . . . O .
# . O O O O                  -->     . O O O O
# . O X O .  (vue matrice)   -->      . O X O .    (vue plateau hexagonal)
# O O O O .                  -->       O O O O .
# . O . . .                  -->        . O . . .
# on regarde les cases adjacentes et les ponts (cases avec lesquelles on peut les relier avec deux différents chemins possibles)

p1_border1 = lambda n: [(x, 0) for x in range(n)]
p1_border2 = lambda n: [(x, n - 1) for x in range(n)]

p2_border1 = lambda n: [(0, y) for y in range(n)]
p2_border2 = lambda n: [(n - 1, y) for y in range(n)]

p1_borders = lambda n: p1_border1(n) + p1_border2(n)
p2_borders = lambda n: p2_border1(n) + p2_border2(n)

def get_cases_adj(x,y,n):
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ if (0 <= x+dx < n) and (0 <= y+dy < n)]

def get_cases_adj_minimax(x,y,n):
    return [(x+dx, y+dy) for dx, dy in CASES_ADJ_MINIMAX if (0 <= x+dx < n) and (0 <= y+dy < n)]


def dijkstra(dict_adj:dict, game_size:int, x:int, y:int):
    poids = {(x, y) : np.inf for x in range(game_size) for y in range(game_size)}
    poids[(x,y)] = 0
    marqués = set([(x,y)])
    traités = set()
    while len(marqués) != len(traités):
        x,y = min(marqués-traités, key=lambda i: poids[i])
        traités.add((x,y))
        for value, x1, y1 in dict_adj[(x,y)]:
            marqués.add((x1,y1))
            if (longueur := value + poids[(x,y)]) < poids[(x1,y1)]:
                poids[(x1,y1)] = longueur
    return poids

def find_shortest_path_length(dict_adj:dict, game_size:int, border1:list, border2:list):
    min_value = np.inf
    for x, y in border1:
        poids = dijkstra(dict_adj, game_size, x, y)
        min_value = min(min_value, min([poids[coo] for coo in border2]))
    return min_value

def create_dict_adj(mat:np.ndarray, id:int, borders:list):
    id_opp = 1 if id==2 else 2
    n = mat.shape[0]
    res = {(x,y):list() for x in range(n) for y in range(n)}
    for y1 in range(n):
        for x1 in range(n):
            for x2, y2 in get_cases_adj(x1,y1,n):
                case1, case2 = mat[y1][x1], mat[y2][x2]
                if case1 == id_opp or case2 == id_opp:
                    continue
                is_c1_border, is_c2_border = (x1,y1) in borders, (x2,y2) in borders
                if case1 == id and case2 == id:
                    value = 0.0
                elif is_c1_border and is_c2_border:
                    value = 1.5
                elif is_c1_border:
                    if case1 == id and case2 == 0:
                        value = 0.5
                    elif case1 == 0 and case2 == id:
                        value = 1.0
                    else:
                        value = 1.5
                elif is_c2_border:
                    if case2 == id and case1 == 0:
                        value = 0.5
                    elif case2 == 0 and case1 == id:
                        value = 1.0
                    else:
                        value = 1.5
                elif case1==id or case2==id:
                    value = 0.5
                else:
                    value = 1.0
                
                res[(x1,y1)].append([value,x2,y2])

    return res





class Player(object):
    def __init__(self, id, n):
        self.id = id
        self.n = n
        if id==1:
            self.border1 = [(x,0) for x in range(n)]
            self.border2 = [(x,n-1) for x in range(n)]
        elif id==2:
            self.border1 = [(0,y) for y in range(n)]
            self.border2 = [(n-1,y) for y in range(n)]
        else:
            raise Exception('id incorrect: veuillez entrer 1 ou 2')
        self.borders = self.border1 + self.border2
        self.adjacences = self.create_dict_adj()

    def create_dict_adj(self) -> dict:
        pass

def potential_moves(mat:np.ndarray):
    n = mat.shape[0]
    return {(x2,y2) for y1,x1 in np.argwhere(mat!=0) 
            for x2,y2 in get_cases_adj_minimax(x1,y1,n) 
            if mat[y2][x2] == 0}



def get_best_move(mat:np.ndarray, player:Player, depth=2):
    n = mat.shape[0]
    if np.all(mat <= 1): # si c'est le premier tour du bot
        while True:
            if n > 3:
                x,y = rd.randint(1,n-2), rd.randint(1,n-2) # retourne un coup au hasard dans le centre du plateau
            else: # si la taille du plateau est <= 3
                x,y = rd.randint(0,n-1), rd.randint(0,n-1)
            
            if mat[y][x] == 0:
                return x,y
    max_id = player.id
    min_id = 1 if max_id == 2 else 2
    res = {}
    moves = potential_moves(mat)
    # print(len(moves))
    for index, coo in enumerate(moves):
        pourcentage = (index+1)*100//len(moves) 
        print(f"\r{pourcentage*'#'+(100-pourcentage)*'-'} | {pourcentage}%", end='', flush=True)
        # print('hey')
        x,y = coo
        mat[y][x] = max_id
        res[(x,y)] = minimax(
            mat=mat, 
            max_id=max_id, 
            min_id=min_id, 
            depth=depth-1, 
            alpha=-np.inf, beta=np.inf, 
            is_max_turn=False
            )
        mat[y][x] = 0
    print("\r" + " " * 150 + "\r", end='', flush=True)
    return max(res, key=res.get) # retourne le coup sous forme de coordonnées x,y


def fonction_evaluation(mat:np.ndarray, max_id:int, depth):
    n = mat.shape[0]
    p1_pcc_len = find_shortest_path_length(create_dict_adj(mat, 1, p1_borders(n)), n, p1_border1(n), p1_border2(n))
    p2_pcc_len = find_shortest_path_length(create_dict_adj(mat, 2, p2_borders(n)), n, p2_border1(n), p2_border2(n))
    # print(mat)
    # print(is_board_terminal(mat))
    if p1_pcc_len == 0:
        # print('win')
        return 1000*(depth+1) if max_id == 1 else -1000*(depth+1)
    elif p2_pcc_len == 0:
        # print('lose')
        return 1000*(depth+1) if max_id == 2 else -1000*(depth+1)
    else:
        # print(mat)
        score_p1 = p2_pcc_len - p1_pcc_len
        # print(score_p1)
        # score_p1 = score_p1/(p2_pcc_len+p1_pcc_len)
        # print(score_p1)
        # print(mat, score_p1)
        return score_p1 if max_id == 1 else -score_p1


def minimax(mat:np.ndarray, max_id:int, min_id:int, 
                        depth:int, alpha:float, beta:float, is_max_turn:bool) -> float:
    # print(mat, is_board_terminal(mat))
    if is_board_terminal(mat) or depth <= 0: # si la position est terminale ou si on a atteint la profondeur de recherche maximale        
        return fonction_evaluation(mat, max_id, depth)
    
    if is_max_turn: #max
        max_eval = -np.inf
        for x,y in potential_moves(mat):
            mat[y][x] = max_id
            eval = minimax(mat, max_id, min_id, depth-1, alpha, beta, False)
            mat[y][x] = 0
            max_eval = max(max_eval, eval)

            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else: #min
        min_eval = np.inf
        for x,y in potential_moves(mat):
            mat[y][x] = min_id
            eval = minimax(mat, max_id, min_id, depth-1, alpha, beta, True)
            mat[y][x] = 0
            min_eval = min(min_eval, eval)

            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

        

class GameHex(object):
    def __init__(self, n:int, pvp:bool):
        self.mat = np.zeros((n,n), dtype=int)
        self.n = n
        self.p1 = Player(1, n)
        self.p2 = Player(2, n)
        self.turn = self.p1
        self.game_over = False

    
    def next_turn(self):
        if self.turn == self.p1:
            self.turn = self.p2
        else:
            self.turn = self.p1
    
    def evaluate(self):
        for p in (self.p1,self.p2):
            # start = time.time()
            dict_adj = create_dict_adj(self.mat, p.id, p.borders)
            # print(dict_adj)
            # end = time.time()
            # print(f"temps d'execution : {end-start:.4f} secondes")

            # start = time.time()
            path_len = find_shortest_path_length(dict_adj, self.n, p.border1, p.border2)
            # end = time.time()
            # print(f"temps d'execution : {end-start:.4f} secondes")
            # print(f"Player{p.id} : {path_len}")

def blue(char:str):
    return f"\033[34m{char}\033[0m"

def red(char:str):
    return f"\033[31m{char}\033[0m"


def prompt(mat:np.ndarray):
    while True:
        try:
            move = input("Case? : ").strip()
            x,y = ALPHABET.index(move[0].upper()), int(move[1:])-1
            if mat[y][x] == 0:
                return x,y
        except (ValueError, IndexError):
            continue
    



def affiche_jeu(mat:np.ndarray):
    n = mat.shape[0]
    print('', red(' '.join([i for i in ALPHABET[:n]])))
    pad = 2
    for y in range(n):
        print(blue(f"{y+1} ".rjust(pad, " ")), end='')
        pad += 1
        for x in range(n):
            value = mat[y][x]
            if value == 0:
                print("⬡", end=" ")
            elif value == 1:
                print(red("⬢"), end=" ")
            elif value == 2:
                print(blue("⬢"), end=" ")
            else:
                raise Exception("erreur couleur plateau")
        print(blue(' '+str(y+1)))
    print(red(' '*pad + ' '.join([i for i in ALPHABET[:n]])))

def is_board_terminal(board:np.ndarray):
    size = board.shape[0]
    goals = (
        [(x,y) for y in (0,size-1) for x in range(0,size)],
        [(x,y) for x in (0,size-1) for y in range(0,size)]
    )
    for i in range(2):
        side1, side2 = goals[i][:size], goals[i][size:]
        for x,y in side1:
            if board[y][x] == i+1:
                marqués = []
                if are_sides_linked(board, x, y, side2, size, color_id=i+1, marqués=marqués):
                    return True
    return False

def are_sides_linked(board:np.ndarray, x:int, y:int, goal:tuple, size:int, color_id:int, marqués:list):
    if (x,y) in goal:
        return True
    
    marqués.append((x,y))

    for y1 in range(-1,2):
        for x1 in range(-1,2):
            x2, y2 = x+x1, y+y1
            if y1 == x1 or x2 >= size or x2 < 0 or y2 >= size or y2 < 0:
                continue
            if board[y2][x2] == color_id and (x2,y2) not in marqués:
                if are_sides_linked(board, x2, y2, goal, size, color_id, marqués):
                    return True
    return False


def main():
    game_size = int(input("Taille du plateau de jeu ? : "))
    p1_bot = True if input("Player1 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    p2_bot = True if input("Player2 Joueur ou Bot ? [J/B] : ").lower() == "b" else False
    game = GameHex(game_size, pvp=False)
    affiche_jeu(game.mat)
    # t = 0
    # start = time.time()
    while not game.game_over:
        # t+= 1
        # print(f"Tour de", "Player1" if game.turn == game.p1 else "Player2")
        if game.turn == game.p1 and p1_bot:
            x,y = get_best_move(game.mat, game.p1, 4)
        elif game.turn == game.p1 and not p1_bot:
            x,y = prompt(game.mat)
        elif game.turn == game.p2 and p2_bot:
            x,y = get_best_move(game.mat, game.p2, 4)
        else:
            x,y = prompt(game.mat)
        game.mat[y][x] = game.turn.id
        affiche_jeu(game.mat)
        if game.turn == game.p1:
            print(red(f"{ALPHABET[x]}{y+1}"))
        else:
            print(blue(f"{ALPHABET[x]}{y+1}"))
        game.evaluate()
        game.next_turn()
        if is_board_terminal(game.mat):
            game.game_over = True
            print('GAME OVER')
            # end = time.time()
            # print('go', t, f"{end-start:.4f} sec")


if __name__ == '__main__':
    main()

        
    
