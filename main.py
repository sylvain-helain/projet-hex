# imports
# from game import Game
from board import BoardApp
# from player import Player, BotPlayer
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
        try:
            self.iconbitmap("./icone.ico")
        except: # bug parfois sur un environnement linux
            pass
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
        self.p1_bot = tk.BooleanVar(value=False)
        self.p2_bot = tk.BooleanVar(value=False)

        self.diff_p1 = tk.IntVar(value=2)
        self.diff_p2 = tk.IntVar(value=2)

        # Frames pour organiser les boutons

        frame_mode = ttk.LabelFrame(self, text='Mode de jeu')
        frame_mode.pack(padx=10, pady=10, fill="x")
        
        frame_param = ttk.LabelFrame(self, text='Paramètres du jeu')
        frame_param.pack(padx=10, pady=10, fill="x")

        frame_launch = ttk.LabelFrame(self, text='Commencer la partie')
        frame_launch.pack(padx=10, pady=10, fill="x")

        # on place ces frames à l'intérieur du frame mode
        self.frame_p1 = ttk.LabelFrame(frame_mode, text='Joueur 1 (rouge)')
        self.frame_p1.grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.frame_p1, text='Humain').grid(row=0, column=1, columnspan=1, sticky=tk.W)
        tk.Label(self.frame_p1, text='Bot').grid(row=1, column=1, columnspan=1, sticky=tk.W)
        self.frame_p2 = ttk.LabelFrame(frame_mode, text='Joueur 2 (bleu)')
        self.frame_p2.grid(row=1, column=0, padx=10, pady=10)
        # tk.Label(self.frame_p2, text='Couleur').grid(row=2,column=0,columnspan=2,sticky=tk.W)

        tk.Label(self.frame_p2, text='Humain').grid(row=0, column=1, columnspan=1, sticky=tk.W)
        tk.Label(self.frame_p2, text='Bot').grid(row=1, column=1, columnspan=1, sticky=tk.W)


        # Radiobuttons pour le choix de la couleur du joueur humain (0:Rouge, 1:Bleu, 2:Aléatoire)
        ttk.Radiobutton(self.frame_p1, variable=self.p1_bot, value=False, command=self.show_p1_bot_diff).grid(row=0,column=0,sticky=tk.W)
        ttk.Radiobutton(self.frame_p1, variable=self.p1_bot, value=True, command=self.show_p1_bot_diff).grid(row=1,column=0,sticky=tk.W)

        ttk.Radiobutton(self.frame_p2, variable=self.p2_bot, value=False, command=self.show_p2_bot_diff).grid(row=0,column=0,sticky=tk.W)
        ttk.Radiobutton(self.frame_p2, variable=self.p2_bot, value=True, command=self.show_p2_bot_diff).grid(row=1,column=0,sticky=tk.W)
    
        
        # Slider pour choix difficulté
        self.diff_p1_label = tk.Label(self.frame_p1, text='Difficulté')
        self.slider_diff_p1 = tk.Scale(self.frame_p1, from_=1, to=5, orient='horizontal')
        self.slider_diff_p1.set(2) # difficulté par défaut à 5

        self.diff_p2_label = tk.Label(self.frame_p2, text='Difficulté')
        self.slider_diff_p2 = tk.Scale(self.frame_p2, from_=1, to=5, orient='horizontal')
        self.slider_diff_p2.set(2) # difficulté par défaut à 5


        # Slider pour choix taille du plateau
        tk.Label(frame_param, text='Taille plateau').grid(row=0, column=0, padx=10, pady=10)
        self.slider_taille = tk.Scale(frame_param, from_=5, to=16, orient='horizontal')
        self.slider_taille.set(11) # taille du plateau par défaut à 11
        self.slider_taille.grid(row=0,column=1, padx=10, pady=10)

        # boutons start et stop
        self.b_start = tk.Button(frame_launch,text='START',command=lambda:self.start(), bg='green')
        self.b_start.grid(row=0,column=0, padx=10, pady=10, sticky=tk.E+tk.W)
        self.b_stop = tk.Button(frame_launch,text='STOP',command=lambda:self.stop(), bg='grey', state='disabled')
        self.b_stop.grid(row=0,column=1, padx=10, pady=10, sticky=tk.E+tk.W)

        self.resizable(False,False)


    def show_p1_bot_diff(self):
        if self.p1_bot.get():
            self.diff_p1_label.grid(row=2, column=0, columnspan=2)
            self.slider_diff_p1.grid(row=3, column=0, columnspan=2)
        else:
            self.diff_p1_label.grid_forget()
            self.slider_diff_p1.grid_forget()

    def show_p2_bot_diff(self):
        if self.p2_bot.get():
            self.diff_p2_label.grid(row=2, column=0, columnspan=2)
            self.slider_diff_p2.grid(row=3, column=0, columnspan=2)
        else:
            self.diff_p2_label.grid_forget()
            self.slider_diff_p2.grid_forget()
        

    def start(self):
        '''fonction attachée au bouton start, elle récupère toutes les variables utilisées par les différents boutons pour
        avoir tous les paramètres de jeu choisis et lance le jeu avec ainsi que la fenêtre d'affichage du plateau.'''
        if len(BoardApp.running) == 0: # on vérifie avant qu'il n'y a pas d'autres instances de jeu en cours
            root = BoardApp(self.slider_taille.get(), self.p1_bot.get(), self.p2_bot.get(), self.slider_diff_p1.get(), self.slider_diff_p2.get())
            self.b_start.configure(bg='grey', state='disabled') # désactive le bouton start
            self.b_stop.configure(bg='red', state='normal') # active le boton stop
            root.mainloop() # lance la fenêtre de jeu
            
    def stop(self):
        '''Fonction attachée au bouton stop, elle permet d'arrêter une partie en cours'''
        if len(BoardApp.running) != 0: # si il y a une instance de jeu en cours
            self.b_start.configure(bg='green', state='normal') # active le bouton start
            self.b_stop.configure(bg='grey', state='disabled') # désactive le bouton stop
            BoardApp.running[0].terminate() # arrêter la partie
    
    def stop_all(self):
        '''Fonction appellée lorsqu'on essaye de fermer la fenêtre avec la croix rouge de la fenêtre,
        permet de fermer toutes les fenêtres en même temps.'''
        self.stop() # arrête d'abord la fenêtre de jeu si il y en a une en cours
        self.destroy() # arrête son processus

    def center_window(self):
        '''Fonction pour corriger le placement de la fenêtre selon la résolution de l'écran'''
        h = self.winfo_screenheight()
        y = (h*2//5) - (self.height//2)
        self.geometry(f"{self.width}x{self.height}+{20}+{y}")


if __name__ == '__main__':
    root = MainTitle()
    root.mainloop()