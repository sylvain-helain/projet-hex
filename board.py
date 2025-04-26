import tkinter as tk
from game import Game
from math import sin, cos, sqrt, pi
from constants import B_WIDTH, B_HEIGHT, PAD, COLORS, LETTERS

class Board(tk.Tk):
    running = []
    def __init__(self, size:int, isPvBot:bool=False, start_color:int|None=None, difficulty:int|None=None):
        super().__init__()
        Board.running.append(self)
        self.iconbitmap("./icone.ico")
        self.title('Hex - Game')
        self.game = Game(size, isPvBot, start_color, difficulty)
        self.window_width= 950
        self.width = B_WIDTH
        self.height = B_HEIGHT
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
        Board.running.remove(self)
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
    
    def update_eval_bar(self):
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


    def handle_tile_change(self, x, y):
        self.change_tile_color(x, y, COLORS[self.game.turn%2])
        self.game.update_mat_plateau(x,y, self.game.turn%2)
        self.display_pcc()
        self.update_eval_bar()
        if self.game.turn == 1:
            self.b_switch.configure(state='normal', bg='blue', fg='white')
        elif self.game.turn == 2:
            self.b_switch.configure(state='disabled', bg='grey', fg='black')
        self.canvas.itemconfig('cursor', fill=COLORS[self.game.turn%2])
        self.canvas.itemconfig('turn_count', fill=COLORS[self.game.turn%2], text=f"PLAYER{self.game.players[self.game.turn%2].id+1}'S TURN")

        # if self.game.game_over:
        #     self.canvas.create_text(self.width/2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font="consolas 41 bold", fill='white')
        #     self.canvas.create_text(self.width/2,self.height/2, text=f'PLAYER {self.game.winner.upper()} WINS!', font=('consolas',40), fill=self.game.winner)

