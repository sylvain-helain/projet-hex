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
        self.protocol("WM_DELETE_WINDOW", self.stop_all) #arrête toutes les instances de tkinter avant de fermer (avec la croix)
        self.center_window()

        # affiche l'image / logo du jeu dans l'écran d'acceuil
        image = Image.open("./hex.jpg")
        image = image.resize((250, 120))
        self.photo = ImageTk.PhotoImage(image)
        label_image = tk.Label(self, image=self.photo)
        label_image.pack()

        # création des variables utilisées dans les boutons / sliders
        self.PvBot = tk.BooleanVar(value=False)
        self.Color = tk.IntVar(value=0)

        # Frames pour organiser les boutons

        frame_mode = ttk.LabelFrame(self, text='Mode de jeu')
        frame_mode.pack(padx=10, pady=10, fill="x")
        
        frame_param = ttk.LabelFrame(self, text='Paramètres du jeu')
        frame_param.pack(padx=10, pady=10, fill="x")

        frame_launch = ttk.LabelFrame(self, text='Commencer la partie')
        frame_launch.pack(padx=10, pady=10, fill="x")

        # on place ces frames à l'intérieur du frame mode
        self.frame_pvp = ttk.LabelFrame(frame_mode, text='Joueur vs Joueur')
        self.frame_pvp.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self.frame_pvp, text='Jouer à deux en local').grid(row=0, column=0, columnspan=2)
        self.frame_pvbot = ttk.LabelFrame(frame_mode, text='Joueur vs Bot')
        self.frame_pvbot.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(self.frame_pvbot, text='Couleur').grid(row=2,column=0,columnspan=2,sticky=tk.W)

        # Radiobuttons pour le choix de la couleur du joueur humain (0:Rouge, 1:Bleu, 2:Aléatoire)
        ttk.Radiobutton(self.frame_pvbot, variable=self.Color, value=0).grid(row=3,column=0,sticky=tk.W)
        ttk.Radiobutton(self.frame_pvbot, variable=self.Color, value=1).grid(row=4,column=0,sticky=tk.W)
        ttk.Radiobutton(self.frame_pvbot, variable=self.Color, value=2).grid(row=5,column=0,sticky=tk.W)
        tk.Label(self.frame_pvbot, text='Rouge').grid(row=3,column=1,sticky=tk.W)
        tk.Label(self.frame_pvbot, text='Bleu').grid(row=4,column=1,sticky=tk.W)
        tk.Label(self.frame_pvbot, text='Aléatoire').grid(row=5,column=1,sticky=tk.W)
        
        # choix pour JcJ ou JcBot
        ttk.Radiobutton(frame_mode, variable=self.PvBot, value=False, command=lambda:self.toggle_widgets_mode(True)).grid(row=0, column=0, padx=10, pady=5)
        ttk.Radiobutton(frame_mode, variable=self.PvBot, value=True, command=lambda:self.toggle_widgets_mode(False)).grid(row=1, column=0, padx=10, pady=5)
        
        # Slider pour choix difficulté
        tk.Label(self.frame_pvbot, text='Difficulté').grid(row=0, column=0)
        self.slider_diff = tk.Scale(self.frame_pvbot, from_=1, to=10, orient='horizontal')
        self.slider_diff.set(5) # difficulté par défaut à 5
        self.slider_diff.grid(row=1,column=0,columnspan=2)

        # Slider pour choix taille du plateau
        tk.Label(frame_param, text='Taille plateau').grid(row=0, column=0, padx=10, pady=10)
        self.slider_taille = tk.Scale(frame_param, from_=6, to=16, orient='horizontal')
        self.slider_taille.set(11) # taille du plateau par défaut à 11
        self.slider_taille.grid(row=0,column=1, padx=10, pady=10)

        # boutons start et stop
        self.b_start = tk.Button(frame_launch,text='START',command=lambda:self.start(), bg='green')
        self.b_start.grid(row=0,column=0, padx=10, pady=10, sticky=tk.E+tk.W)
        self.b_stop = tk.Button(frame_launch,text='STOP',command=lambda:self.stop(), bg='grey', state='disabled')
        self.b_stop.grid(row=0,column=1, padx=10, pady=10, sticky=tk.E+tk.W)

        self.toggle_widgets_mode(True) 
        self.resizable(False,False)

    def toggle_widgets_mode(self,var):
        '''Cette fonction sert de switch pour faire en sorte que le contenu de la frame non sélectionnée soient grisés,
        La frame sélectionnée sera non grisée'''
        if var: # var = True : pour le mode JcJ
            a,b = 'normal','disabled'
        else: # var = False : pour le mode JcBot
            a,b = 'disabled','normal'
        for widget in self.frame_pvbot.winfo_children(): #JcBot
            try: # on met un try car certains éléments ne peuvent pas être disabled dans les frame et génèrent une erreur
                widget.configure(state=b)
            except:
                continue
        for widget in self.frame_pvp.winfo_children(): #JcJ
            try:
                widget.configure(state=a)
            except:
                continue

    def start(self):
        '''fonction attachée au bouton start, elle récupère toutes les variables utilisées par les différents boutons pour
        avoir tous les paramètres de jeu choisis et lance le jeu avec ainsi que la fenêtre d'affichage du plateau.'''
        if len(Board.running) == 0: # on vérifie avant qu'il n'y a pas d'autres instances de jeu en cours
            if self.PvBot.get(): # JcBot
                root = Board(size = self.slider_taille.get(),
                        isPvBot= True,
                        start_color= self.Color.get())
            else: # JcJ
                root = Board(size = self.slider_taille.get())

            self.b_start.configure(bg='grey', state='disabled') # désactive le bouton start
            self.b_stop.configure(bg='red', state='normal') # active le boton stop
            root.mainloop() # lance la fenêtre de jeu
            
    def stop(self):
        '''Fonction attachée au bouton stop, elle permet d'arrêter une partie en cours'''
        if len(Board.running) != 0: # si il y a une instance de jeu en cours
            self.b_start.configure(bg='green', state='normal') # active le bouton start
            self.b_stop.configure(bg='grey', state='disabled') # désactive le bouton stop
            Board.running[0].terminate() # arrêter la partie
    
    def stop_all(self):
        '''Fonction appellée lorsqu'on essaye de fermer la fenêtre avec la croix rouge de la fenêtre,
        permet de fermer toutes les fenêtres en même temps.'''
        self.stop() # arrête d'abord la fenêtre de jeu si il y en a une en cours
        self.destroy() # arrête son processus

    def center_window(self):
        '''Fonction pour corriger le placement de la fenêtre selon la résolution de l'écran'''
        h = self.winfo_screenheight()
        y = (h*3//8) - (self.height//2)
        self.geometry(f"{self.width}x{self.height}+{20}+{y}")


if __name__ == '__main__':
    root = MainTitle()
    root.mainloop()