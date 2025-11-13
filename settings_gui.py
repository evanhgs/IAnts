import pygame
import thorpy as tp
from univers import Map, Point, Wall, Trap, Food, Nest, QTable, Pheromone, AntCategory, step_simulation
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Configuration - AI FAnts")

bck = pygame.Surface(screen.get_size())
bck.fill((30, 30, 40))

tp.set_default_font(("arialrounded", "arial", "calibri", "century"), font_size=20)
tp.init(screen, tp.theme_round2)

# ------------------------------------------------------------
# CONFIG PAR DÉFAUT
# ------------------------------------------------------------
default_config = {
    "width": 64,
    "height": 36,
    "food_sources": 5,
    "traps": 5,
    "walls": 150,
}

# ------------------------------------------------------------
# COMPOSANTS THORPY
# ------------------------------------------------------------
title = tp.make_text("AI FAnts - Configuration", 30, (220, 220, 255))

width_box = tp.Inserter(name="Largeur :", value=str(default_config["width"]))
height_box = tp.Inserter(name="Hauteur :", value=str(default_config["height"]))
food_box = tp.Inserter(name="Sources de nourriture :", value=str(default_config["food_sources"]))
traps_box = tp.Inserter(name="Pièges :", value=str(default_config["traps"]))
walls_box = tp.Inserter(name="Murs :", value=str(default_config["walls"]))

show_phero_checkbox = tp.CheckBox(text="Afficher les phéromones", value=True)
mode_select = tp.DropDownList(
    titles=["Mode apprentissage", "Mode simulation"],
    normal_params={"text": "Choisir un mode"},
)

status_text = tp.make_text("", 18, (200, 200, 200))

# ------------------------------------------------------------
# FONCTIONS
# ------------------------------------------------------------
def build_world(config):
    w = Map(config["width"], config["height"])
    # murs
    for _ in range(config["walls"]):
        x = random.randint(0, w.width - 1)
        y = random.randint(0, w.height - 1)
        w.walls.append(Wall(Point(x, y)))
    # pièges
    for _ in range(config["traps"]):
        x = random.randint(0, w.width - 1)
        y = random.randint(0, w.height - 1)
        w.traps.append(Trap(Point(x, y)))
    # nourriture
    for _ in range(config["food_sources"]):
        x = random.randint(0, w.width - 1)
        y = random.randint(0, w.height - 1)
        w.foods.append(Food(Point(x, y), qte=random.randint(1000, 20000)))
    w.nest = Nest(Point(w.width // 2, w.height // 2))
    return w


def launch_simulation():
    # lire valeurs interface
    try:
        config = {
            "width": int(width_box.get_value()),
            "height": int(height_box.get_value()),
            "food_sources": int(food_box.get_value()),
            "traps": int(traps_box.get_value()),
            "walls": int(walls_box.get_value()),
            "show_phero": show_phero_checkbox.get_value(),
            "mode": mode_select.get_value() or "Mode simulation",
        }
    except ValueError:
        status_text.set_text("Erreur : valeurs numériques invalides.")
        return

    status_text.set_text("Lancement de la simulation...")
    pygame.display.flip()

    # lancer le simulateur pygame (fenêtre séparée)
    run_simulation(config)


# ------------------------------------------------------------
# SIMULATION PYGAME (reprend la logique de ton main.py)
# ------------------------------------------------------------
def run_simulation(config):
    CELL = 16
    SCREEN_W = config["width"] * CELL
    SCREEN_H = config["height"] * CELL

    sim_screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("AI FAnts - Simulation")

    clock = pygame.time.Clock()
    running = True

    world = build_world(config)
    qtable = QTable(alpha=0.2, gamma=0.9, epsilon=0.2)
    pher = Pheromone(world)

    ants = []
    for _ in range(8):
        ants.append(AntCategory.exploratrice(world.nest.pos, qtable))
    for _ in range(12):
        ants.append(AntCategory.recolteuse(world.nest.pos, qtable))
    ants.append(AntCategory.combattante(world.nest.pos, qtable))

    paused = False
    steps_per_frame = 1

    def draw_world():
        sim_screen.fill((25, 25, 35))
        # murs
        for w in world.walls:
            pygame.draw.rect(sim_screen, (100, 100, 100), (w.pos.x * CELL, w.pos.y * CELL, CELL, CELL))
        # pièges
        for t in world.traps:
            pygame.draw.rect(sim_screen, (180, 30, 30), (t.pos.x * CELL, t.pos.y * CELL, CELL, CELL))
        # nourriture
        for f in world.foods:
            q = min(20000, max(0, f.qte))
            intensity = int(50 + (q / 20000) * 205)
            pygame.draw.rect(sim_screen, (intensity, intensity // 2, 20), (f.pos.x * CELL, f.pos.y * CELL, CELL, CELL))
        # nid
        pygame.draw.rect(sim_screen, (200, 180, 60), (world.nest.pos.x * CELL, world.nest.pos.y * CELL, CELL, CELL))

        # phéromones (optionnel)
        if config["show_phero"]:
            for p, val in world.pheromone_to_food.items():
                alpha = max(0, min(255, int(abs(val) * 0.05)))
                color = (0, alpha, 0)
                pygame.draw.rect(sim_screen, color, (p.x * CELL, p.y * CELL, CELL, CELL))
            for p, val in world.pheromone_to_nest.items():
                alpha = max(0, min(255, int(abs(val) * 0.05)))
                color = (alpha, 0, 0)
                pygame.draw.rect(sim_screen, color, (p.x * CELL, p.y * CELL, CELL, CELL))

        # fourmis
        for a in ants:
            x, y = a.position.x * CELL + 2, a.position.y * CELL + 2
            size = CELL - 4
            if a.category == "exploratrice":
                color = (50, 200, 50)
            elif a.category == "recolteuse":
                color = (50, 150, 220)
            elif a.category == "combattante":
                color = (220, 50, 50)
            else:
                color = (200, 200, 200)
            pygame.draw.rect(sim_screen, color, (x, y, size, size))

        # HUD
        font = pygame.font.Font(None, 24)
        text = font.render(f"Nest food: {world.nest.food_stored}", True, (255, 255, 255))
        sim_screen.blit(text, (10, 10))
        pygame.display.flip()

    # boucle principale simulation
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP:
                    steps_per_frame = min(10, steps_per_frame + 1)
                elif event.key == pygame.K_DOWN:
                    steps_per_frame = max(1, steps_per_frame - 1)

        if not paused:
            for _ in range(steps_per_frame):
                step_simulation(ants, world, qtable, pher, dt=1)

        draw_world()
        clock.tick(60)

    pygame.display.set_mode((1280, 720))  # retour à la fenêtre menu


# ------------------------------------------------------------
# ORGANISATION INTERFACE
# ------------------------------------------------------------
apply_button = tp.make_button("Lancer la simulation", func=launch_simulation)
quit_button = tp.make_button("Quitter", func=pygame.quit)

menu_box = tp.Box(
    elements=[
        title,
        width_box, height_box, food_box, traps_box, walls_box,
        mode_select, show_phero_checkbox,
        apply_button, quit_button, status_text,
    ]
)
menu_box.center()

menu = tp.Menu(menu_box)
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        menu.react(event)

    screen.blit(bck, (0, 0))
    menu_box.blit()
    menu_box.update()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
