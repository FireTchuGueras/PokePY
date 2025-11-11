import pygame
import sys
import time
import os
import math

# --- Módulos do Jogo ---
import battle_system  # Para funções de batalha, desenho e fontes

# Importa Classes e Constantes
from classes import Player, Pokemon, ZONES, POKEMON_OPTIONS, ITEM_CAPS
from classes import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, BLUE, RED, GRAY, DARK_GREEN,
                     GREEN,
                     BG_COLOR_MENU, MENU_BOX_COLOR, SHADOW_COLOR_DARK, SHADOW_COLOR_LIGHT,
                     BUTTON_NORMAL_COLOR, BUTTON_HOVER_COLOR, SELECTED_COLOR_LIGHT,
                     CONFIRM_COLOR_OK, CONFIRM_COLOR_BAD, TEXT_COLOR_DARK, TEXT_COLOR_LIGHT
                     )
from classes import load_sprite, load_tile
from battle_system import (battle, is_button_clicked, draw_rounded_box, init_fonts)
from classes import load_player_sprite


# Inicializar Pygame
pygame.init()


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PokePy")

# --- CARREGAR OS MAPAS VISUAIS ---
zone_backgrounds = {
    "Zona 1": pygame.image.load("mapa/mapa_zona1.png").convert(),
    "Zona 2": pygame.image.load("mapa/mapa_zona2.png").convert(),
    "Zona 3": pygame.image.load("mapa/mapa_zona3.png").convert(),
}

# Redimensiona para o tamanho da tela
for key in zone_backgrounds:
    zone_backgrounds[key] = pygame.transform.scale(zone_backgrounds[key], (800, 640))


# --- INICIALIZAÇÃO CRÍTICA DAS FONTES ---
battle_system.init_fonts()
# ----------------------------------------

clock = pygame.time.Clock()

# Variáveis globais de mensagem
ITEM_MESSAGE_DURATION = 1500
ITEM_PICKUP_COOLDOWN = 1.5
item_message = None
item_message_timer = 0
last_item_pickup_time = 0.0
inventory_full_flag = False

# --- FUNÇÕES AUXILIARES (Curar Pokémon) ---
def select_pokemon_for_heal(screen, player):
    if player.items.get("Poção", 0) <= 0:
        return "no_potion"

    healing = True
    while healing:
        screen.fill((235, 238, 245))

        # Caixa principal
        box_width, box_height = 500, 450
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_width, box_height), border_radius=25)
        pygame.draw.rect(screen, (200, 200, 220), (box_x, box_y, box_width, box_height), 3, border_radius=25)

        battle_system.draw_text(screen, "Escolha um Pokémon para curar:", SCREEN_WIDTH // 2, box_y + 40,
                                current_font=battle_system.font_xl, color=(50, 50, 80), center=True)

        # Função botão arredondado
        def draw_round_button(y, color, text):
            rect = pygame.Rect(box_x + 75, y, 350, 45)
            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=15)
            battle_system.draw_text(screen, text, rect.centerx, rect.centery,
                                    color=(255, 255, 255), current_font=battle_system.font_large, center=True)
            return rect

        buttons = []
        for i, p in enumerate(player.team):
            btn = draw_round_button(box_y + 100 + i * 60, (100, 150, 255),
                                    f"{p.name} (HP: {p.hp}/{p.max_hp})")
            buttons.append((btn, p))

        back_button_rect = draw_round_button(box_y + 100 + len(player.team) * 60 + 50, (220, 90, 90), "Voltar")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if is_button_clicked(mouse_pos, back_button_rect):
                    return "canceled"

                for button_rect, p in buttons:
                    if is_button_clicked(mouse_pos, button_rect):
                        p.hp = min(p.hp + 50, p.max_hp)
                        player.items["Poção"] -= 1
                        return "healed"


def main():
    global item_message, item_message_timer, last_item_pickup_time, inventory_full_flag

    # Carrega o sprite do avatar do jogador na exploração
    player_sprite = load_sprite("Player Avatar", direction="front", scale=1)

    # --- Configuração do sistema de sprite dinâmico ---
    player_direction = "Frente"  # Direção inicial
    player_frame = 0  # 0 = parado
    player_sprite = load_player_sprite(player_direction, player_frame)
    last_valid_sprite = player_sprite  # guarda o último sprite válido

    sprite_timer = 0
    sprite_interval = 200  # milissegundos entre frames
    sprite_frame_max = 4  # até "New Piskel-4.png"

    player = Player()
    state = "select_team"
    selected_pokemon = []
    current_zone = ZONES[0]
    enemy = None
    current_battle_pokemon = None

    final_boss_defeated = False
    final_boss_triggered = False

    while True:
        current_time_ms = pygame.time.get_ticks()
        current_time_s = time.time()

        if player.repelente_active and current_time_ms > player.repelente_end_time:
            player.repelente_active = False

        prev_state = state

        # 1. ESTADO: SELEÇÃO DE TIME
        if state == "select_team":

            MENU_WIDTH = 450
            BUTTON_HEIGHT = 50
            BUTTON_PADDING = 15

            MENU_HEIGHT = (30 + 60 + 40 + ((len(POKEMON_OPTIONS) * BUTTON_HEIGHT) + (
                    (len(POKEMON_OPTIONS) - 1) * BUTTON_PADDING)) + 30 + BUTTON_HEIGHT + 30)

            MENU_X = (SCREEN_WIDTH - MENU_WIDTH) // 2
            MENU_Y = (SCREEN_HEIGHT - MENU_HEIGHT) // 2

            mouse_pos = pygame.mouse.get_pos()

            # --- DESENHO ---
            screen.fill(BG_COLOR_MENU)
            menu_rect = pygame.Rect(MENU_X, MENU_Y, MENU_WIDTH, MENU_HEIGHT)
            draw_rounded_box(screen, menu_rect, MENU_BOX_COLOR, radius=15, shadow_color=SHADOW_COLOR_DARK,
                             shadow_offset=(5, 5))

            # Título
            y_cursor = MENU_Y + 30
            title_text = "Selecione seu Time"
            title_surf = battle_system.font_xl.render(title_text, True, TEXT_COLOR_DARK)
            title_rect = title_surf.get_rect(center=(MENU_X + MENU_WIDTH // 2, y_cursor + 20))
            screen.blit(title_surf, title_rect)

            # Subtítulo
            y_cursor += 60
            subtitle_text = f"Selecionado: {len(selected_pokemon)}/3"
            subtitle_surf = battle_system.font_large.render(subtitle_text, True, TEXT_COLOR_DARK)
            subtitle_rect = subtitle_surf.get_rect(center=(MENU_X + MENU_WIDTH // 2, y_cursor))
            screen.blit(subtitle_surf, subtitle_rect)

            y_cursor += 40

            # --- Botões dos Pokémon ---
            pokemon_buttons = []
            button_width = MENU_WIDTH - 60

            for i, p in enumerate(POKEMON_OPTIONS):
                is_selected = p.name in [pkm.name for pkm in selected_pokemon]

                button_rect = pygame.Rect(MENU_X + 30, y_cursor, button_width, BUTTON_HEIGHT)

                is_hovered = button_rect.collidepoint(mouse_pos)
                if is_selected:
                    btn_color = SELECTED_COLOR_LIGHT
                    shadow = SHADOW_COLOR_LIGHT
                elif is_hovered:
                    btn_color = BUTTON_HOVER_COLOR
                    shadow = SHADOW_COLOR_DARK
                else:
                    btn_color = BUTTON_NORMAL_COLOR
                    shadow = SHADOW_COLOR_LIGHT

                draw_rounded_box(screen, button_rect, btn_color, radius=10, shadow_color=shadow, shadow_offset=(2, 2))

                # Desenhar texto do botão (centralizado)
                btn_text = f"{p.name} ({p.type})"
                btn_text_surf = battle_system.font_large.render(btn_text, True, TEXT_COLOR_DARK)
                btn_text_rect = btn_text_surf.get_rect(center=button_rect.center)
                screen.blit(btn_text_surf, btn_text_rect)

                pokemon_buttons.append((button_rect, p))
                y_cursor += BUTTON_HEIGHT + BUTTON_PADDING

                # --- Botão Confirmar ---
            y_cursor += 30
            confirm_button_rect = pygame.Rect(MENU_X + 30, y_cursor, button_width, BUTTON_HEIGHT)

            can_confirm = (len(selected_pokemon) == 3)
            is_hovered = confirm_button_rect.collidepoint(mouse_pos)
            if can_confirm:
                btn_color = CONFIRM_COLOR_OK
                text_color = TEXT_COLOR_LIGHT
                if is_hovered: btn_color = (min(btn_color[0] + 20, 255), min(btn_color[1] + 20, 255),
                                            min(btn_color[2] + 20, 255))
            else:
                btn_color = CONFIRM_COLOR_BAD
                text_color = TEXT_COLOR_LIGHT
                if is_hovered: btn_color = (min(btn_color[0] + 20, 255), min(btn_color[1] + 20, 255),
                                            min(btn_color[2] + 20, 255))

            draw_rounded_box(screen, confirm_button_rect, btn_color, radius=10, shadow_color=SHADOW_COLOR_DARK,
                             shadow_offset=(2, 2))

            # Texto do botão confirmar
            confirm_text_surf = battle_system.font_large.render("Confirmar Time", True, text_color)
            confirm_text_rect = confirm_text_surf.get_rect(center=confirm_button_rect.center)
            screen.blit(confirm_text_surf, confirm_text_rect)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button_rect, p in pokemon_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            new_p = Pokemon(p.name, p.type, p.level, p.hp, p.attacks[:])
                            p_names = [pkm.name for pkm in selected_pokemon]
                            if new_p.name in p_names:
                                selected_pokemon = [pkm for pkm in selected_pokemon if pkm.name != new_p.name]
                            elif len(selected_pokemon) < 3:
                                selected_pokemon.append(new_p)

                    if confirm_button_rect.collidepoint(mouse_pos) and len(selected_pokemon) == 3:
                        player.team = selected_pokemon[:]
                        state = "explore"

        # 2. ESTADO: EXPLORAÇÃO
        elif state == "explore":
            # --- NOVO SISTEMA DE MAPA USANDO IMAGENS MASK ---
            map_base = zone_backgrounds[current_zone.name]  # imagem de fundo completa da zona
            # Corrige o caminho do arquivo da máscara, com prefixo "mapa_" e número sem espaço
            zona_numero = current_zone.name.split()[-1]  # pega o número da zona ("1", "2", "3")
            map_mask = pygame.image.load(f"mapa/mapa_zona{zona_numero}_mask.png").convert_alpha()

            # Redimensiona para caber na tela
            map_mask = pygame.transform.scale(map_mask, (SCREEN_WIDTH, SCREEN_HEIGHT))

            # Desenha o mapa base e depois a máscara da grama
            screen.blit(map_mask, (0, 0))
            screen.blit(map_base, (0, 0))

            keys = pygame.key.get_pressed()
            moved = False

            move_speed = 5
            previous_direction = player_direction

            # Detecta direção do movimento
            if keys[pygame.K_LEFT]:
                player.x -= move_speed
                player_direction = "Esquerda"
                moved = True
            elif keys[pygame.K_RIGHT]:
                player.x += move_speed
                player_direction = "Direita"
                moved = True
            elif keys[pygame.K_UP]:
                player.y -= move_speed
                player_direction = "Costas"
                moved = True
            elif keys[pygame.K_DOWN]:
                player.y += move_speed
                player_direction = "Frente"
                moved = True

            # Mantém o jogador dentro da tela
            player.x = max(10, min(player.x, SCREEN_WIDTH - 10))
            player.y = max(10, min(player.y, SCREEN_HEIGHT - 10))

            # Atualiza frame da animação
            current_time = pygame.time.get_ticks()
            if moved:
                if current_time - sprite_timer > sprite_interval:
                    player_frame = (player_frame % 3) + 2  # alterna entre 2,3,4
                    sprite_timer = current_time
            else:
                player_frame = 0  # parado

            # Atualiza sprite conforme direção e frame
            player_sprite = load_player_sprite(player_direction, player_frame)
            # Evita sumir o sprite se não carregar a tempo
            if player_sprite is None:
                # Mantém o último sprite válido em tela
                player_sprite = last_valid_sprite
            else:
                # Atualiza o último sprite válido
                last_valid_sprite = player_sprite

            # Desenho do Jogador (Avatar)
            if player_sprite:
                sprite_w = player_sprite.get_width()
                sprite_h = player_sprite.get_height()

                # Centraliza horizontalmente, mas ancora pelos pés
                sprite_x = player.x - sprite_w // 2
                sprite_y = player.y - sprite_h  # pés ficam no ponto (player.x, player.y)

                screen.blit(player_sprite, (sprite_x, sprite_y))
            else:
                pygame.draw.circle(screen, BLUE, (player.x, player.y), 10)

            # --- HUD Superior (Zona + Repelente) ---
            hud_rect = pygame.Rect(20, 15, 260, 44)

            # Sombra leve para dar profundidade
            shadow_rect = hud_rect.move(2, 2)
            pygame.draw.rect(screen, (210, 215, 235), shadow_rect, border_radius=14)

            # Fundo do HUD
            pygame.draw.rect(screen, (240, 243, 255), hud_rect, border_radius=14)
            pygame.draw.rect(screen, (160, 170, 200), hud_rect, 2, border_radius=14)

            # --- Nome da Zona ---
            zone_text = f"{current_zone.name}"
            battle_system.draw_text(
                screen,
                zone_text,
                hud_rect.x + 14,
                hud_rect.y + 10,
                color=(40, 50, 90),
                current_font=battle_system.font_small,
            )

            # --- Barra de tempo ou status do repelente ---
            if player.repelente_active:
                remaining = max(0, player.repelente_end_time - current_time_ms)
                duration_ratio = min(1.0, remaining / 10000)
                bar_width = int(110 * duration_ratio)
                bar_x = hud_rect.x + 14
                bar_y = hud_rect.y + 28

                # Fundo da barra
                pygame.draw.rect(screen, (190, 210, 240), (bar_x, bar_y, 110, 6), border_radius=4)
                # Parte preenchida (tempo restante)
                pygame.draw.rect(screen, (70, 140, 255), (bar_x, bar_y, bar_width, 6), border_radius=4)

                remaining_s = remaining // 1000
                repel_text = f"Repelente ativo ({remaining_s}s)"
                repel_color = (70, 110, 200)
            else:
                repel_text = "Repelente inativo"
                repel_color = (120, 120, 140)

            # --- Texto do repelente (lado direito do HUD) ---
            tooltip_surface = battle_system.font_small.render(repel_text, True, repel_color)
            tooltip_rect = tooltip_surface.get_rect()
            tooltip_rect.topright = (hud_rect.right - 10, hud_rect.y + 10)
            screen.blit(tooltip_surface, tooltip_rect)
            # --- Fim do HUD ---


            #Mochila sistema
            # Caminho do ícone da mochila
            icon_path = os.path.join(os.path.dirname(__file__), "sprites", "backpack_icon.png")

            # Posição e tamanho do botão
            button_center = (SCREEN_WIDTH - 80, 70)
            button_radius = 22  # raio do botão

            # --- Desenha o botão circular ---
            pygame.draw.circle(screen, (90, 140, 250), button_center, button_radius)
            pygame.draw.circle(screen, (255, 255, 255), button_center, button_radius, 2)  # borda branca

            # --- Ícone da mochila ---
            if os.path.exists(icon_path):
                backpack_icon = pygame.image.load(icon_path).convert_alpha()

                #Ajusta automaticamente o tamanho do ícone com base no botão
                icon_size = int(button_radius * 1.3)
                backpack_icon = pygame.transform.smoothscale(backpack_icon, (icon_size, icon_size))

                # Centraliza o ícone
                icon_rect = backpack_icon.get_rect(center=button_center)
                screen.blit(backpack_icon, icon_rect)
            else:
                font = pygame.font.SysFont(None, 28)
                text = font.render("🎒", True, (0, 0, 0))
                text_rect = text.get_rect(center=button_center)
                screen.blit(text, text_rect)

            # --- Detecção de eventos ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Distância do clique até o centro do botão
                    dist = math.hypot(mouse_pos[0] - button_center[0], mouse_pos[1] - button_center[1])
                    if dist <= button_radius:
                        state = "inventory"
                        inventory_full_flag = False
            # --- Fim sistema mochila ---

                        # LÓGICA DA BATALHA FINAL (ZONA 3)
            if current_zone.name == "Zona 3" and not final_boss_defeated and not final_boss_triggered:
                if player.x > SCREEN_WIDTH - 180 and player.y > SCREEN_HEIGHT // 2 - 50 and player.y < SCREEN_HEIGHT // 2 + 50:
                    final_boss_triggered = True

                    active_found = False
                    for p in player.team:
                        if p.is_alive():
                            current_battle_pokemon = p
                            active_found = True
                            break

                    if active_found:
                        for alpha in range(0, 300, 5):
                            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                            s.set_alpha(alpha)
                            s.fill(BLACK)
                            screen.blit(s, (0, 0))
                            battle_system.draw_text(screen, "Um inimigo colossal bloqueia o caminho!", 150, 280,
                                                    color=WHITE,
                                                    current_font=battle_system.font_xl)
                            pygame.display.flip()
                            pygame.time.wait(5)
                        pygame.time.wait(1000)

                        enemy = Pokemon("Boss Final", "Gelo", level=10, hp=400)

                        state = "battle"
                        continue
                    else:
                        state = "game_over"

                        # Checagem de encontros/itens
            if moved and current_zone.is_in_grass(player.x, player.y) and not (
                    current_zone.name == "Zona 3" and final_boss_triggered):

                # Encontros
                if not player.repelente_active:
                    new_enemy = current_zone.random_encounter()
                    if new_enemy:
                        enemy = new_enemy

                        active_found = False
                        for p in player.team:
                            if p.is_alive():
                                current_battle_pokemon = p
                                active_found = True
                                break

                        if active_found:
                            state = "battle"
                        else:
                            state = "game_over"

                        continue

                        # Itens
                if current_time_s - last_item_pickup_time >= ITEM_PICKUP_COOLDOWN:
                    item = current_zone.random_item(player.x)

                    if item:
                        if player.items.get(item, 0) < ITEM_CAPS.get(item, 999):
                            player.items[item] += 1
                            item_message = f"Encontrou {item}!"
                            item_message_timer = current_time_ms + ITEM_MESSAGE_DURATION
                            last_item_pickup_time = current_time_s
                            inventory_full_flag = False

                        elif not inventory_full_flag:
                            item_message = f"Inventário de {item} cheio!"
                            item_message_timer = current_time_ms + ITEM_MESSAGE_DURATION
                            inventory_full_flag = True
                            # Transição de zona / Vitória
            if player.x > 780:
                player.zone += 1

                # Inicia o Fade-out
                for alpha in range(0, 255, 15):
                    # Mantém o fundo atual e desenha um overlay preto
                    fade_s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    fade_s.set_alpha(alpha)
                    fade_s.fill(BLACK)
                    screen.blit(fade_s, (0, 0))

                    # Desenha a mensagem de transição (opcionalmente)
                    if player.zone < len(ZONES):
                        msg = f"Entrando na {ZONES[player.zone].name}..."
                    elif final_boss_defeated:
                        msg = "Você Venceu o Jogo! Parabéns, Treinador!"
                    else:
                        msg = "Derrote o Boss Final para continuar!"

                    if alpha > 100:  # Mostra a mensagem quando está escuro o suficiente
                        battle_system.draw_text(screen, msg, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                                color=WHITE, current_font=battle_system.font_xl, center=True)

                    pygame.display.flip()
                    pygame.time.wait(20)

                # --- Lógica Pós-Fade ---
                if player.zone < len(ZONES):
                    current_zone = ZONES[player.zone]
                    player.x = 20
                    player.y = SCREEN_HEIGHT // 2

                    # Fica no estado de exploração, mas com o fade-in

                elif final_boss_defeated:
                    # Tela de vitória estilizada (mantida no preto por mais tempo)
                    battle_system.draw_text(screen, "Você Venceu o Jogo! Parabéns, Treinador!", SCREEN_WIDTH // 2,
                                            SCREEN_HEIGHT // 2,
                                            color=BLUE, current_font=battle_system.font_xl, center=True)
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    sys.exit()

                else:
                    # Bloqueado, volta o jogador para trás
                    player.zone -= 1  # Reverte o incremento
                    current_zone = ZONES[player.zone]
                    player.x = 770

                    # Se o jogador foi bloqueado, o fade-in reverte para a tela atual

                # Inicia o Fade-in (Voltando ao normal)
                for alpha in range(255, 0, -15):
                    # Redesenha a tela de exploração (que é o 'fundo' de onde o fade está voltando)
                    screen.fill(WHITE)
                    if player_sprite:
                        sprite_w = player_sprite.get_width()
                        sprite_h = player_sprite.get_height()
                        screen.blit(player_sprite, (player.x - sprite_w // 2, player.y - sprite_h // 2))

                    # Desenha o overlay preto, diminuindo a transparência
                    fade_s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    fade_s.set_alpha(alpha)
                    fade_s.fill(BLACK)
                    screen.blit(fade_s, (0, 0))

                    pygame.display.flip()
                    pygame.time.wait(20)

            # Exibição da mensagem de item
            if item_message and current_time_ms < item_message_timer:
                battle_system.draw_text(screen, item_message, 50, SCREEN_HEIGHT - 50, color=BLACK,
                                        current_font=battle_system.font_large)
            else:
                item_message = None

        elif state == "inventory":
                # Fundo escurecido com leve transparência
                screen.fill((230, 230, 240))

                # Caixa principal centralizada
                box_width, box_height = 500, 400
                box_x = (SCREEN_WIDTH - box_width) // 2
                box_y = (SCREEN_HEIGHT - box_height) // 2
                box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

                # Fundo e borda suave
                pygame.draw.rect(screen, (245, 245, 250), box_rect, border_radius=25)
                pygame.draw.rect(screen, (200, 200, 220), box_rect, 3, border_radius=25)

                # Ícone e título — centralizados
                icon_path = os.path.join(os.path.dirname(__file__), "sprites", "backpack_icon.png")
                icon = None
                if os.path.exists(icon_path):
                    icon = pygame.image.load(icon_path).convert_alpha()
                    icon = pygame.transform.smoothscale(icon, (40, 40))

                title_font = battle_system.font_xl
                title_surface = title_font.render("MOCHILA", True, (40, 40, 70))
                title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2 + 20, box_y + 50))

                if icon:
                    # Centraliza o ícone + texto em conjunto
                    icon_rect = icon.get_rect()
                    total_width = icon_rect.width + 10 + title_rect.width
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    icon_rect.topleft = (start_x, box_y + 30)
                    title_rect.topleft = (start_x + icon_rect.width + 10, box_y + 35)
                    screen.blit(icon, icon_rect)
                screen.blit(title_surface, title_rect)

                # Função para desenhar botões arredondados centralizados
                def draw_round_button(y, color, text):
                    button_width, button_height = 350, 50
                    rect = pygame.Rect(
                        (SCREEN_WIDTH - button_width) // 2, y, button_width, button_height
                    )
                    pygame.draw.rect(screen, color, rect, border_radius=15)
                    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=15)
                    battle_system.draw_text(
                        screen,
                        text,
                        rect.centerx,
                        rect.centery,
                        color=(255, 255, 255),
                        current_font=battle_system.font_large,
                        center=True,
                    )
                    return rect

                # Botões (alinhados verticalmente)
                repel_button_rect = draw_round_button(box_y + 120, (80, 140, 255),
                                                      f"Usar Repelente ({player.items.get('Repelente', 0)})")
                potion_button_rect = draw_round_button(box_y + 200, (90, 190, 120),
                                                       f"Usar Poção ({player.items.get('Poção', 0)})")
                close_button_rect = draw_round_button(box_y + 300, (220, 90, 90),
                                                      "Fechar Mochila")

                pygame.display.flip()

                # Eventos
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()

                        # Usar Repelente
                        if is_button_clicked(mouse_pos, repel_button_rect):
                            if player.use_item("Repelente"):
                                battle_system.draw_text(screen, "Repelente ativado!", SCREEN_WIDTH // 2,
                                                        box_y + box_height - 40,
                                                        color=(50, 50, 80), current_font=battle_system.font_large,
                                                        center=True)
                                pygame.display.flip()
                                pygame.time.wait(1000)
                            else:
                                battle_system.draw_text(screen, "Sem Repelentes!", SCREEN_WIDTH // 2,
                                                        box_y + box_height - 40,
                                                        color=(200, 60, 60), current_font=battle_system.font_large,
                                                        center=True)
                                pygame.display.flip()
                                pygame.time.wait(1000)

                        # Usar Poção
                        elif is_button_clicked(mouse_pos, potion_button_rect):
                            if player.items.get("Poção", 0) > 0:
                                result = select_pokemon_for_heal(screen, player)
                                if result in ("canceled", "healed"):
                                    state = "inventory"
                            else:
                                battle_system.draw_text(screen, "Sem Poções!", SCREEN_WIDTH // 2,
                                                        box_y + box_height - 40,
                                                        color=(200, 60, 60), current_font=battle_system.font_large,
                                                        center=True)
                                pygame.display.flip()
                                pygame.time.wait(1000)

                        # Fechar Mochila
                        elif is_button_clicked(mouse_pos, close_button_rect):
                            state = "explore"

        # 4. ESTADO: BATALHA
        elif state == "battle":
            result = battle(screen, player, current_battle_pokemon, enemy, current_zone)

            if result == "win":
                if enemy.name == "Boss Final":
                    final_boss_defeated = True
                    battle_system.draw_text(screen, "O Boss Final foi derrotado!", 200, 300, color=GREEN,
                                            current_font=battle_system.font_xl)
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    tela_creditos(screen)
                else:
                    battle_system.draw_text(screen, f"Você venceu e ganhou XP!", 300, 300)
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    state = "explore"

            elif result == "lose":
                state = "game_over"

            elif result == "fled":
                # --- TELA DE FUGA SUCESSO ---
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                screen.blit(s, (0, 0))

                BOX_W, BOX_H = 500, 150
                BOX_X = (SCREEN_WIDTH - BOX_W) // 2
                BOX_Y = (SCREEN_HEIGHT - BOX_H) // 2
                message_rect = pygame.Rect(BOX_X, BOX_Y, BOX_W, BOX_H)

                battle_system.draw_rounded_box(screen, message_rect, battle_system.BATTLE_MENU_BG, radius=15,
                                               shadow_color=battle_system.SHADOW_COLOR_DARK, shadow_offset=(5, 5))
                pygame.draw.rect(screen, battle_system.BATTLE_MENU_BORDER, message_rect, 2, border_radius=15)

                battle_system.draw_text(screen, "Você fugiu com sucesso!", BOX_X + BOX_W // 2, BOX_Y + BOX_H // 2,
                                        color=battle_system.DARK_BLUE, current_font=battle_system.font_xl, center=True)

                pygame.display.flip()
                pygame.time.wait(1500)
                state = "explore"  # Retorna ao modo de exploração

            elif result == "flee_blocked":
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                screen.blit(s, (0, 0))

                BOX_W, BOX_H = 500, 150
                BOX_X = (SCREEN_WIDTH - BOX_W) // 2
                BOX_Y = (SCREEN_HEIGHT - BOX_H) // 2
                message_rect = pygame.Rect(BOX_X, BOX_Y, BOX_W, BOX_H)

                battle_system.draw_rounded_box(screen, message_rect, CONFIRM_COLOR_BAD, radius=15,
                                               shadow_color=SHADOW_COLOR_DARK, shadow_offset=(5, 5))
                pygame.draw.rect(screen, RED, message_rect, 2, border_radius=15)

                battle_system.draw_text(screen, "Não é possível fugir do Boss!", BOX_X + BOX_W // 2, BOX_Y + BOX_H // 2,
                                        color=TEXT_COLOR_LIGHT, current_font=battle_system.font_large, center=True)

                pygame.display.flip()
                pygame.time.wait(1500)
                state = "battle"  # Permanece no estado de batalha para que o jogador escolha outra ação

            elif result == "switch_required" or result == "switch_requested":
                state = "select_in_battle"

        # 5. ESTADO: SELEÇÃO DE POKÉMON DURANTE A BATALHA
        elif state == "select_in_battle":
            forced_switch = (not current_battle_pokemon.is_alive())


            temp_current_pokemon = current_battle_pokemon if not forced_switch else None


            new_pokemon, switched = battle_system.select_pokemon_in_battle(screen, player, temp_current_pokemon, enemy, current_zone)



            if switched:
                current_battle_pokemon = new_pokemon
                battle_system.display_message(
                    screen,
                    current_battle_pokemon,
                    enemy,
                    f"Vai, {current_battle_pokemon.name}!",
                    current_zone,
                    1000
                )
                state = "battle"
            elif not switched and forced_switch:
                pass

        # 6. ESTADO: GAME OVER
        elif state == "game_over":
            # --- ESTILO PARA TELA DE GAME OVER  ---
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, (0, 0))

            BOX_W = 500
            BOX_H = 150
            BOX_X = (SCREEN_WIDTH - BOX_W) // 2
            BOX_Y = (SCREEN_HEIGHT - BOX_H) // 2

            message_rect = pygame.Rect(BOX_X, BOX_Y, BOX_W, BOX_H)

            battle_system.draw_rounded_box(
                screen, message_rect, CONFIRM_COLOR_BAD, radius=15,
                shadow_color=SHADOW_COLOR_DARK, shadow_offset=(5, 5)
            )
            pygame.draw.rect(screen, RED, message_rect, 3, border_radius=15)

            battle_system.draw_text(
                screen, "GAME OVER", BOX_X + BOX_W // 2, BOX_Y + BOX_H // 2 - 20,
                color=TEXT_COLOR_LIGHT, current_font=battle_system.font_xl, center=True
            )
            battle_system.draw_text(
                screen, "Seu time desmaiou!", BOX_X + BOX_W // 2, BOX_Y + BOX_H // 2 + 25,
                color=TEXT_COLOR_LIGHT, current_font=battle_system.font, center=True
            )

            pygame.display.flip()
            pygame.time.wait(3000)
            sys.exit()

        # LÓGICA DE ATIVAÇÃO DO REPELENTE
        if prev_state == "inventory" and state == "explore" and player.repelente_pending:
            player.repelente_active = True
            player.repelente_end_time = current_time_ms + 5000
            player.repelente_pending = False

        pygame.display.flip()
        clock.tick(60)


def tela_creditos(screen):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 26, bold=True)
    big_font = pygame.font.SysFont("Arial", 40, bold=True)

    # Fade-in para preto total
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(30)

    # Lista dos créditos (principais + 20 extras)
    creditos = [
        "PokePy - Fim da Jornada",
        "",
        "Créditos Especiais",
        "",
        "Sprites: João Lucas",
        "Sprite do avatar: Prima do Eduardo",
        "Sprite do mapa: Eduardo",
        "Sistema de mochila: Jéssica",
        "Tela inicial: Luiz",
        "Sistema de batalha: Maycon",
        "",
        "Equipe de Apoio",
        "Animações: Maycon",
        "Roteiro: Jéssica e Eduardo",
        "Design de UI: João Lucas e Maycon",
        "Balanceamento: Luiz",
        "Cenários: Eduardo",
        "Testes: Maycon",
        "Programação auxiliar: Luiz",
        "Ilustrações: Eduardo",
        "Consultoria Pokémon: Maycon",
        "Documentação: Maycon e Luiz",
        "Gerenciamento: Jéssica",
        "Agradecimentos especiais: ChatOpenAI!",
        "",
        "",
        "Obrigado por jogar!",
    ]

    # Define a posição inicial (fora da tela)
    y_offset = SCREEN_HEIGHT + 50
    scroll_speed = 1.2  # Velocidade suave

    running = True
    while running:
        screen.fill((0, 0, 0))

        # Desenha os créditos subindo
        for i, line in enumerate(creditos):
            if i == 0:
                text_surface = big_font.render(line, True, (255, 255, 255))
            else:
                text_surface = font.render(line, True, (230, 230, 230))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 40))
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        clock.tick(60)
        y_offset -= scroll_speed  # Faz os créditos subirem

        # Fecha automaticamente após o fim
        if y_offset + len(creditos) * 40 < -50:
            running = False

        # Permite sair mais cedo
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                running = False

    # Fade-out final
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.wait(20)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()