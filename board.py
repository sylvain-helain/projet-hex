import tkinter as tk
from game import Game
from player import Player, BotPlayer
from ai import Ai
from math import sin, cos, sqrt, pi
from constants import B_WIDTH, B_HEIGHT, PAD, COLORS, LETTERS


import random as rd

class BoardApp(tk.Tk):
    '''Classe pour l'affichage d'une fenêtre tkinter pour affichage du plateau de jeu hex.
    Prend plusieurs paramètres en entrée à l'initialisation comme:
    - la taille du plateau, 
    - le mode de jeu JcJ ou JcBot,
    - la couleur du joueur humain
    - la difficulté du bot '''
    running = []
    def __init__(self, size:int, isPvBot:bool=False, start_color:int|None=None, difficulty:int|None=None):
        '''Création du plateau
        size : [6:16] -> taille du plateau
        isPvBot : True -> JcBot ; False -> JcJ
        start_color : 0 -> Rouge ; 1 -> Bleu ; 2 -> Aléatoire ; None -> Si JcJ
        difficulty : [1:10] -> 1 étant la difficulté la plus faible et 10 la plus élevée'''
        super().__init__()
        BoardApp.running.append(self)
        self.iconbitmap("./icone.ico")
        self.title('Hex - Game')
        self.window_width= 950
        self.width = B_WIDTH
        self.height = B_HEIGHT
        self.resizable(False,False)
        self.center_window()

        self.game = Game(size, isPvBot, start_color, difficulty) # comment
        self.ai = Ai(self.game)

        # canvas
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=6)
        # bouton switch
        self.b_switch = tk.Button(self, text='Switch', command=self.switch, state='disabled', bg='grey')
        self.b_switch.grid(row=0,column=1, sticky="nsew")
        # bouton afficher / masquer évaluation
        self.b_toggle_eval = tk.Button(self, text='Toggle Eval', command=self.toggle_eval)
        self.b_toggle_eval.grid(row=0, column=2, sticky="nsew")
        # affichage des couleurs pour chaque joueur
        self.p1, self.p2 = sorted(self.game.players,key=lambda x: x.id) # le joueur dont l'id est 0 aura p1
        self.canvas.create_text(self.width*2//10,self.height-PAD, text=f"Player {self.p1.id+1} ({'Bot' if type(self.p1) == BotPlayer else 'Human'}): {self.p1.color}", font="consolas 20", tag='player1_info', fill=self.p1.color)
        self.canvas.create_text(self.width*8//10,self.height-PAD, text=f"Player {self.p2.id+1} ({'Bot' if type(self.p2) == BotPlayer else 'Human'}): {self.p2.color}", font="consolas 20", tag='player2_info', fill=self.p2.color)
        # affichage du tour
        couleur_tour = COLORS[self.game.turn%2]
        joueur_tour = next(p for p in self.game.players if p.color == couleur_tour)
        self.canvas.create_text(self.width-PAD*5,PAD,text=f"PLAYER{joueur_tour.id+1}'S TURN", font=('consolas',20), fill=couleur_tour, tag='turn_count')

        self.canvas.bind('<Motion>', self.move) # mouvement de souris
        self.canvas.bind('<Button-1>', self.click) # clic gauche souris

        self.draw_board(self.game.size) #dessine le plateau

        # empeche la fermeture avec la croix
        self.protocol("WM_DELETE_WINDOW", lambda:print('Veuillez fermer la fenêtre depuis le menu principal.'))
        if type(joueur_tour) == BotPlayer:
            self.clickable = False
            self.get_ai_input()
        else:
            self.clickable = True


    
    def toggle_eval(self):
        '''Fonction pour activer / désactiver l'affichage de l'évaluation sur le canvas du plateau'''
        pass

    def center_window(self):
        '''Fonction pour ajuster l'emplacement de la fenêtre en fonction de la résolution de l'écran'''
        l = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        x = (l*3//5) - (self.window_width//2)
        y = (h*7//16) - (self.height//2)
        self.geometry(f"{self.window_width}x{self.height}+{x}+{y}")

    def terminate(self):
        '''Fontion appelée pour supprimer l'instance de plateau crée dans la liste Board.running avant de fermer la fenêtre'''
        BoardApp.running.remove(self)
        self.destroy()
    
    def move(self, event):
        '''Fonction appelée à chaque mouvement de souris, permet de montrer un rond coloré (bleu ou rouge)
        sous le pointeur de la souris indiquant quel Joueur doit colorer une case'''
        x,y = event.x, event.y
        self.canvas.delete('cursor')
        if x > self.width or x < 0 or y > self.height or y < 0: # si le curseur est en dehors des limites du canvas
            return
        self.canvas.create_oval(x-7,y-7,x+7,y+7,fill=COLORS[self.game.turn%2], width=0, tag='cursor')

    def draw_hexagon(self, x,y,r,tag):
        '''Dessine un hexagone à la position x,y avec un "rayon" r, lui donne un tag spécifique pour tkinter'''
        # on calcule 6 points équidistants sur le cercle de rayon r pour tracer l'hexagone (en incrémentant de pi/3 la rotation)
        points = [[x+cos(pi/6+i*pi/3)*r,y+sin(pi/6+i*pi/3)*r] for i in range(6)]

        # création du polygone avec les points calculés
        self.canvas.create_polygon(points,fill='light grey',outline='black',width=2,tag=tag)

        # si cet hexagone est situé sur un des bords, on colore certaines de ses arêtes en la couleur du but associé

        if tag.split(':')[0] == str(0): # côté gauche : but bleu
            for ligne in (points[1:3], points[2:4]):
                # les tags ignore et ignore2 sont utilisés pour les filtrers lorsqu'on cherche a récupérer le tag d'une case lors d'un clic
                self.canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')

        if tag.split(':')[0] == str(self.game.size-1): # côté droit : but bleu
            for ligne in ([points[-1], points[0]],points[4:6]):
                self.canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')

        if tag.split(':')[-1] == str(0): # côté haut : but rouge
            for ligne in (points[3:5], points[4:6]):
                self.canvas.create_line(ligne, fill='red', width=5, tag='ignore2')

        if tag.split(':')[-1] == str(self.game.size-1): # côté bas : but rouge
            for ligne in (points[1:3], points[0:2]):
                self.canvas.create_line(ligne, fill='red', width=5, tag='ignore2')

    def draw_board(self, n):
        '''Fonction qui dessine le plateau en entier, prend en entrée une taille n de plateau.
        Dessinera un plateau de taille n*n.
        On fera plusieurs appels à draw_hexagon pour accomplir cette tache.
        Chaque hexagone aura son tag spécifique pour faciliter la récupération d'une case lors d'un clic sur le canvas.'''
        spacing_x = (self.width-PAD*2)/(n+n/2) # distance x entre chaque centre d'hexagones
        rad = spacing_x/sqrt(3) # rayon pour les cercles sur lesquels on va se baser pour dessiner les hexagones
        spacing_y = rad*sqrt(2) # distance y entre chaque centre d'hexagones
        pad_y = ((self.height-PAD*2)-spacing_y*n)/2 # padding du plateau pour avoir une marge avec le bord du canvas

        # boucle principle
        for y in range(n):
            for x in range(n):
                # calcule le centre x1,y1 de l'hexagone
                x1 = x*spacing_x+PAD+rad+y*spacing_x/2 
                y1 = pad_y + y*spacing_y+PAD+rad
                self.draw_hexagon(x1,y1,rad,tag=f"{x}:{y}")
                # si il se trouve sur les bords, on ajoute un texte pour donner le nom de la colonne ou de la ligne
                if x == 0: # gauche, numéro ligne
                    self.canvas.create_text(x1-rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
                if x == n-1: # droit, numéro ligne
                    self.canvas.create_text(x1+rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
                if y == 0: # haut, lettre colonne
                    self.canvas.create_text(x1-rad,y1-rad*1.5,text=LETTERS[x],font=('consolas',20),tag='ignore')
                if y == n-1: # bas, lettre colonne
                    self.canvas.create_text(x1+rad,y1+rad*1.5,text=LETTERS[x],font=('consolas',20),tag='ignore')

        self.canvas.tag_lower('ignore')
        self.canvas.tag_raise('ignore2') # pour afficher les bordures bleues et rouges en haut des hexagones

    def change_tile_color(self, x, y, color):
        '''Fonction qui change la coeuleur de la case x,y à la couleur en entrée'''
        self.canvas.itemconfig(f"{x}:{y}", fill=color) # on change la couleur de la case grâce à son tag qui correspond à ces coordonnées

    def get_tile(self, x, y) -> tuple|None:
        '''Récupère les coordonnées de la case (utilisables dans la matrice du jeu) à partir des coordonnées x,y d'un clic sur le canvas
        On retourne None si le clic n'intersecte pas une case.
        On retourne x,y ses coordonnées d'une case si le clic intersecte une case dans le canvas.'''
        # retourne une liste des tags des objets dessinés dans le canvas qui intersectent le clic
        overlap = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)

        if len(overlap) == 0: # si il n'y a rien dans la liste
            return None
        
        tags = [self.canvas.gettags(overlap[i])[0] for i in range(len(overlap))]
        tags = [i for i in tags if i not in ['ignore', 'ignore2']] # on filtre la liste et on retire les objets dont le tag est à ignorer
        if len(tags) == 0: # si la liste résultate est vide alors on retourne None
            return None
        
        tag = tags[0] # notre case trouvée
        if self.canvas.itemcget(tag,"fill") == 'light grey': # si la case n'est pas déjà colorée par un joueur (donc grise)
            x,y = tag.split(':') # on décompose ses coordonnées grâce à son tag qui est de la forme "x:y"
            return int(x), int(y)
        else:
            return None

    def get_ai_input(self):
        self.ai.get_next_turn()
        if self.game.turn == 1 and rd.randint(0,1) == 1:
            self.switch()
            return

        while True:
            x,y = rd.randint(0,self.game.size-1), rd.randint(0,self.game.size-1)
            if self.game.mat_plateau[y][x] == 0:
                break
        self.handle_tile_change(x, y)

    def click(self, event):
        '''Fonction bind au clic souris gauche, appelle la fonction get_tile pour savoir si on séléctionne une case valide,
        si oui elle appelle la fonction handle_tile_change pour modifier la configuration du plateau de jeu dans la classe Game.'''
        if (res := self.get_tile(event.x, event.y)) == None or self.game.game_over or self.clickable == False: # si le clic n'est pas valide ou la partie est terminée
            return
        x, y = res
        self.handle_tile_change(x, y)
    
    def switch(self):
        '''Fonction bind au bouton switch, appelle la fonction switch du jeu, change l'affichage pour intervertir les roles des joueurs'''
        print('switch')
        self.b_switch.configure(state='disabled', bg='grey', fg='black') # désactive le bouton
        self.game.switch()
        joueur_tour = next(p for p in self.game.players if p.color == COLORS[self.game.turn%2])
        self.canvas.itemconfig('turn_count', text=f"PLAYER{joueur_tour.id+1}'S TURN")
        self.canvas.itemconfig("player1_info", text=f"Player {self.p1.id+1} ({'Bot' if type(self.p1) == BotPlayer else 'Human'}): {self.p1.color}", font="consolas 20", fill=self.p1.color)
        self.canvas.itemconfig("player2_info", text=f"Player {self.p2.id+1} ({'Bot' if type(self.p2) == BotPlayer else 'Human'}): {self.p2.color}", font="consolas 20", fill=self.p2.color)
        if type(joueur_tour) == BotPlayer:
            self.clickable = False
            self.get_ai_input()
        else:
            self.clickable = True
    
    def display_pcc(self):
        '''Fonction pour afficher les plus courts chemins de chaque joueur'''
        self.canvas.delete('chemin')
        # définition des variables à utiliser pour calculer les x et y relatifs au canvas de chaque noeuds pour les chemins
        n = self.game.size
        spacing_x = (self.width-PAD*2)/(n+n/2)
        rad = spacing_x/sqrt(3)
        spacing_y = rad*sqrt(2)
        pad_y = ((self.height-PAD*2)-spacing_y*n)/2

        for player in self.game.players: # pour les 2 joueurs
            chemin = player.pcc[1] # retourne le chemin sous forme de liste de coordonnées
            # boucle principale
            for i in range(len(chemin)): # on parcours chaque noeud du chemin
                x,y = chemin[i]
                # calcul des coordonnées x et y relatives au canvas
                x1 = x*spacing_x+PAD+rad+y*spacing_x/2
                y1 = pad_y + y*spacing_y+PAD+rad
                chemin[i] = (x1,y1) # on écrase les anciennes coordonnées avec les nouvelles
            if chemin: # ce if est utile dans le cas où un joueur n'a pas de pcc (si il a perdu)
                # dessine le chemin
                self.canvas.create_line(chemin, fill='light grey', tag='chemin', width=8, smooth=True, capstyle='round')
                self.canvas.create_line(chemin, fill=player.color, tag='chemin', width=4, smooth=True, capstyle='round')
    
    def update_eval_bar(self):
        '''Fonction utilisée pour modifier la barre d'évaluation selon l'évaluation actuelle des joueurs'''
        player1_percentage = self.p1.score/(self.p1.score+self.p2.score) # calcul du pourcentage du joueur1
        print(f"player1\n{player1_percentage}\n{self.p1.color}\n")
        print(f"player2\n{1-player1_percentage}\n{self.p2.color}\n") # 1-pourcentage
        # calcul coordonnées début, fin de la barre pour les deux joueurs
        xe, ye = self.width/2, self.height-50
        size_e = 150
        middle = size_e*player1_percentage
        if player1_percentage <= 1: # si les deux joueurs ont un score
            self.canvas.delete('eval_bar')
            self.canvas.create_rectangle(xe-size_e/2,ye-15/2,xe-size_e/2+middle,ye+15,fill=self.p1.color,tag='eval_bar')
            self.canvas.create_rectangle(xe-size_e/2+middle,ye-15/2,xe+size_e/2,ye+15,fill=self.p2.color,tag='eval_bar')


    def handle_tile_change(self, x, y):
        '''Fonction utilisée pour appeler toutes les fonctions utiles à changer la configuration du jeu et de l'interface
        lorsqu'un joueur à joué un coup à des coordonnées x,y en entrée.'''
        self.change_tile_color(x, y, COLORS[self.game.turn%2]) # change la couleur de la case
        player = next(p for p in self.game.players if p.color == COLORS[self.game.turn%2])
        self.game.tile_change(x,y, player.id) # permet a l'instance de la classe Game du jeu de s'actualiser
        Ai.evaluate_position(self.p1, self.p2)
        self.display_pcc() # montre les plus courts chemins s'ils existent
        self.update_eval_bar() # affiche la barre d'évaluation si possible

        if self.game.turn == 1: # si c'est le 2ème tour, le joueur bleu peut choisir de switch
            self.b_switch.configure(state='normal', bg='blue', fg='white')
        elif self.game.turn == 2: # 3ème tour, ce n'est plus possible, le bouton est désactivé
            self.b_switch.configure(state='disabled', bg='grey', fg='black')

        # update la couleur du curseur directement après le clic (car la fonction move le fera que si le curseur bouge à nouveau)
        self.canvas.itemconfig('cursor', fill=COLORS[self.game.turn%2]) 
        # update l'affichage du tour
        couleur_tour = COLORS[self.game.turn%2]
        joueur_tour = next(p for p in self.game.players if p.color == couleur_tour)
        self.canvas.itemconfig('turn_count', fill=couleur_tour, text=f"PLAYER{joueur_tour.id+1}'S TURN")

        if type(joueur_tour) == BotPlayer:
            self.clickable = False
            self.get_ai_input()
        else:
            self.clickable = True

        # if self.game.game_over:
        #     self.canvas.create_text(self.width/2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font="consolas 41 bold", fill='white')
        #     self.canvas.create_text(self.width/2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font=('consolas',40), fill=self.game.winner)

