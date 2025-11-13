import pygame
import threading
from smart_program import SimulationController

pygame.init()
FONT = pygame.font.Font(None, 24)
CELL = 16

class MetaProgramConfig:
    def __init__(self, init_speed_given:float):
        self.thread = None
        self.controller = None
        self.config = None
        self.custom_speed = init_speed_given
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Aifants - Config")
        self.clock = pygame.time.Clock()
        self.running = True

    def run_simulation(self):
        self.controller = SimulationController(custom_speed=self.custom_speed)
        self.controller.configure_world(**self.config)
        self.thread = threading.Thread(target=self.controller.run, daemon=True)
        self.thread.start()
        self.screen = pygame.display.set_mode((1900, 1080))
        pygame.display.set_caption("Aifants - interface pro gaming")
        self.running = True
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
                elif event.key == pygame.K_m:
                    self.controller.set_speed(self.controller.speed + 1000)
                elif event.key == pygame.K_d:
                    self.controller.set_speed(self.controller.speed - 1000)
                elif event.key == pygame.K_p:
                    self.controller.set_speed(self.controller.speed + 100000)
                elif event.key == pygame.K_a:
                    self.controller.set_speed(self.controller.speed - 100000)



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
        line(f"[ENTER] Reset")
        line(f"jouez avec les flèches pour augmenter ou baisser la vitesse ({self.controller.speed:.1f}x)")
        line("M: +1000 vitesse | D: -1000 vitesse")
        line("P: +100000 vitesse | A: -100000 vitesse")
        line("")
        line(f"Taille : {self.config['width']}x{self.config['height']}")
        line(f"Nourriture : {self.config['food_sources']}")
        line(f"Pièges : {self.config['traps']}")
        line(f"Murs : {self.config['walls']}")


        if self.config is not None:
            line(f"Taille : {self.config['width']}x{self.config['height']}")
            line(f"Nourriture : {self.config['food_sources']}")
            line(f"Pièges : {self.config['traps']}")
            line(f"Murs : {self.config['walls']}")
        else:
            line("(Aucune configuration chargée)", (180, 180, 180))

        if self.controller.paused:
            line("-- PAUSED --", (255, 100, 100))
        else:
            line("-- RUNNING --", (100, 255, 100))

    def draw(self):
        world = self.controller.world
        if world:
            self.draw_world(world)
        self.draw_panel()

    def settings_menu(self):
        """Affiche un menu simple pour choisir les valeurs avant de lancer la simulation"""
        menu_running = True
        width = 80
        height = 64
        food = 10
        traps = 20
        walls = 100
        nb_explo = 6
        nb_recol = 6
        nb_comba = 6

        input_active = None  # quel champ est actif pour taper
        fields = [
            ("width", width), ("height", height), ("food", food),
            ("traps", traps), ("walls", walls),
            ("exploratrice", nb_explo), ("recolteuse", nb_recol), ("combattante", nb_comba)
        ]
        values = {name: val for name, val in fields}

        while menu_running:
            self.screen.fill((30, 30, 40))
            y = 50
            mx, my = pygame.mouse.get_pos()

            for i, (name, val) in enumerate(values.items()):
                color = (255, 255, 255) if input_active != name else (255, 200, 80)
                txt = FONT.render(f"{name}: {val}", True, color)
                rect = txt.get_rect(topleft=(50, y))
                self.screen.blit(txt, rect)
                # clic sur le champ
                if rect.collidepoint((mx, my)) and pygame.mouse.get_pressed()[0]:
                    input_active = name
                y += 40

            # bouton start
            start_rect = pygame.Rect(50, y + 20, 120, 40)
            pygame.draw.rect(self.screen, (80, 200, 80), start_rect)
            start_txt = FONT.render("START", True, (0, 0, 0))
            self.screen.blit(start_txt, (start_rect.x + 10, start_rect.y + 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN:
                        input_active = None
                    elif event.key == pygame.K_BACKSPACE:
                        values[input_active] = int(str(values[input_active])[:-1] or 0)
                    elif event.unicode.isdigit():
                        values[input_active] = int(str(values[input_active]) + event.unicode)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(event.pos):
                        # Valider la config
                        self.config = {
                            "width": values["width"],
                            "height": values["height"],
                            "food_sources": values["food"],
                            "traps": values["traps"],
                            "walls": values["walls"],
                            "nb_ant_explo": values["exploratrice"],
                            "nb_ant_recol": values["recolteuse"],
                            "nb_ant_comba": values["combattante"],
                        }
                        menu_running = False

            pygame.display.flip()
            self.clock.tick(30)

