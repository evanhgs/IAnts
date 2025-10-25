from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

@dataclass(frozen=True) # le param frozen sert a rendre les points immutables et leve une erreur si ils changent, pratique pour les logs
class Point:
    x: int
    y: int
    def clamp(self, w: int, h: int) -> "Point":
        cx = max(0, min(self.x, w -1 ))
        cy = max(0, min(self.y, h -1 ))
        return Point(cx, cy)


class Time:
    """Gestion simple du temps de la simulation."""
    def __init__(self, start: int = 0, end: int = 1_000_000_000):
        self.start = start
        self.end = end
        self.current = start

    def tick(self, dt: int = 1):
        self.current += dt

class Movement:
    """
    Représente la vitesse / comportement de déplacement.
    velocity: nombre d'unités de déplacement par case (M) en unité de temps (S)
    Ici on stocke ticks_per_move combien d'unités de temps pour faire 1 case
    """
    DIR_R = (1, 0)
    DIR_L = (-1, 0)
    DIR_U = (0, -1)
    DIR_D = (0, 1)
    DIR_NONE = (0, 0)

    def __init__(self, ticks_per_move: int = 5):
        if ticks_per_move <= 0:
            raise ValueError("ticks_per_move must be > 0")
        self.ticks_per_move = ticks_per_move

class Fov:
    # Un champs de vision, nombre de case qu’elles peuvent voir (détecter les objets)
    def __init__(self, radius):
        if radius < 0:
            raise ValueError('fov value must be >= 0')
        self.radius = radius


class MapObject:
    """Base class for objects"""
    def __init__(self, pos: Point):
        self.pos = pos


class Wall(MapObject):
    """infrachissable"""
    pass


class Trap(MapObject):
    pass


class Food(MapObject):
    """Source de nourriture"""
    def __init__(self, pos: Point, qte: int):
        super().__init__(pos)
        if qte < 0:
            raise ValueError("qte must be >= 0")
        self.qte = qte


class Nest(MapObject):
    """Le nid : stocke de la nourriture, nombre de fourmis prêtes à sortir, etc."""
    def __init__(self, pos: Point, capacity_outside: int = 10):
        super().__init__(pos)
        self.capacity_outside = capacity_outside
        self.food_stored = 0

class Map:
    """
    Contient walls, traps, foods, nest
    """
    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive integers")
        self.width = width
        self.height = height
        self.walls: List[Wall] = []
        self.traps: List[Trap] = []
        self.foods: List[Food] = []
        self.nest: Nest

        # Q-tables / phéromones : deux cartes (vers nourriture, vers nid)
        # On utilise dictionnaires (Point -> value) pour stocker uniquement cases non nulles
        self.pheromone_to_food: Dict[Point, float] = {}
        self.pheromone_to_nest: Dict[Point, float] = {}

    def in_bounds(self, p: Point) -> bool:
        return 0 <= p.x < self.width and 0 <= p.y < self.height

    def is_wall(self, p: Point) -> bool:
        return any(w.pos == p for w in self.walls)

    def is_trap(self, p: Point) -> bool:
        return any(t.pos == p for t in self.traps)

    def get_food_at(self, p: Point) -> Optional[Food]:
        for f in self.foods:
            if f.pos == p:
                return f
        return None

    def decay_pheromones(self, decay_rate: float = 0.01):
        """
        Appliquer la dissipation d'1% par tour
        """
        def apply_decay(d):
            to_delete = []
            for pos, val in d.items():
                new_val = val * (1 - decay_rate)
                if abs(new_val) < 1e-6:
                    to_delete.append(pos)
                else:
                    d[pos] = new_val
            for pos in to_delete:
                del d[pos]

        apply_decay(self.pheromone_to_food)
        apply_decay(self.pheromone_to_nest)

class QParams:
    def __init__(self, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon


class Ant:
    def __init__(
            self,
            pos: Point,
            ticks_per_move: int,
            fov_radius: int,
            food_max_load: int,
            category: str = "generic",
            qparams: Optional[QParams] = None
    ):
        self.position: Point = pos
        self.movement: Movement = Movement(ticks_per_move)
        self.fov: Fov = Fov(fov_radius)
        self.food_max_load: int = food_max_load
        self.food_load: int = 0
        self.category: str = category
        self.qparams: QParams = qparams or QParams()
        self._ticks_until_move = 0 # internal timing: ticks until next allowed move


    def can_move(self) -> bool:
        return self._ticks_until_move <= 0

    def start_move_cooldown(self):
        self._ticks_until_move = self.movement.ticks_per_move

    def tick(self, dt: int = 1):
        self._ticks_until_move = max(0, self._ticks_until_move - dt) # appeler t pour decrmenter le cooldown

    def pick_food(self, amount: int) -> int:
        space = self.food_max_load - self.food_load
        taken = max(0, min(space, amount))
        self.food_load += taken
        return taken

    def drop_all(self) -> int:
        q = self.food_load
        self.food_load = 0
        return q

class AntState(Enum):
    SEARCHING_FOOD = 1
    RETURNING_NEST = 2

class AntMod(Ant):
    def __init__(
            self,
            pos: Point,
            ticks_per_move: int,
            fov_radius: int,
            food_max_load: int,
            category: str = "new born"
    ):
        super().__init__(
            pos,
            ticks_per_move,
            fov_radius,
            food_max_load,
            category
        )
        self.state: AntState = AntState.SEARCHING_FOOD if self.food_load == 0 else AntState.RETURNING_NEST

    def update_state(self):
        if self.food_load == 0:
            self.state = AntState.SEARCHING_FOOD
        else:
            self.state = AntState.RETURNING_NEST


class AntCategory(Ant):

    @staticmethod
    def exploratrice(pos: Point) -> AntMod:
        return AntMod(pos=pos, ticks_per_move=5, fov_radius=1, food_max_load=10, category="exploratrice")

    @staticmethod
    def combattante(pos: Point) -> AntMod:
        return AntMod(pos=pos, ticks_per_move=5, fov_radius=1, food_max_load=10, category="combattante")

    @staticmethod
    def recolteuse(pos: Point) -> AntMod:
        return AntMod(pos=pos, ticks_per_move=10, fov_radius=0, food_max_load=100, category="recolteuse")


class Pheromone:
    """
    Gestion simplifiée des contributions de Q-learning (phéromones) :
    On stocke modifications temporaires pendant un tour, puis on applique la somme
    dissipation déjà gérée par Map.decay_pheromones
    """
    REWARD_FOOD = 1000.0
    REWARD_NEST = 1000.0
    REWARD_TRAP = -100.0
    REWARD_OTHER = -1.0

    def __init__(self, world: Map):
        self.world = world
        self.delta_food: Dict[Point, float] = {} # logs des maj des pos
        self.delta_nest: Dict[Point, float] = {}

    def add_delta(self, pos: Point, amount: float, towards: str = "food"):
        """Ajouter une modification (positive ou négative) pour la case pos."""
        if not self.world.in_bounds(pos):
            return
        if towards == "food":
            self.delta_food[pos] = self.delta_food.get(pos, 0.0) + amount
        else:
            self.delta_nest[pos] = self.delta_nest.get(pos, 0.0) + amount

    def flush(self):
        """Appliquer les deltas accumulés sur les cartes de phéromones du map."""
        for pos, val in self.delta_food.items():
            self.world.pheromone_to_food[pos] = self.world.pheromone_to_food.get(pos, 0.0) + val
        for pos, val in self.delta_nest.items():
            self.world.pheromone_to_nest[pos] = self.world.pheromone_to_nest.get(pos, 0.0) + val
        self.delta_food.clear()
        self.delta_nest.clear()