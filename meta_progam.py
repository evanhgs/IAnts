import pygame
import threading
from smart_program import SimulationController

pygame.init()
FONT = pygame.font.Font(None, 24)
CELL = 16

class MetaProgram:
    def __init__(self):
        self.controller = SimulationController()
        self.controller.configure_world()
        self.thread = threading.Thread(target=self.controller.run, daemon=True)
        self.thread.start()

        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("AiFAnts - Meta Program")
        self.clock = pygame.time.Clock()
        self.running = True

        # Config par défaut
        self.config = {
            "width": 60,
            "height": 40,
            "food_sources": 5,
            "traps": 5,
            "walls": 100,
        }

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.controller.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.controller.toggle_pause()
                elif event.key == pygame.K_RETURN:
                    self.controller.configure_world(**self.config)
                elif event.key == pygame.K_UP:
                    self.controller.set_speed(self.controller.speed + 0.5)
                elif event.key == pygame.K_DOWN:
                    self.controller.set_speed(self.controller.speed - 0.5)

    def draw_grid(self, world):
        for x in range(world.width):
            for y in range(world.height):
                rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
                pygame.draw.rect(self.screen, (40, 40, 60), rect, 1)

    def draw_world(self, world):
        if not world:
            return
        # fond
        self.screen.fill((25, 25, 40))
        # murs
        for w in world.walls:
            pygame.draw.rect(self.screen, (120, 120, 120),
                             (w.pos.x * CELL, w.pos.y * CELL, CELL, CELL))
        # pièges
        for t in world.traps:
            pygame.draw.rect(self.screen, (200, 50, 50),
                             (t.pos.x * CELL, t.pos.y * CELL, CELL, CELL))
        # nourriture
        for f in world.foods:
            pygame.draw.rect(self.screen, (50, 200, 50),
                             (f.pos.x * CELL, f.pos.y * CELL, CELL, CELL))
        # nid
        if world.nest:
            pygame.draw.rect(self.screen, (255, 220, 60),
                             (world.nest.pos.x * CELL, world.nest.pos.y * CELL, CELL, CELL))
        # fourmis
        for a in self.controller.ants:
            color = (200, 200, 255) if a.category == "exploratrice" else \
                    (255, 120, 60) if a.category == "recolteuse" else \
                    (255, 50, 50)
            pygame.draw.circle(self.screen, color,
                               (a.position.x * CELL + CELL//2, a.position.y * CELL + CELL//2), 4)

    def draw_panel(self):
        panel_x = self.controller.world.width * CELL + 10
        y = 20
        def line(text, color=(255, 255, 255)):
            nonlocal y
            surf = FONT.render(text, True, color)
            self.screen.blit(surf, (panel_x, y))
            y += 26

        line("=== META CONFIG ===", (255, 200, 80))
        line(f"[SPACE] Pause/Play")
        line(f"[ENTER] Reconfigurer")
        line(f"[↑/↓] Vitesse ({self.controller.speed:.1f}x)")
        line("")
        line(f"Taille : {self.config['width']}x{self.config['height']}")
        line(f"Nourriture : {self.config['food_sources']}")
        line(f"Pièges : {self.config['traps']}")
        line(f"Murs : {self.config['walls']}")
        if self.controller.paused:
            line("-- PAUSED --", (255, 100, 100))
        else:
            line("-- RUNNING --", (100, 255, 100))

    def draw(self):
        world = self.controller.world
        if world:
            self.draw_world(world)
        self.draw_panel()

if __name__ == "__main__":
    MetaProgram().run()
