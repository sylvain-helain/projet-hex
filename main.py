import tkinter as tk
from math import cos, sin, pi, sqrt
import numpy as np
import random as rd
from tkinter import ttk
from PIL import Image, ImageTk



class Player(object):
    def __init__(self, id, color, game_size):
        self.id = id
        self.color = color
        self.pcc = [np.inf,[]]
        self.max_pcc = 0
        self.game_size = game_size
        self.score = 0

        self.mat_adjacence = np.full((game_size**2, game_size**2), fill_value=np.inf)
        self.mat_points = np.full((game_size, game_size), fill_value=np.inf)

        if id == 1:
            self.game_borders = [(x,y) for x in [0, game_size-1] for y in range(game_size)]
        else:
            self.game_borders = [(x,y) for y in [0, game_size-1] for x in range(game_size)]

    def find_shortest_paths(self):
        self.pcc = [np.inf, []]
        self.max_pcc = 0
        self.mat_points = np.full((self.game_size, self.game_size), fill_value=np.inf)
        border1, border2 = self.game_borders[:self.game_size], self.game_borders[self.game_size:]
        for x1, y1 in border1:
            poids, chemins = self.dijkstra(x1,y1)
            # print(poids,chemins)
            for x2, y2 in border2:
                p = poids[(x2, y2)]
                if p < self.pcc[0]:
                    self.pcc = [p, []]
                    new_pcc = True
                else:
                    new_pcc = False
                
                if p > self.max_pcc:
                    self.max_pcc = p

                node = (x2, y2)
                while node != None:
                    x3, y3 = node
                    if new_pcc:
                        self.pcc[1].append((x3,y3))
                    if p < self.mat_points[y3][x3]:
                        self.mat_points[y3][x3] = p
                    node = chemins[(x3, y3)]

    def dijkstra(self, x:int, y:int):
        poids = {(i%self.game_size, i//self.game_size) : np.inf for i in range(self.game_size**2)}
        chemins = {(i%self.game_size, i//self.game_size) : None for i in range(self.game_size**2)}
        poids[(x,y)] = 0
        marqués = set([(x,y)])
        traités = set([])
        while len(marqués) != len(traités):
            x,y = min(marqués-traités, key=lambda i: poids[i])
            traités.add((x,y))
            for x1 in range(-1,2):
                for y1 in range(-1,2):
                    y2, x2 = y+y1, x+x1
                    if (y1 == x1) or (y2 >= self.game_size) or (y2 < 0) or (x2 >= self.game_size) or (x2 < 0):
                        continue
                    yp, xp = y*self.game_size + x, y2*self.game_size + x2
                    value = self.mat_adjacence[yp][xp]
                    if value != np.inf:
                        marqués.add((x2,y2))
                        if (longueur := value + poids[(x,y)]) < poids[(x2,y2)]:
                            poids[(x2,y2)] = longueur
                            chemins[(x2,y2)] = (x,y)

        
        return poids, chemins


class Bot(Player):
    def __init__(self, id, color, game_size, difficulty):
        super().__init__(id, color, game_size)
        self.difficulty = difficulty

class Game(object):
    def __init__(self, size:int, is_PvBot:bool, color_choice:int|None, difficulty:int|None=5):
        # color_choice, 0,1 ou 2 : 0 = red ; 1 = blue ; 2 = random
        if color_choice == None:
            color_choice = 0
        if color_choice == 2: #choix couleur random
            color_choice = rd.randint(0,1)
        color = ['red', 'blue']

        self.size = size
        self.mat_plateau = np.zeros((size,size),dtype=int)

        self.player0 = Player(0, color.pop(color_choice), size)
        if is_PvBot:
            self.player1 = Bot(1, color.pop(), size, difficulty)
        else:
            self.player1 = Player(1, color.pop(), size)
        self.players = (self.player0, self.player1)

        self.create_mat_adjacence()

        self.turn = 0
        self.game_over = False

    def update_evaluation(self):
        min_pcc = min(self.player0.pcc[0], self.player0.pcc[0])
        # max_pcc = max(self.player0.max_pcc, self.player1.max_pcc)
        for player in self.players:
            # print('###############""')
            player.find_shortest_paths()
            np.mask_indices
            # print('1)', player.mat_points)
            grid_eval = min_pcc + 5 - player.mat_points
            # print('2)', grid_eval)
            grid_eval[grid_eval < 0] = 0
            # print(np.sum(grid_eval > 0))
            # print('3)', grid_eval)
            grid_eval = grid_eval**2
            score = np.sum(grid_eval)
            # print('score)', score)
            player.mat_points = grid_eval
            player.score = score


    def create_mat_adjacence(self):
        '''Fonction pour créer une matrice adjacence des joueurs
        Une matrice d'adjacence pour un plateau de 11x11 est une matrice symétrique de taille 121x121
        Chaque colonne et chaque ligne représente une case et leur intersection est un lien pondéré entre elles'''
        for player in self.players:
            for y in range(self.size**2):
                for x in range(y,self.size**2):
                    # on parcours la matrice du plateau de jeu de gauche a droite et haut en bas
                    x1, y1 = y%self.size, y//self.size 
                    x2, y2 = x%self.size, x//self.size
                    dx, dy = x1-x2, y1-y2
                    if y == x:
                        player.mat_adjacence[y][x] = 0
                        player.mat_adjacence[x][y] = 0
                    elif (dx == -1 and dy == -1) or (dx == 1 and dy == 1):
                        # on évite les cases qui se trouvent sur la diagonale non adjacente
                        continue
                    elif abs(dx) <= 1 and abs(dy) <= 1:
                        # on gère les connexions entre les cases "but" et les cases "non but"
                        if ((x1,y1) in player.game_borders) ^ ((x2,y2) in player.game_borders):
                            poid = 1.5
                        else:
                            poid = 1
                        
                        player.mat_adjacence[y][x] = poid
                        player.mat_adjacence[x][y] = poid
    
    def update_mat_plateau(self, x, y, player_n):
        '''Fonction qui gère l'ajout d'un pion sur le plateau'''
        player = self.players[player_n]
        other_player = self.players[(player_n+1)%2]
        self.mat_plateau[y][x] = player_n+1
        for y1 in range(-1,2):
            for x1 in range(-1,2):
                y2, x2 = y+y1, x+x1
                if (y1 == x1) or (y2 >= self.size) or (y2 < 0) or (x2 >= self.size) or (x2 < 0):
                    # on skip les cases inatteignables ou inexistantes
                    continue
                yp, xp = y*self.size + x, y2*self.size + x2 #calcul des coordonnées pour la matrice de poids
                value = self.mat_plateau[y2][x2]
                if value == 0:
                    if not ((x,y) in player.game_borders) and ((x2,y2) in player.game_borders):
                        poid = 1
                    else:
                        poid = 0.5
                elif value == player.id+1:
                    poid = 0
                else:
                    poid = np.inf
                player.mat_adjacence[yp][xp] = poid
                player.mat_adjacence[xp][yp] = poid
                other_player.mat_adjacence[yp][xp] = np.inf
                other_player.mat_adjacence[xp][yp] = np.inf
        self.turn += 1
        self.update_evaluation()
    
    def switch(self):
        self.player0.color, self.player1.color = self.player1.color, self.player0.color
        self.player0, self.player1 = self.player1, self.player0
        self.players = self.players[::-1]


    def dijkstra(self, x:int, y:int, player:Player|Bot):
        poids = {(i%self.size, i//self.size) : np.inf for i in range(self.size**2)}
        chemins = {(i%self.size, i//self.size) : None for i in range(self.size**2)}
        poids[(x,y)] = 0
        marqués = set([(x,y)])
        traités = set([])
        while len(marqués) != len(traités):
            x,y = min(marqués-traités, key=lambda i: poids[i])
            traités.add((x,y))
            for x1 in range(-1,2):
                for y1 in range(-1,2):
                    y2, x2 = y+y1, x+x1
                    if (y1 == x1) or (y2 >= self.size) or (y2 < 0) or (x2 >= self.size) or (x2 < 0):
                        continue
                    yp, xp = y*self.size + x, y2*self.size + x2
                    value = player.mat_adjacence[yp][xp]
                    if value != np.inf:
                        marqués.add((x2,y2))
                        if (longueur := value + poids[(x,y)]) < poids[(x2,y2)]:
                            poids[(x2,y2)] = longueur
                            chemins[(x2,y2)] = (x,y)

        
        return poids, chemins
    
PAD = 35
COLORS = ('red', 'blue')
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class MainTitle(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap("./icone.ico")
        self.title('Hex - Menu')
        self.width = 250
        self.height = 600
        self.toggle = True
        self.protocol("WM_DELETE_WINDOW", self.stop_all)
        self.center_window()

        image = Image.open("./hex3.jpg")  # ex: "image.jpg"
        image = image.resize((250, 120))  # redimensionner si nécessaire
        self.photo = ImageTk.PhotoImage(image)

        # Créer un label pour afficher l'image
        label_image = tk.Label(self, image=self.photo)
        label_image.pack()

        self.PvBot = tk.BooleanVar(value=False)
        self.Color = tk.IntVar(value=0)

        frame_mode = ttk.LabelFrame(self, text='Mode de jeu')
        frame_mode.pack(padx=10, pady=10, fill="x")
        
        frame_param = ttk.LabelFrame(self, text='Paramètres du jeu')
        frame_param.pack(padx=10, pady=10, fill="x")

        frame_launch = ttk.LabelFrame(self, text='Commencer la partie')
        frame_launch.pack(padx=10, pady=10, fill="x")

        self.frame_pvp = ttk.LabelFrame(frame_mode, text='Joueur vs Joueur')
        self.frame_pvp.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self.frame_pvp, text='Jouer à deux en local').grid(row=0, column=0, columnspan=2)

        self.frame_pvbot = ttk.LabelFrame(frame_mode, text='Joueur vs Bot')
        self.frame_pvbot.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.frame_pvbot, text='Couleur').grid(row=2,column=0,columnspan=2,sticky=tk.W)

        ttk.Radiobutton(self.frame_pvbot, variable=self.Color, value=0).grid(row=3,column=0,sticky=tk.W)
        ttk.Radiobutton(self.frame_pvbot, variable=self.Color, value=1).grid(row=4,column=0,sticky=tk.W)
        ttk.Radiobutton(self.frame_pvbot, variable=self.Color, value=2).grid(row=5,column=0,sticky=tk.W)

        tk.Label(self.frame_pvbot, text='Rouge').grid(row=3,column=1,sticky=tk.W)
        tk.Label(self.frame_pvbot, text='Bleu').grid(row=4,column=1,sticky=tk.W)
        tk.Label(self.frame_pvbot, text='Aléatoire').grid(row=5,column=1,sticky=tk.W)
        

        ttk.Radiobutton(frame_mode, variable=self.PvBot, value=False, command=lambda:self.toggle_widgets_mode(True)).grid(row=0, column=0, padx=10, pady=5)
        ttk.Radiobutton(frame_mode, variable=self.PvBot, value=True, command=lambda:self.toggle_widgets_mode(False)).grid(row=1, column=0, padx=10, pady=5)
        tk.Label(self.frame_pvbot, text='Difficulté').grid(row=0, column=0)

        self.slider_diff = tk.Scale(self.frame_pvbot, from_=1, to=10, orient='horizontal')
        self.slider_diff.set(5)
        self.slider_diff.grid(row=1,column=0,columnspan=2)

        tk.Label(frame_param, text='Taille plateau').grid(row=0, column=0, padx=10, pady=10)

        self.slider_taille = tk.Scale(frame_param, from_=6, to=16, orient='horizontal')
        self.slider_taille.set(11)
        self.slider_taille.grid(row=0,column=1, padx=10, pady=10)

        self.b_start = tk.Button(frame_launch,text='START',command=lambda:self.start(), bg='green')
        self.b_start.grid(row=0,column=0, padx=10, pady=10, sticky=tk.E+tk.W)

        self.b_stop = tk.Button(frame_launch,text='STOP',command=lambda:self.stop(), bg='grey', state='disabled')
        self.b_stop.grid(row=0,column=1, padx=10, pady=10, sticky=tk.E+tk.W)
        self.toggle_widgets_mode(True)
        self.resizable(False,False)

    def toggle_widgets_mode(self,var):
        if var:
            a,b = 'normal','disabled'
        else:
            a,b = 'disabled','normal'
        for widget in self.frame_pvbot.winfo_children():
            try:
                widget.configure(state=b)
            except:
                continue
        for widget in self.frame_pvp.winfo_children():
            try:
                widget.configure(state=a)
            except:
                continue

    def start(self):
        if len(App.running) == 0:
            if self.PvBot.get():
                root = App(size = self.slider_taille.get(),
                        isPvBot= True,
                        start_color= self.Color.get())
            else:
                root = App(size = self.slider_taille.get())
            self.b_start.configure(bg='grey', state='disabled')
            self.b_stop.configure(bg='red', state='normal')
            root.mainloop()
            
    def stop(self):
        if len(App.running) != 0:
            self.b_start.configure(bg='green', state='normal')
            self.b_stop.configure(bg='grey', state='disabled')
            App.running[0].terminate()
    
    def stop_all(self):
        self.stop()
        self.destroy()

    def center_window(self):
        h = self.winfo_screenheight()
        y = (h*3//8) - (self.height//2)
        self.geometry(f"{self.width}x{self.height}+{20}+{y}")

        


class App(tk.Tk):
    running = []
    def __init__(self, size:int, isPvBot:bool=False, start_color:int|None=None, difficulty:int|None=None):
        super().__init__()
        App.running.append(self)
        self.iconbitmap("./icone.ico")
        self.title('Hex - Game')
        self.game = Game(size, isPvBot, start_color, difficulty)
        self.window_width= 950
        self.width = 900
        self.height = 700
        self.resizable(False,False)
        self.center_window()
        
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=6)

        self.b_switch = tk.Button(self, text='Switch', command=self.switch, state='disabled', bg='grey')
        self.b_switch.grid(row=0,column=1, sticky="nsew")

        self.b_toggle_eval = tk.Button(self, text='Toggle Eval', command=self.toggle_eval)
        self.b_toggle_eval.grid(row=0, column=2, sticky="nsew")

        # self.canvas.create_text(self.width//7,PAD, text=f"Player 1: {self.game.player0.color}\nPlayer 2: {self.game.player1.color}", font='consolas 20', tag='player_info')
        self.canvas.create_text(self.width//7,self.height-PAD, text=f"Player 1: {self.game.player0.color}", font="consolas 20", tag='player1_info', fill=self.game.player0.color)
        self.canvas.create_text(self.width*6//7,self.height-PAD, text=f"Player 2: {self.game.player1.color}", font="consolas 20", tag='player2_info', fill=self.game.player1.color)

        self.canvas.create_text(self.width-PAD*5,PAD,text=f"PLAYER{self.game.players[self.game.turn%2].id+1}'S TURN", font=('consolas',20), fill=COLORS[self.game.turn%2], tag='turn_count')

        # self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<Motion>', self.move)
        self.canvas.bind('<Button-1>', self.click)

        self.draw_board(self.game.size)

        # empeche la fermeture avec la croix
        self.protocol("WM_DELETE_WINDOW", lambda:print('Veuillez fermer la fenêtre depuis le menu principal.'))
    
    def toggle_eval(self):
        pass

    def center_window(self):
        l = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        x = (l*3//5) - (self.window_width//2)
        y = (h*7//16) - (self.height//2)
        self.geometry(f"{self.window_width}x{self.height}+{x}+{y}")

    def terminate(self):
        App.running.remove(self)
        self.destroy()
    
    def move(self, event):
        x,y = event.x, event.y
        self.canvas.delete('cursor')
        if x > self.width or x < 0 or y > self.height or y < 0:
            return
        self.canvas.create_oval(x-7,y-7,x+7,y+7,fill=COLORS[self.game.turn%2], width=0, tag='cursor')

    def draw_hexagon(self, x,y,r,tag):
        points = [[x+cos(pi/6+i*pi/3)*r,y+sin(pi/6+i*pi/3)*r] for i in range(6)]
        self.canvas.create_polygon(points,fill='light grey',outline='black',width=2,tag=tag)
        if tag.split(':')[0] == str(0):
            for ligne in (points[1:3], points[2:4]):
                self.canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')
        if tag.split(':')[0] == str(self.game.size-1):
            for ligne in ([points[-1], points[0]],points[4:6]):
                self.canvas.create_line(ligne, fill='blue', width=5, tag='ignore2')
        if tag.split(':')[-1] == str(0):
            for ligne in (points[3:5], points[4:6]):
                self.canvas.create_line(ligne, fill='red', width=5, tag='ignore2')
        if tag.split(':')[-1] == str(self.game.size-1):
            for ligne in (points[1:3], points[0:2]):
                self.canvas.create_line(ligne, fill='red', width=5, tag='ignore2')

    def draw_board(self, n):
        spacing_x = (self.width-PAD*2)/(n+n/2)
        rad = spacing_x/sqrt(3)
        spacing_y = rad*sqrt(2)
        pad_y = ((self.height-PAD*2)-spacing_y*n)/2
        for y in range(n):
            for x in range(n):
                x1 = x*spacing_x+PAD+rad+y*spacing_x/2
                y1 = pad_y + y*spacing_y+PAD+rad

                

                self.draw_hexagon(x1,y1,rad,tag=f"{x}:{y}")

                # self.canvas.create_text(x1-rad/2-1,y1-1,text='0',fill='white', tag=f'text0_{x}:{y}', font='consolas 10')
                # self.canvas.create_text(x1+rad/2-1,y1-1,text='0',fill='white', tag=f'text1_{x}:{y}', font='consolas 10')
                # self.canvas.create_text(x1-rad/2,y1,text='0',fill='red', tag=f'text0_{x}:{y}', font='consolas 10')
                # self.canvas.create_text(x1+rad/2,y1,text='0',fill='blue', tag=f'text1_{x}:{y}', font='consolas 10')

                if x == 0:
                    self.canvas.create_text(x1-rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
                if x == n-1:
                    self.canvas.create_text(x1+rad*1.75,y1,text=str(y+1),font=('consolas',20),tag='ignore')
                if y == 0:
                    self.canvas.create_text(x1-rad,y1-rad*1.5,text=LETTERS[x],font=('consolas',20),tag='ignore')
                if y == n-1:
                    self.canvas.create_text(x1+rad,y1+rad*1.5,text=LETTERS[x],font=('consolas',20),tag='ignore')
        self.canvas.tag_lower('ignore')
        self.canvas.tag_raise('ignore2')

    def change_tile_color(self, x, y, color):
        self.canvas.itemconfig(f"{x}:{y}", fill=color)

    def get_tile(self, x, y) -> tuple|None:
        overlap = self.canvas.find_overlapping(x-1, y-1, x+1, y+1)
        if len(overlap) == 0:
            return None
        tags = [self.canvas.gettags(overlap[i])[0] for i in range(len(overlap))]
        tags = [i for i in tags if i not in ['ignore', 'ignore2']]
        if len(tags) == 0:
            return None
        tag = tags[0]
        if self.canvas.itemcget(tag,"fill") == 'light grey':
            # si la case n'est pas déjà occupée
            x,y = tag.split(':')
            return int(x), int(y)
        else:
            return None

    def click(self, event):
        if (res := self.get_tile(event.x, event.y)) == None or self.game.game_over:
            return
        x, y = res
        self.handle_tile_change(x, y)
    
    def switch(self):
        self.b_switch.configure(state='disabled', bg='grey', fg='black')
        self.game.switch()
        self.canvas.itemconfig('turn_count', text=f"PLAYER{self.game.players[self.game.turn%2].id+1}'S TURN")
        self.canvas.itemconfig("player1_info", text=f"Player 1: {self.game.player1.color}", fill=self.game.player1.color)
        self.canvas.itemconfig("player2_info", text=f"Player 2: {self.game.player0.color}", fill=self.game.player0.color)
    
    def display_pcc(self):
        n = self.game.size
        spacing_x = (self.width-PAD*2)/(n+n/2)
        rad = spacing_x/sqrt(3)
        spacing_y = rad*sqrt(2)
        pad_y = ((self.height-PAD*2)-spacing_y*n)/2
        self.canvas.delete('chemin')
        for player in self.game.players:
            chemin = player.pcc[1]
            for i in range(len(chemin)):
                x,y = chemin[i]
                x1 = x*spacing_x+PAD+rad+y*spacing_x/2
                y1 = pad_y + y*spacing_y+PAD+rad
                chemin[i] = (x1,y1)
            if chemin:
                self.canvas.create_line(chemin, fill='light grey', tag='chemin', width=8, smooth=True, capstyle='round')
                self.canvas.create_line(chemin, fill=player.color, tag='chemin', width=4, smooth=True, capstyle='round')
        
    def handle_tile_change(self, x, y):
        self.change_tile_color(x, y, COLORS[self.game.turn%2])
        self.game.update_mat_plateau(x,y, self.game.turn%2)
        self.display_pcc()
        # for player in self.game.players:
        #     for ya in range(self.game.size):
        #         for xa in range(self.game.size):
        #             try:
        #                 self.canvas.itemconfig(f'text{player.id}_{xa}:{ya}', text=str(int(player.mat_points[ya][xa])))
        #             except:
        #                 self.canvas.itemconfig(f'text{player.id}_{xa}:{ya}', text=str(-1))
        player1_percentage = self.game.player0.score/(self.game.player0.score+self.game.player1.score)
        print(f"player1\n{player1_percentage}\n{self.game.player0.color}\n")
        print(f"player2\n{1-player1_percentage}\n{self.game.player1.color}\n")
        xe, ye = self.width/2, self.height-50
        size_e = 150
        middle = size_e*player1_percentage
        if player1_percentage <= 1:
            self.canvas.delete('eval_bar')
            self.canvas.create_rectangle(xe-size_e/2,ye-15/2,xe-size_e/2+middle,ye+15,fill=self.game.player0.color,tag='eval_bar')
            self.canvas.create_rectangle(xe-size_e/2+middle,ye-15/2,xe+size_e/2,ye+15,fill=self.game.player1.color,tag='eval_bar')
        if self.game.turn == 1:
            self.b_switch.configure(state='normal', bg='blue', fg='white')
        elif self.game.turn == 2:
            self.b_switch.configure(state='disabled', bg='grey', fg='black')
        self.canvas.itemconfig('cursor', fill=COLORS[self.game.turn%2])
        self.canvas.itemconfig('turn_count', fill=COLORS[self.game.turn%2], text=f"PLAYER{self.game.players[self.game.turn%2].id+1}'S TURN")

        # if self.game.game_over:
        #     self.canvas.create_text(self.width/2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font="consolas 41 bold", fill='white')
        #     self.canvas.create_text(self.width/2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font=('consolas',40), fill=self.game.winner)



def main():
    main_title = MainTitle()
    main_title.mainloop()


if __name__ == '__main__':
    main()