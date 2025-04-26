# imports
from game import Game
from board import Board
from player import Player, Bot
from constants import MT_WIDTH, MT_HEIGHT

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class MainTitle(tk.Tk):
    '''Classe Maintitle, instance d'une fenêtre tkinter pour choisir les paramètres de jeu avant de lancer le jeu.
    Ces paramètres incluent :
    - Choix JcJ ou JcBot
    - Choix taille du plateau
    - Choix difficulté bot
    - Choix couleur de départ (Rouge, Bleu, Aléatoire)
    Cette fenêtre permet aussi de lancer le jeu et de l'arrêter, qu'une instance de jeu ne peut être lancée à la fois.'''
    def __init__(self):
        super().__init__()
        self.iconbitmap("./icone.ico")
        self.title('Hex - Menu')
        self.width = MT_WIDTH
        self.height = MT_HEIGHT
        self.toggle = True
        self.protocol("WM_DELETE_WINDOW", self.stop_all)
        self.center_window()

        image = Image.open("./hex.jpg")  # ex: "image.jpg"
        image = image.resize((250, 120))
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
        self.slider_diff.set(5) # difficulté par défaut à 5
        self.slider_diff.grid(row=1,column=0,columnspan=2)

        tk.Label(frame_param, text='Taille plateau').grid(row=0, column=0, padx=10, pady=10)

        self.slider_taille = tk.Scale(frame_param, from_=6, to=16, orient='horizontal')
        self.slider_taille.set(11) # taille du plateau par défaut à 11
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
        if len(Board.running) == 0:
            if self.PvBot.get():
                root = Board(size = self.slider_taille.get(),
                        isPvBot= True,
                        start_color= self.Color.get())
            else:
                root = Board(size = self.slider_taille.get())
            self.b_start.configure(bg='grey', state='disabled')
            self.b_stop.configure(bg='red', state='normal')
            root.mainloop()
            
    def stop(self):
        if len(Board.running) != 0:
            self.b_start.configure(bg='green', state='normal')
            self.b_stop.configure(bg='grey', state='disabled')
            Board.running[0].terminate()
    
    def stop_all(self):
        self.stop()
        self.destroy()

    def center_window(self):
        h = self.winfo_screenheight()
        y = (h*3//8) - (self.height//2)
        self.geometry(f"{self.width}x{self.height}+{20}+{y}")


if __name__ == '__main__':
    root = MainTitle()
    root.mainloop()