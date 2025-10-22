class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.nest_pos = Nest
        self.trap = Trap
        self.wall = Wall

class Wall:
    def __init__(self, pos):
        self.pos = pos

class Trap:
    def __init__(self, width, height, pos):
        self.width = width
        self.height = height
        self.position = pos

class Time:
    def __init__(self):
        self.start = 0
        self.end = 100.000
        self.unity = "s"

class Nest:
    def __init__(self, pos):
        self.position = pos


class Food:
    def __init__(self, pos, qte):
        self.position = pos
        self.qte = qte

class Fov:
    # Un champs de vision, nombre de case qu’elles peuvent voir (détecter les objets)
    def __init__(self):
        self.fov = 1

class Movement:
    # Une vitesse de déplacement (nombre d’unité de déplacement par case(M) en unité de temps(S) )
    def __init__(self, pos, vel):
        self.pos = pos
        self.vel = vel
        self.directionR = 1, 0
        self.directionL = -1, 0
        self.directionU = 0, 1
        self.directionD = 0, -1
        self.directionN = 0

class Categorie:
    def __init__(self):
        self.categories = []

    def Exploratrice(self):
        return
    def Combattante(self):
        return
    def Recolteuse(self):
        return


class Ant:
    def __init__(self, pos, velocity, fov, food_max_load, ):
        self.position = pos
        self.velocity = velocity
        self.fov = fov
        self.food_max_load = food_max_load