#start
import pygame
import sys
import time
import random

pygame.init()

width = 1250
height = 770

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Game")

player = pygame.image.load("play.png").convert_alpha()
player = pygame.transform.smoothscale(player, (200, 320))
player_rect = player.get_rect(bottomleft=(0, 0))

clock = pygame.time.Clock()

def display_quest_box():
    quest_rect = pygame.Rect(100, 100, 1050, 570)
    pygame.draw.rect(screen, (246, 194, 86), quest_rect)

#dialogue (setup)
font = pygame.font.SysFont('Times New Roman', 20)
first_dialogue = ["Where's my friend?", "Hi.", "What are you?!"]
postfight_dialogue = ["I'm a LaLa and I'm trying to help you. Let me explain first.", "Okay, fine. What do you wanna help me with?", "I know, what happened to your friend. I used to work for this guy [...]", "Well, Mr. Labufi wants all the LaLas in the world to work for him. And your friend, he knows their locations. I don't know where he is, can you help me find him and save the LaL[...]"]
text_renders = [font.render(text, True, (172, 147, 98)) for text in first_dialogue]

#images
room1_bg = pygame.image.load("raum_von_player.png").convert_alpha()
room1_bg = pygame.transform.smoothscale(room1_bg, (width, height))

lala_img = pygame.image.load("lala.png").convert_alpha()

panel_img = pygame.image.load("panel.png").convert_alpha()
panel_img = pygame.transform.smoothscale(panel_img, (0, 250))
knife_img = pygame.image.load("knife.png").convert_alpha()
heart_img = pygame.image.load("heart.png").convert_alpha()
heart_img = pygame.transform.smoothscale(heart_img, (20, 20))
cactusfruit_img = pygame.image.load("cactusfruit.png").convert_alpha()
slot_img = pygame.image.load("slot.png").convert_alpha()
quest_button = pygame.image.load("quest_button.png").convert_alpha()
try:
    scorpion_img = pygame.image.load("scorpion.png").convert_alpha()
except Exception:
    scorpion_img = pygame.Surface((80, 40), pygame.SRCALPHA)
    scorpion_img.fill((80, 40, 0))
    pygame.draw.circle(scorpion_img, (0, 0, 0), (20, 12), 4)
    pygame.draw.circle(scorpion_img, (0, 0, 0), (60, 12), 4)
scorpion_img = pygame.transform.smoothscale(scorpion_img, (100, 50))
scorpion_rect = scorpion_img.get_rect(topleft=(0, 0))

is_quest_box_shown = False

rooms = [
    {
        "bg": room1_bg,
        "has_lala": True,
        "lala_pos": (200, 150),
        "lala_lives": 3,
        "has_scorpion": False,
        "scorpion_pos": (600, 420),
        "scorpion_lives": 5,
    },
]

#variables
current_room = 0

speed = 5

lala_lives = 0
lala_alive = False
lala_rect = lala_img.get_rect(topleft=(0, 0))

scorpion_active = False
scorpion_lives = 0

player_lives = 3
max_player_lives = 3

knives = []
knife_speed = 10
max_knives = 3

poison_spews = []
poison_speed = 6
poison_damage = 1
poison_img = pygame.Surface((12, 12), pygame.SRCALPHA)
pygame.draw.circle(poison_img, (64, 200, 64), (6, 6), 6)

lala_slimes = []
lala_slime_speed = 6
lala_slime_img = pygame.Surface((14, 14), pygame.SRCALPHA)
pygame.draw.circle(lala_slime_img, (150, 100, 255), (7, 7), 7)
lala_slime_timer = 0
lala_slime_min_cd = 60
lala_slime_max_cd = 180

player_invulnerable = False
invulnerable_frames = 60
invulnerable_timer = 0

facing = "right"

run = True

title_font = pygame.font.SysFont('Times New Roman', 64)
instr_font = pygame.font.SysFont('Times New Roman', 28)

INV_SLOTS = 5
SLOT_SIZE = 64
SLOT_SPACING = 10
slot_img = pygame.transform.smoothscale(slot_img, (SLOT_SIZE, SLOT_SIZE))
knife_inv_img = pygame.transform.smoothscale(knife_img, (int(SLOT_SIZE*0.6), int(SLOT_SIZE*0.6)))
food_inv_img = pygame.transform.smoothscale(cactusfruit_img, (int(SLOT_SIZE*0.6), int(SLOT_SIZE*0.6)))

item_imgs = [knife_inv_img, food_inv_img]
for i in range(INV_SLOTS - len(item_imgs)):
    empty = pygame.Surface((int(SLOT_SIZE*0.6), int(SLOT_SIZE*0.6)), pygame.SRCALPHA)
    item_imgs.append(empty)

inventory = [None] * INV_SLOTS
equipped_index = 0

dropped_items = [
    {
        'type': 0,
        'rect': knife_img.get_rect(topleft=(500, 400)),
        'img': knife_img
    },
]

game_state = "start_screen"
dialogue_index = 0
space_released = True
dialogue_done = False

#functions
def reset_game_state():
    global current_room, lala_lives, lala_alive, lala_rect, player_lives
    global knives, player_rect, facing, player_invulnerable, invulnerable_timer
    global equipped_index, inventory, dropped_items, game_state, dialogue_index, space_released, dialogue_done
    global scorpion_active, scorpion_rect, poison_spews, scorpion_lives, lala_slimes, lala_slime_timer
    current_room = 0
    room = rooms[current_room]
    lala_lives = room.get("lala_lives", 0)
    lala_alive = bool(room.get("has_lala", False))
    lala_rect.topleft = room.get("lala_pos", (0, 0))
    scorpion_active = bool(room.get("has_scorpion", False))
    scorpion_rect.topleft = room.get("scorpion_pos", (0, 0))
    scorpion_lives = room.get("scorpion_lives", 0)
    poison_spews = []
    lala_slimes = []
    lala_slime_timer = random.randint(lala_slime_min_cd, lala_slime_max_cd)
    player_lives = max_player_lives
    knives = []
    player_rect.topleft = (0, 0)
    facing = "right"
    player_invulnerable = False
    invulnerable_timer = 0
    equipped_index = 0
    inventory = [None] * INV_SLOTS
    dropped_items = [
        {
            'type': 0,
            'rect': knife_img.get_rect(topleft=(500, 400)),
            'img': knife_img
        },
    ]
    game_state = "start_screen"
    dialogue_index = 0
    space_released = True
    dialogue_done = False


reset_game_state()


def enter_room(new_room_index, from_right):
    global current_room, lala_lives, lala_alive, lala_rect, scorpion_active, scorpion_rect, poison_spews, scorpion_lives, lala_slime_timer
    current_room = new_room_index
    room = rooms[current_room]
    lala_lives = room.get("lala_lives", 0)
    lala_alive = bool(room.get("has_lala", False))
    lala_rect.topleft = room.get("lala_pos", (0, 0))
    scorpion_active = bool(room.get("has_scorpion", False))
    scorpion_rect.topleft = room.get("scorpion_pos", (0, 0))
    scorpion_lives = room.get("scorpion_lives", 0)
    poison_spews = []
    lala_slime_timer = random.randint(lala_slime_min_cd, lala_slime_max_cd)
    if from_right:
        player_rect.right = width
    else:
        player_rect.left = 0


def get_inventory_rects():
    total_width = INV_SLOTS * SLOT_SIZE + (INV_SLOTS - 1) * SLOT_SPACING
    start_x = (width - total_width) // 2
    y = height - SLOT_SIZE - 10
    rects = []
    for i in range(INV_SLOTS):
        x = start_x + i * (SLOT_SIZE + SLOT_SPACING)
        rects.append(pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE))
    return rects


def render_inventory(surface, mouse_pos, equipped):
    rects = get_inventory_rects()
    for i, rect in enumerate(rects):
        if i == equipped:
            pygame.draw.rect(surface, (255, 220, 0), rect.inflate(6, 6), 4)
        elif rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, (100, 200, 255), rect.inflate(4, 4), 4)
        surface.blit(slot_img, rect.topleft)
        idx = inventory[i]
        if idx is not None:
            item_rect = item_imgs[idx].get_rect()
            item_rect.center = rect.center
            surface.blit(item_imgs[idx], item_rect)

quest_button_x = 1115
quest_button_y = 50
mouse = pygame.mouse.get_pos()

#main game loop
while run:
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    screen.blit(rooms[current_room]["bg"], (0, 0))
    screen.blit(quest_button, (quest_button_x, quest_button_y))

    #ball
    ball_img = pygame.image.load("ball.png").convert_alpha()
ball_img = pygame.transform.smoothscale(ball_img, (20, 20))
ball_speed = 10
balls = []  # Liste für Ballprojektil

...

if event.key == pygame.K_e:  # Spieler hebt Item auf
    to_pick = None
    for i, item in enumerate(dropped_items):
        if player_rect.colliderect(item['rect']):
            to_pick = i
            break
    if to_pick is not None:
        free_slot = None
        for idx, slot in enumerate(inventory):
            if slot is None:
                free_slot = idx
                break
        if free_slot is not None:
            item_type = dropped_items[to_pick]['type']
            inventory[free_slot] = item_type
            if item_type == 1:  # Falls Cactusfruit
                print("Cactusfruit aufgesammelt!")
                for ball_slot in range(len(inventory)):
                    if inventory[ball_slot] is None:  # Freier Slot für Ball
                        inventory[ball_slot] = 2
                        print("Ein Ball wurde ins Inventar gelegt!")
                        break
            dropped_items.pop(to_pick)
        else:
            print("Inventar ist voll!")

...

if event.key == pygame.K_z and len(knives) < max_knives:
    if inventory[equipped_index] == 0:  # Messer werfen
        k_rect = knife_img.get_rect(center=player_rect.center)
        vx = knife_speed if facing == "right" else -knife_speed
        knives.append({'rect': k_rect, 'vx': vx})
    elif inventory[equipped_index] == 2:  # Ball werfen
        b_rect = ball_img.get_rect(center=player_rect.center)
        vx = ball_speed if facing == "right" else -ball_speed
        balls.append({'rect': b_rect, 'vx': vx})

...

# Ballbewegung und Kollision
for ball in balls[:]:
    ball['rect'].x += ball['vx']
    if ball['rect'].right < 0 or ball['rect'].left > width:
        balls.remove(ball)
        continue
    if lala_alive and ball['rect'].colliderect(lala_rect):
        lala_lives = max(0, lala_lives - 2)
        balls.remove(ball)
        continue
    if scorpion_active and ball['rect'].colliderect(scorpion_rect):
        scorpion_lives = max(0, scorpion_lives - 3)
        balls.remove(ball)
        if scorpion_lives <= 0:
            scorpion_active = False

# Rendern der Bälle
for ball in balls:
    screen.blit(ball_img, ball['rect'])

    #reihenfolge (game states)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if quest_button_x <= mouse[0] <= quest_button_x + 125 and quest_button_y <= mouse[1] <= quest_button_y + 75:
                is_quest_box_shown = not is_quest_box_shown
        if game_state == "start_screen":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                game_state = "intro"
                dialogue_index = 0
                space_released = False
        elif game_state == "intro":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and space_released:
                dialogue_index += 1
                space_released = False
                if dialogue_index >= len(first_dialogue):
                    game_state = "main"
                    dialogue_done = True
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                space_released = True
        elif game_state == "main":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and len(knives) < max_knives:
                    if inventory[equipped_index] == 0:
                        k_rect = knife_img.get_rect(center=player_rect.center)
                        vx = knife_speed if facing == "right" else -knife_speed
                        if vx > 0:
                            k_rect.left = player_rect.right
                        else:
                            k_rect.right = player_rect.left
                        knives.append({'rect': k_rect, 'vx': vx})
                if lala_lives == 1:
                    game_state = "postfight_dialogue"
        elif game_state == "postfight_dialogue":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and space_released:
                dialogue_index += 1
                space_released = False
                if dialogue_index >= len(postfight_dialogue):
                    game_state = "main"
                    dialogue_done = True
                    scorpion_active = True
                    scorpion_rect.topleft = rooms[current_room].get("scorpion_pos", scorpion_rect.topleft)
                    scorpion_lives = rooms[current_room].get("scorpion_lives", scorpion_lives)
                    has_cactus = any(item.get('type') == 1 for item in dropped_items)
                    if not has_cactus:
                        cx = scorpion_rect.left
                        cy = scorpion_rect.bottom + 10
                        rect = cactusfruit_img.get_rect(topleft=(cx, cy))
                        dropped_items.append({
                            'type': 1,
                            'rect': rect,
                            'img': cactusfruit_img
                        })
                    lala_slime_timer = random.randint(lala_slime_min_cd, lala_slime_max_cd)
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                space_released = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    to_pick = None
                    for i, item in enumerate(dropped_items):
                        if player_rect.colliderect(item['rect']):
                            to_pick = i
                            break
                    if to_pick is not None:
                        free_slot = None
                        for idx, slot in enumerate(inventory):
                            if slot is None:
                                free_slot = idx
                                break
                        if free_slot is not None:
                            inventory[free_slot] = dropped_items[to_pick]['type']
                            dropped_items.pop(to_pick)
                if event.key == pygame.K_g:
                    drop_item = inventory[equipped_index]
                    if drop_item is not None:
                        px = player_rect.centerx - item_imgs[drop_item].get_width()//2
                        py = player_rect.bottom - item_imgs[drop_item].get_height()
                        rect = item_imgs[drop_item].get_rect(topleft=(px, py))
                        dropped_items.append({
                            'type': drop_item,
                            'rect': rect,
                            'img': item_imgs[drop_item] if drop_item < len(item_imgs) else knife_img
                        })
                        inventory[equipped_index] = None
                if event.key == pygame.K_f and inventory[equipped_index] == 1:
                    player_lives = min(player_lives + 1, max_player_lives)
                    inventory[equipped_index] = None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                rects = get_inventory_rects()
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        equipped_index = i

#game states
    if game_state == "start_screen":
        screen.fill((172, 147, 98))
        title_surf = title_font.render("Save the LaLas!", True, (255, 255, 255))
        instr_surf = instr_font.render("Click Enter oder Space to start...", True, (200, 200, 200))
        screen.blit(title_surf, ((width - title_surf.get_width())//2, height//3))
        screen.blit(instr_surf, ((width - instr_surf.get_width())//2, height//3 + 100))
        pygame.display.update()
        clock.tick(60)
        continue


    if game_state == "intro":
        screen.blit(lala_img, lala_rect)
        screen.blit(player, player_rect)
        if dialogue_index < len(text_renders):
            text_surface = text_renders[dialogue_index]
            padding = 12
            panel_w = text_surface.get_width() + padding * 2
            panel_h = text_surface.get_height() + padding * 2
            panel = pygame.transform.smoothscale(panel_img, (panel_w, panel_h))
            panel.blit(text_surface, (padding, padding))
            panel_x = (width - panel_w) // 2
            panel_y = height - panel_h - 20
            screen.blit(panel, (panel_x, panel_y))
        pygame.display.update()
        clock.tick(60)
        continue

    if game_state == "main":
        if lala_alive and rooms[current_room]["has_lala"]:
            screen.blit(lala_img, lala_rect)

        if scorpion_active:
            if random.random() < 0.01:
                sx, sy = scorpion_rect.center
                px, py = player_rect.center
                dx = px - sx
                dy = py - sy
                dist = (dx*dx + dy*dy) ** 0.5
                if dist == 0:
                    dist = 1
                vx = (dx / dist) * poison_speed
                vy = (dy / dist) * poison_speed
                p = {
                    'x': sx - poison_img.get_width() / 2,
                    'y': sy - poison_img.get_height() / 2,
                    'vx': vx,
                    'vy': vy,
                    'rect': poison_img.get_rect(center=(int(sx), int(sy)))
                }
                poison_spews.append(p)

#knife mechanics
        for k in knives[:]:
            k['rect'].x += k['vx']
            if k['rect'].right < 0 or k['rect'].left > width:
                knives.remove(k)
                continue
            if lala_alive and k['rect'].colliderect(lala_rect):
                lala_lives = max(0, lala_lives - 1)
                knives.remove(k)
                continue
            if scorpion_active and k['rect'].colliderect(scorpion_rect):
                scorpion_lives = max(0, scorpion_lives - 1)
                knives.remove(k)
                if scorpion_lives <= 0:
                    scorpion_active = False
                continue

#lala attack
        if lala_alive:
            lala_slime_timer -= 1
            if lala_slime_timer <= 0:
                if scorpion_active:
                    tx, ty = scorpion_rect.center
                    target_flag = 'scorpion'
                else:
                    tx, ty = player_rect.center
                    target_flag = 'player'
                lx, ly = lala_rect.center
                dx = tx - lx
                dy = ty - ly
                dist = (dx*dx + dy*dy) ** 0.5
                if dist == 0:
                    dist = 1
                vx = (dx / dist) * lala_slime_speed
                vy = (dy / dist) * lala_slime_speed
                s = {
                    'x': lx - lala_slime_img.get_width() / 2,
                    'y': ly - lala_slime_img.get_height() / 2,
                    'vx': vx,
                    'vy': vy,
                    'rect': lala_slime_img.get_rect(center=(int(lx), int(ly))),
                    'target': target_flag
                }
                lala_slimes.append(s)
                lala_slime_timer = random.randint(lala_slime_min_cd, lala_slime_max_cd)

#lala attack, colliding
        for s in lala_slimes[:]:
            s['x'] += s['vx']
            s['y'] += s['vy']
            s['rect'].topleft = (int(s['x']), int(s['y']))
            if s['rect'].right < 0 or s['rect'].left > width or s['rect'].bottom < 0 or s['rect'].top > height:
                try:
                    lala_slimes.remove(s)
                except ValueError:
                    pass
                continue
            if s.get('target') == 'scorpion' and scorpion_active and s['rect'].colliderect(scorpion_rect):
                scorpion_lives = max(0, scorpion_lives - 1)
                try:
                    lala_slimes.remove(s)
                except ValueError:
                    pass
                if scorpion_lives <= 0:
                    scorpion_active = False
                continue
            if s.get('target') == 'player' and s['rect'].colliderect(player_rect):
                if not player_invulnerable:
                    player_lives = max(0, player_lives - 1)
                    player_invulnerable = True
                    invulnerable_timer = invulnerable_frames
                try:
                    lala_slimes.remove(s)
                except ValueError:
                    pass
                continue

#scorpion attack, colliding
        for p in poison_spews[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['rect'].topleft = (int(p['x']), int(p['y']))
            if p['rect'].right < 0 or p['rect'].left > width or p['rect'].bottom < 0 or p['rect'].top > height:
                poison_spews.remove(p)
                continue
            if p['rect'].colliderect(player_rect):
                if not player_invulnerable:
                    player_lives = max(0, player_lives - poison_damage)
                    player_invulnerable = True
                    invulnerable_timer = invulnerable_frames
                try:
                    poison_spews.remove(p)
                except ValueError:
                    pass
                continue

#fight mechanics
        if lala_alive and lala_rect.colliderect(player_rect):
            if not player_invulnerable:
                player_lives -= 1
                player_lives = max(0, player_lives)
                player_invulnerable = True
                invulnerable_timer = invulnerable_frames

        if player_invulnerable:
            invulnerable_timer -= 1
            if invulnerable_timer <= 0:
                player_invulnerable = False

        if player_lives <= 0:
            reset_game_state()
            continue

        if dialogue_done and lala_alive:
            for i in range(lala_lives):
                x = width - 10 - heart_img.get_width() - i * (heart_img.get_width() + 5)
                y = 10
                screen.blit(heart_img, (x, y))
            if lala_lives <= 0:
                lala_alive = False

        for k in knives:
            screen.blit(knife_img, k['rect'])

        for s in lala_slimes:
            screen.blit(lala_slime_img, s['rect'])

        for p in poison_spews:
            screen.blit(poison_img, p['rect'])

        if scorpion_active:
            screen.blit(scorpion_img, scorpion_rect)
            bar_w = scorpion_img.get_width()
            bar_h = 6
            bar_x = scorpion_rect.left
            bar_y = scorpion_rect.top - bar_h - 4
            if bar_w > 0:
                health_ratio = scorpion_lives / float(rooms[current_room].get("scorpion_lives", max(1, scorpion_lives)))
                pygame.draw.rect(screen, (120, 120, 120), (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(screen, (200, 50, 50), (bar_x, bar_y, int(bar_w * health_ratio), bar_h))

        if player_invulnerable and (invulnerable_timer // 6) % 2 == 0:
            pass
        else:
            screen.blit(player, player_rect)

        heart_w = heart_img.get_width()
        spacing = 5
        for i in range(player_lives):
            x = 10 + i * (heart_w + spacing)
            y = 10
            screen.blit(heart_img, (x, y))

        pygame.mouse.set_visible(True)
        render_inventory(screen, mouse_pos, equipped_index)

        for item in dropped_items:
            screen.blit(item['img'], item['rect'])

    if game_state == "main":
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += speed
            facing = "right"
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= speed
            facing = "left"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_rect.y -= speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_rect.y += speed

        if player_rect.left >= width:
            if current_room < len(rooms) - 1:
                enter_room(current_room + 1, from_right=False)
            else:
                player_rect.right = width - 1

        if player_rect.right <= 0:
            if current_room > 0:
                enter_room(current_room - 1, from_right=True)
            else:
                player_rect.left = 0

        if player_rect.top < 0:
            player_rect.top = 0
        if player_rect.bottom > height:
            player_rect.bottom = height

    if is_quest_box_shown:
        display_quest_box()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
