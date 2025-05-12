from utils import get_cases_adj
import numpy as np


class Player(object):
    '''Instance d'un joueur, bot ou humain. Stockant toutes les variables et fonctions nécessaires pour calculer le plus court chemin
    d'un joueur.'''
    def __init__(self, id, n, mat):
        self.id = id
        self.opp_id = 1 if self.id == 2 else 2 # id de l'adversaire
        self.n = n
        self.mat = mat # on récupère la référence de la matrice de plateau du jeu
        self.color = 'red' if id==1 else 'blue'
        if id==1: # côtés à relier pour les rouges
            self.border1 = [(x,0) for x in range(n)]
            self.border2 = [(x,n-1) for x in range(n)]
        elif id==2: # bleu
            self.border1 = [(0,y) for y in range(n)]
            self.border2 = [(n-1,y) for y in range(n)]
        else:
            raise Exception('id incorrect: veuillez entrer 1 ou 2')
        self.borders = self.border1 + self.border2

    def get_shortest_path(self):
        '''Fonction plus longue que find_shortest_path length, pour pouvoir récupérer
        la liste contenant tous les points formant le pcc et un boolén indiquant si le joueur gagne ou non.
        Celle ci n'est utilisée que pour trouver le pcc afin de l'afficher dans l'interface.'''
        dict_adj = self.create_dict_adj() # dictionnaire d'adjacence utilisé dans Dijkstra (à la place de la matrice d'adjacence)
        min_value = np.inf
        path = []
        # on teste pour toutes les cases d'un côté vers toutes les cases de l'autre
        for x, y in self.border1:
            poids, chemins = self.dijkstra_path(dict_adj, x, y)
            val = min([poids[coo] for coo in self.border2]) # min sur les chemins menant aux cases du bord opposé
            if val < min_value:
                min_value = val
                x1,y1 = [key for key,value in poids.items() if value == min_value and key in self.border2][0]
                path = [(x1,y1)] # on update le chemin
                while (to_add := chemins[path[-1]]) != None:
                    path.append(to_add)
        if min_value == 0: # si le pcc == 0 alors le joueur a gagné
            win = True
        else:
            win = False
        return path, win
    
    def dijkstra_path(self, dict_adj:dict, x:int, y:int):
        '''Fonction dijkstra modifiéé pour aussi retourner un dictionnaire des chemins,
        on enregistre dans ce dictionnaire pour chaque case (clé) son prédecesseur (valeur)'''
        chemins = {(x1, y1) : None for x1 in range(self.n) for y1 in range(self.n)}
        poids = {(x1, y1) : np.inf for x1 in range(self.n) for y1 in range(self.n)}
        poids[(x,y)] = 0
        marqués = set([(x,y)])
        traités = set([])
        while len(marqués) != len(traités):
            x,y = min(marqués-traités, key=lambda i: poids[i])
            traités.add((x,y))
            
            for value, x1, y1 in dict_adj[(x,y)]:
                marqués.add((x1,y1))
                if (longueur := value + poids[(x,y)]) < poids[(x1,y1)]:
                    poids[(x1,y1)] = longueur
                    chemins[(x1,y1)] = (x,y)
        return poids, chemins


    def find_shortest_path_length(self):
        '''Fonction optimisée, utilisée pour minimax dans la fonction d'évaluation, on ne calcule pas les prédecesseurs des chemins
        pour améliorer la rapidité des choix de l'ia. On retourne la longeur du plus court chemin du joueur.'''
        dict_adj = self.create_dict_adj()
        min_value = np.inf
        for x, y in self.border1:
            poids = self.dijkstra(dict_adj, x, y)
            min_value = min(min_value, min([poids[coo] for coo in self.border2]))
        return min_value
    
    def dijkstra(self, dict_adj:dict, x:int, y:int):
        '''Algorithme de dijkstra, on a modifié la matrice d'adjacence pour un dictionnaire d'adjacence car dans notre
        plateau / "matrice", chaque case est reliée à un petit nombre de cases adjacentes (6 max). Dans ce cas,
        une matrice d'adjacence fera (pour un plateau de 11x11) 121x121 cases alors que chaque ligne (121 cases)
        ne stockera que 6 cases utiles au maximum. Un dictionnaire sera plus efficace pour des plateaux de grandes tailles.'''
        poids = {(x, y) : np.inf for x in range(self.n) for y in range(self.n)}
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
    
    def create_dict_adj(self) -> dict:
        '''Création du dictionnaire d'adjacence remplacant la matrice d'adjacence utilisée dans Dijkstra.
        - Une distance entre deux cases vides est de 1, 
        - Si une des cases est colorée par le joueur : la distance est de 0.5,
        - Si les deux cases sont colorées par le joueur : la distance est de 0,
        - Si au moins une des deux cases sont colorées par l'adversaire : la distance est de inf.
        On doit gérer différement les liens entre les cases d'un côté "but" et les cases non "but", leur distance sera incrémentée
        de 0.5 si la case présente sur le bord n'est pas colorée.'''
        res = {(x,y):list() for x in range(self.n) for y in range(self.n)}
        for y1 in range(self.n):
            for x1 in range(self.n):
                for x2, y2 in get_cases_adj(x1,y1,self.n):
                    case1, case2 = self.mat[y1][x1], self.mat[y2][x2]
                    if case1 == self.opp_id or case2 == self.opp_id: # si au moins une des deux cases est colorée par l'adversaire
                        continue
                    is_c1_border, is_c2_border = (x1,y1) in self.borders, (x2,y2) in self.borders
                    if case1 == self.id and case2 == self.id: # si les deux cases sont colorées
                        value = 0.0
                    elif is_c1_border and is_c2_border: # si les deux cases sont sur un bord
                        value = 1.5
                    elif is_c1_border: # si seulement case1 est sur un bord
                        if case1 == self.id and case2 == 0:
                            value = 0.5
                        elif case1 == 0 and case2 == self.id:
                            value = 1.0
                        else:
                            value = 1.5
                    elif is_c2_border: # si seulement case2 est sur un bord
                        if case2 == self.id and case1 == 0:
                            value = 0.5
                        elif case2 == 0 and case1 == self.id:
                            value = 1.0
                        else:
                            value = 1.5
                    # si case1 et case2 ne sont pas sur un bord et l'une d'entre elle est colorée
                    elif case1==self.id or case2==self.id: 
                        value = 0.5
                    else: # si elles sont toutes les deux vides
                        value = 1.0
                    
                    res[(x1,y1)].append([value,x2,y2])

        return res
