from player import Player, BotPlayer
import numpy as np
import random as rd
# from utils import update_mat_adj, switch

class Game(object):
    def __init__(self, size:int, is_PvBot:bool, color_choice:int|None, difficulty:int|None=5):
        # color_choice, 0,1 ou 2 : 0 = red ; 1 = blue ; 2 = random
        if color_choice == None:
            color_choice = 0
        if color_choice == 2: #choix couleur random
            color_choice = rd.randint(0,1)
        color = ['red', 'blue']

        self.size = size
        self.mat_plateau = np.zeros((size,size),dtype=int) # 0 : case vide ; 1 : rouge ; 2 : bleu

        p1 = Player(0, color.pop(color_choice), size)
        if is_PvBot:
            p2 = BotPlayer(1, color.pop(), size, difficulty)
        else:
            p2 = Player(1, color.pop(), size)
        self.players = (p1,p2)

        self.turn = 0
        self.game_over = False

   
        

    
    def tile_change(self, x, y, player_id):
        '''Fonction qui gère l'ajout d'un pion sur le plateau'''
        player = next(p for p in self.players if p.id == player_id)
        self.mat_plateau[y][x] = player.color_id
        self.turn += 1
        
    
    def switch(self):
        p1, p2 = self.players
        Player.switch(p1, p2)
