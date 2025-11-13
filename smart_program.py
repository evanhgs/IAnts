import random
import time
import threading
from univers import Map, Point, Nest, Food, Trap, Wall, Pheromone, AntCategory

class SimulationController:
    """
    Endpoint entre la GUI et le moteur logique.
    """
    def __init__(self):
        self.running = False
        self.paused = True
        self.speed = 1.0
        self.world = None
        self.pheromone = None
        self.ants = []
        self.lock = threading.Lock()

    def configure_world(self, width=60, height=40, food_sources=5, traps=5, walls=100):
        """Initialise la map."""
        self.world = Map(width, height)
        self.world.nest = Nest(Point(width // 2, height // 2))
        # murs
        for _ in range(walls):
            self.world.walls.append(Wall(Point(random.randint(0, width - 1), random.randint(0, height - 1))))
        # nourriture
        for _ in range(food_sources):
            self.world.foods.append(Food(Point(random.randint(0, width - 1), random.randint(0, height - 1)), 10000))
        # pièges
        for _ in range(traps):
            self.world.traps.append(Trap(Point(random.randint(0, width - 1), random.randint(0, height - 1))))
        self.pheromone = Pheromone(self.world)
        self.ants.clear()
        for _ in range(6):
            self.ants.append(AntCategory.exploratrice(self.world.nest.pos))
        for _ in range(6):
            self.ants.append(AntCategory.recolteuse(self.world.nest.pos))
        for _ in range(2):
            self.ants.append(AntCategory.combattante(self.world.nest.pos))

    def toggle_pause(self):
        with self.lock:
            self.paused = not self.paused

    def set_speed(self, s):
        with self.lock:
            self.speed = max(0.1, min(s, 10))

    def reset(self):
        with self.lock:
            self.running = False
            self.paused = True
            self.world = None
            self.ants.clear()

    def step(self):
        """Un tick logique simple (sans Q-learning ici)."""
        if not self.world:
            return
        for ant in self.ants:
            ant.tick(1)
            if ant.can_move():
                dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                np = Point(ant.position.x + dx, ant.position.y + dy).clamp(self.world.width, self.world.height)
                if not self.world.is_wall(np) and not self.world.is_trap(np):
                    ant.position = np
                ant.start_move_cooldown()
        self.world.decay_pheromones()

    def run(self):
        """Boucle moteur (thread séparé)."""
        self.running = True
        while self.running:
            with self.lock:
                if not self.paused and self.world:
                    self.step()
            time.sleep(1.0 / self.speed)
