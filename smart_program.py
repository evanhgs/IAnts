import random
import time
import threading
from univers import Map, Point, Nest, Food, Trap, Wall, Pheromone, AntCategory

class SimulationController:
    """
    Endpoint entre la GUI et le moteur logique.
    """
    def __init__(self, custom_speed: float):
        print(f"[SimulationController] __init__ speed={custom_speed}")
        self.running = False
        self.paused = False
        self.speed = custom_speed
        self.world = None
        self.pheromone = None
        self.ants = []
        self.lock = threading.Lock()

    def configure_world(self, width:int, height:int, food_sources:int, traps:int, walls:int, nb_ant_explo:int, nb_ant_recol:int, nb_ant_comba:int):
        """default value ex: 128, 64, 10, 20, 100, 6, 6, 2"""
        print(f"[configure_world] Starting configuration: {width}x{height}, foods={food_sources}, traps={traps}, walls={walls}, ants(explo/recol/comba)={nb_ant_explo}/{nb_ant_recol}/{nb_ant_comba}")
        self.world = Map(width, height)
        self.world.nest = Nest(Point(width // 2, height // 2))
        print(f"[configure_world] Nest placed at {self.world.nest.pos}")

        self.world.walls.clear()
        for i in range(walls):
            p = Point(random.randint(0, width -1), random.randint(0, height -1))
            self.world.walls.append(Wall(p))
            if i < walls:
                print(f"[configure_world] Wall #{i} at {p}")
        print(f"[configure_world] ... total walls = {walls}")

        self.world.foods.clear()
        for i in range(food_sources):
            p = Point(random.randint(0, width - 1), random.randint(0, height - 1))
            self.world.foods.append(Food(p, 10000))
            print(f"[configure_world] Food #{i} at {p} (qty=10000)")

        self.world.traps.clear()
        for i in range(traps):
            p = Point(random.randint(0, width - 1), random.randint(0, height - 1))
            self.world.traps.append(Trap(p))
            print(f"[configure_world] Trap #{i} at {p}")

        self.pheromone = Pheromone(self.world)
        print(f"[configure_world] Pheromone system initialized")

        self.ants.clear()
        for i in range(nb_ant_explo):
            ant = AntCategory.exploratrice(self.world.nest.pos)
            self.ants.append(ant)
            print(f"[configure_world] Exploratrice #{i} created at {ant.position}")
        for i in range(nb_ant_recol):
            ant = AntCategory.recolteuse(self.world.nest.pos)
            self.ants.append(ant)
            print(f"[configure_world] Recolteuse #{i} created at {ant.position}")
        for i in range(nb_ant_comba):
            ant = AntCategory.combattante(self.world.nest.pos)
            self.ants.append(ant)
            print(f"[configure_world] Combattante #{i} created at {ant.position}")

        print(f"[configure_world] World configured: ants={len(self.ants)}, walls={len(self.world.walls)}, foods={len(self.world.foods)}, traps={len(self.world.traps)}")

    def toggle_pause(self):
        with self.lock:
            self.paused = not self.paused
            print(f"[toggle_pause] paused -> {self.paused}")

    def set_speed(self, s):
        with self.lock:
            old = self.speed
            self.speed = max(0.1, min(s, 1000000))
            print(f"[set_speed] speed changed from {old} to {self.speed}")

    def reset(self):
        with self.lock:
            print("[reset] Resetting simulation state")
            self.running = False
            self.paused = True
            self.world = None
            self.ants.clear()
            self.pheromone = None
            print("[reset] Reset complete")

    def step(self):
        """TODO: QLEARNING de qualité française"""
        if not self.world:
            print("[step] No world configured, skipping step")
            return
        print(f"[step] Starting step with {len(self.ants)} ants")
        for idx, ant in enumerate(self.ants):
            try:
                print(f"[step][ant #{idx}] before tick: pos={ant.position}, moving_cooldown={getattr(ant, 'moving_cooldown', 'N/A')}")
                ant.tick(1)
                print(f"[step][ant #{idx}] after tick: pos={ant.position}")
                if ant.can_move():
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    print(f"[step][ant #{idx}] can_move -> chosen delta=({dx},{dy})")
                    np = Point(ant.position.x + dx, ant.position.y + dy).clamp(self.world.width, self.world.height)
                    if np.x != ant.position.x + dx or np.y != ant.position.y + dy:
                        print(f"[step][ant #{idx}] clamped to {np}")
                    if self.world.is_wall(np):
                        print(f"[step][ant #{idx}] blocked by wall at {np}")
                    elif self.world.is_trap(np):
                        print(f"[step][ant #{idx}] would enter trap at {np} -> move cancelled")
                    else:
                        ant.position = np
                        print(f"[step][ant #{idx}] moved to {ant.position}")
                    ant.start_move_cooldown()
                    print(f"[step][ant #{idx}] started move cooldown")
                else:
                    print(f"[step][ant #{idx}] cannot move this tick")
            except Exception as e:
                print(f"[step][ant #{idx}] Exception during step: {e}")

        try:
            self.world.decay_pheromones()
            print("[step] pheromones decayed")
        except Exception as e:
            print(f"[step] Exception while decaying pheromones: {e}")

    def run(self):
        """Boucle moteur thread séparé"""
        print("[run] Engine thread starting")
        self.running = True
        while self.running:
            with self.lock:
                if not self.paused and self.world:
                    print("[run] stepping engine (not paused)")
                    self.step()
                else:
                    if self.paused:
                        print("[run] engine paused")
                    else:
                        print("[run] no world configured")
            sleep_time = 1.0 / max(0.1, self.speed)
            print(f"[run] sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        print("[run] Engine thread exiting")
