import pygame
import sys
import random
# Importa load_sprite e cores (incluindo as novas de UI)
from classes import (SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, BUTTON_COLOR, SELECTED_COLOR, RED,
                     DARK_BLUE, LIGHT_GRAY, GREEN, BLUE, GRAY, WHITE, DARK_GREEN,
                     SHADOW_COLOR_DARK,
                     # --- Novas Cores para Batalha ---
                     BATTLE_MENU_BG, BATTLE_MENU_BORDER, BATTLE_BUTTON_NORMAL,
                     BATTLE_BUTTON_HOVER, BATTLE_BUTTON_SELECTED,
                     HP_BAR_EMPTY, HP_BAR_LOW, HP_BAR_MEDIUM, HP_BAR_FULL,
                     BATTLE_BG_OVERLAY,
                     load_sprite, load_background # <--- Importe também load_background
                     )
from classes import Player, Pokemon
# Variáveis globais de fonte inicializadas como None.
font = None
font_large = None
font_xl = None
font_small = None
font_medium = None

def init_fonts():
    """Inicializa e define as variáveis globais de fonte APÓS o pygame.init()."""
    global font, font_large, font_xl, font_small, font_medium  # <-- isso é essencial

    try:
        if not pygame.font.get_init():
            pygame.font.init()

        font_small = pygame.font.SysFont(None, 18)
        font_medium = pygame.font.SysFont("arial", 18, bold=True)
        font = pygame.font.SysFont(None, 24)
        font_large = pygame.font.SysFont(None, 30)
        font_xl = pygame.font.SysFont(None, 40)

    except pygame.error as e:
        print(f"Erro ao inicializar as fontes em battle_system: {e}")
        sys.exit()



# --- FUNÇÕES DE DESENHO AUXILIARES ---
def draw_text(
    screen,
    text,
    x,
    y,
    color=BLACK,
    current_font=None,
    center=False,
    center_y=False,
    align_right=False
):
    """
    Desenha texto na tela com várias opções de alinhamento:
      - center: centraliza no eixo X e Y
      - center_y: centraliza apenas verticalmente
      - align_right: alinha o texto à direita no ponto X
    """

    if current_font is None:
        current_font = font

    text_surface = current_font.render(str(text), True, color)
    text_rect = text_surface.get_rect()

    # --- Lógica de alinhamento ---
    if center:
        text_rect.center = (x, y)
    elif align_right:
        text_rect.right = x
        text_rect.centery = y
    elif center_y:
        text_rect.midleft = (x, y)
    else:
        text_rect.topleft = (x, y)
    # ------------------------------

    screen.blit(text_surface, text_rect)


def draw_button(screen, text, x, y, w, h, color=BUTTON_COLOR):
    pygame.draw.rect(screen, color, (x, y, w, h))
    draw_text(screen, text, x + 10, y + 10)
    return pygame.Rect(x, y, w, h)


def is_button_clicked(mouse_pos, button_rect):
    # Verifica se button_rect é um Rect ou uma tupla (x, y, w, h)
    if isinstance(button_rect, pygame.Rect):
        return button_rect.collidepoint(mouse_pos)
    elif isinstance(button_rect, (tuple, list)) and len(button_rect) == 4:
        x, y, w, h = button_rect
        return x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h

    # Se não for um formato reconhecido, retorna False
    # print(f"Formato de button_rect não reconhecido: {button_rect}")
    return False


def draw_button_styled(screen, text, rect, text_color, bg_color, hover_color,
                       is_selected=False, mouse_pos=None, font_to_use=None):
    """
    Desenha um botão com estilo moderno (arredondado, sombra, hover, seleção).
    """
    if font_to_use is None:
        font_to_use = font_large  # Usa a fonte global default

    # Converte rect para pygame.Rect se for uma tupla
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(rect)

    current_bg_color = bg_color
    shadow_offset = (2, 2)
    shadow_color_btn = SHADOW_COLOR_DARK  # Cor padrão da sombra

    # Lógica de Hover/Seleção
    if is_selected:
        current_bg_color = BATTLE_BUTTON_SELECTED  # Cor verde claro para selecionado
        shadow_offset = (0, 0)  # Sem sombra quando selecionado/pressionado
    elif mouse_pos and rect.collidepoint(mouse_pos):
        current_bg_color = hover_color  # Cor de hover
        shadow_offset = (1, 1)  # Sombra mais sutil no hover

    # Desenha a sombra
    shadow_rect = pygame.Rect(rect.x + shadow_offset[0], rect.y + shadow_offset[1], rect.width, rect.height)
    pygame.draw.rect(screen, shadow_color_btn, shadow_rect, border_radius=8)

    # Desenha o botão principal
    pygame.draw.rect(screen, current_bg_color, rect, border_radius=8)

    # Desenha a borda (opcional, pode deixar sem ou mais fina)
    pygame.draw.rect(screen, BATTLE_MENU_BORDER, rect, 1, border_radius=8)

    # Desenha o texto (centralizado)
    text_surf = font_to_use.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

def draw_rounded_box(screen, rect, color, radius=10, shadow_color=None, shadow_offset=(3, 3)):
    """
    Desenha uma caixa com cantos arredondados e uma leve sombra.
    """
    if shadow_color is None:
        shadow_color = SHADOW_COLOR_DARK  # Usa a cor importada como padrão

    # Converte rect (que pode ser tupla) para pygame.Rect
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(rect)

    # 1. Desenha a Sombra
    shadow_rect = pygame.Rect(
        rect.x + shadow_offset[0],
        rect.y + shadow_offset[1],
        rect.width,
        rect.height
    )
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=radius)

    # 2. Desenha a Caixa principal
    pygame.draw.rect(screen, color, rect, border_radius=radius)


# Em battle_system.py
def draw_pokemon_status(screen, pokemon, x_start, is_player=True):
    box_w = 200
    box_h = 100

    if is_player:
        direction = "back"
    else:
        direction = "front"

    box_y = 30 if not is_player else SCREEN_HEIGHT - 350  # <--- AJUSTADO (inimigo mais para cima)

    status_rect = pygame.Rect(x_start, box_y, box_w, box_h)

    draw_rounded_box(screen, status_rect, BATTLE_MENU_BG, radius=10,
                     shadow_color=SHADOW_COLOR_DARK, shadow_offset=(3, 3))

    draw_text(screen, f"{pokemon.name}", x_start + 10, box_y + 10,
              color=BLACK, current_font=font_large)
    draw_text(screen, f"Lvl: {pokemon.level}", x_start + 10, box_y + 35,
              color=BLACK)

    hp_bar_x = x_start + 10
    hp_bar_y = box_y + 60
    hp_bar_w = box_w - 20
    hp_bar_h = 15

    current_hp_ratio = pokemon.hp / pokemon.max_hp if pokemon.max_hp > 0 else 0
    hp_color = HP_BAR_FULL
    if current_hp_ratio < 0.2:
        hp_color = HP_BAR_EMPTY
    elif current_hp_ratio < 0.5:
        hp_color = HP_BAR_LOW
    elif current_hp_ratio < 0.75:
        hp_color = HP_BAR_MEDIUM

    pygame.draw.rect(screen, HP_BAR_EMPTY, (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), border_radius=5)
    pygame.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, int(hp_bar_w * current_hp_ratio), hp_bar_h),
                     border_radius=5)
    pygame.draw.rect(screen, BLACK, (hp_bar_x, hp_bar_y, hp_bar_w, hp_bar_h), 1, border_radius=5)

    hp_text_y = box_y + 80
    draw_text(screen, f"HP: {pokemon.hp}/{pokemon.max_hp}", x_start + 10, hp_text_y, color=BLACK)

    # Posições para os sprites
    if is_player: # Pokémon do jogador
        sprite_x = SCREEN_WIDTH * 0.2
        sprite_y = SCREEN_HEIGHT * 0.3
    else: # Pokémon inimigo
        sprite_x = SCREEN_WIDTH * 0.80
        sprite_y = SCREEN_HEIGHT * 0.32

    # --- FIM DO REPOSICIONAMENTO DOS SPRITES ---
    direction = "back" if is_player else "front"
    sprite_img = load_sprite(pokemon.name, direction = direction)



    if sprite_img:
        # Posição superior esquerda ajustada pela metade do tamanho do sprite para centralizar
        img_x = sprite_x - sprite_img.get_width() // 2
        img_y = sprite_y - sprite_img.get_height() // 2

        screen.blit(sprite_img, (img_x, img_y))
    else:
        sprite_color = BLUE if is_player else RED
        pygame.draw.circle(screen, sprite_color, (int(sprite_x), int(sprite_y)), 50)
        draw_text(screen, "SPRITE", int(sprite_x) - 30, int(sprite_y) - 10, color=WHITE)


def draw_battle_screen(screen, current_pokemon, enemy, current_zone):  # <--- MODIFICADO

    # 1. Desenha o fundo da zona
    background_img = load_background(current_zone.name)
    if background_img:
        screen.blit(background_img, (0, 0))
    else:
        # Fallback para cor verde se a imagem não carregar
        screen.fill(DARK_GREEN)

        # Adiciona um leve overlay escuro para melhorar contraste do UI
    overlay_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay_surf.fill(BATTLE_BG_OVERLAY)  # Cor do overlay (preto semi-transparente)
    screen.blit(overlay_surf, (0, 0))

    # 2. Desenha os status dos Pokémon
    draw_pokemon_status(screen, enemy, SCREEN_WIDTH - 250, is_player=False)
    draw_pokemon_status(screen, current_pokemon, 50, is_player=True)

    MENU_X = 20  # Mais afastado das bordas
    MENU_Y = SCREEN_HEIGHT - 170  # Menu um pouco mais para cima
    MENU_W = SCREEN_WIDTH - 40  # Largura total - 2x padding
    MENU_H = 150

    # Desenha a caixa principal do menu de batalha com estilo arredondado e sombra
    battle_menu_rect = pygame.Rect(MENU_X, MENU_Y, MENU_W, MENU_H)
    draw_rounded_box(screen, battle_menu_rect, BATTLE_MENU_BG, radius=15,
                     shadow_color=SHADOW_COLOR_DARK, shadow_offset=(5, 5))  # <--- MODIFICADO
    # Borda externa
    pygame.draw.rect(screen, BATTLE_MENU_BORDER, battle_menu_rect, 2, border_radius=15)

    # Caixa de mensagem (arredondada também)
    message_rect = pygame.Rect(MENU_X, MENU_Y - 50, MENU_W, 40)
    draw_rounded_box(screen, message_rect, WHITE, radius=10,
                     shadow_color=SHADOW_COLOR_DARK, shadow_offset=(3, 3))  # <--- MODIFICADO
    pygame.draw.rect(screen, BATTLE_MENU_BORDER, message_rect, 1, border_radius=10)  # Borda


def display_message(screen, current_pokemon, enemy, message, current_zone, wait_time=1500): # <--- MODIFICADO
    # Passa current_zone para draw_battle_screen
    draw_battle_screen(screen, current_pokemon, enemy, current_zone) # <--- MODIFICADO

    MENU_X = 20 # Ajustado para o novo layout
    MENU_Y = SCREEN_HEIGHT - 170 # Ajustado para o novo layout

    draw_text(screen, message, MENU_X + 10, MENU_Y - 40, color=BLACK, current_font=font_large)

    pygame.display.flip()

    if wait_time > 0:
        pygame.time.wait(wait_time)


# --- LÓGICA DE BATALHA PRINCIPAL ---
def select_pokemon_in_battle(screen, player, current_pokemon, enemy, current_zone=None):
    """
    Tela para trocar de Pokémon no meio da batalha.
    Retorna (pokemon_escolhido, True) se trocou.
    Retorna (pokemon_atual, False) se cancelou (clicou em Voltar).
    """

    clock = pygame.time.Clock()

    # Toast (mensagem curta) - não bloqueante
    toast_text = None
    toast_expire = 0  # pygame time in ms when toast should disappear
    TOAST_DURATION_MS = 900

    while True:
        now = pygame.time.get_ticks()

        # Fundo leve (consistente com resto da UI)
        screen.fill((230, 230, 240))

        # Caixa centralizada
        box_w, box_h = 640, 480
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        # Caixa com borda e sombra simples (use suas funções se preferir)
        draw_rounded_box(screen, box_rect, (250, 250, 255), radius=18, shadow_color=(180, 180, 200), shadow_offset=(6, 6))
        pygame.draw.rect(screen, (200, 200, 220), box_rect, 2, border_radius=18)

        # Título
        draw_text(screen, "Escolha um Pokémon:", SCREEN_WIDTH // 2, box_y + 36,
                  color=(40, 40, 70), current_font=font_xl, center=True)

        # Botões dos pokémons
        buttons = []
        btn_w, btn_h = 420, 48
        gap = 12
        start_y = box_y + 90
        for i, p in enumerate(player.team):
            y = start_y + i * (btn_h + gap)
            rect = pygame.Rect((SCREEN_WIDTH - btn_w) // 2, y, btn_w, btn_h)

            # Cor conforme status
            if p is current_pokemon:
                bg = (80, 150, 230)
            elif not p.is_alive():
                bg = (200, 80, 80)
            else:
                bg = (90, 170, 120)

            # Desenha botão arredondado
            pygame.draw.rect(screen, bg, rect, border_radius=14)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=14)

            # Texto centrado
            status = "ATIVO" if p is current_pokemon else ("FADIGADO" if not p.is_alive() else "OK")
            draw_text(screen,
                      f"{p.name} (Lvl {p.level}) — HP {p.hp}/{p.max_hp} [{status}]",
                      rect.centerx, rect.centery,
                      color=(255, 255, 255), current_font=font_large, center=True)

            buttons.append((rect, p))

        # Botão Voltar (apenas se não for troca forçada)
        back_rect = None
        if current_pokemon is not None and current_pokemon.is_alive():
            back_rect = pygame.Rect((SCREEN_WIDTH - 220) // 2, box_y + box_h - 70, 220, 46)
            pygame.draw.rect(screen, (200, 90, 90), back_rect, border_radius=14)
            pygame.draw.rect(screen, (255, 255, 255), back_rect, 2, border_radius=14)
            draw_text(screen, "Voltar", back_rect.centerx, back_rect.centery,
                      color=(255, 255, 255), current_font=font_large, center=True)
        else:
            draw_text(screen, "Seu Pokémon desmaiou! Escolha o próximo.",
                      SCREEN_WIDTH // 2, box_y + box_h - 64,
                      color=(180, 50, 50), current_font=font_large, center=True)

        # Desenha toast se existir
        if toast_text and now < toast_expire:
            toast_w, toast_h = 420, 40
            toast_x = (SCREEN_WIDTH - toast_w) // 2
            toast_y = box_y + box_h - 120
            toast_rect = pygame.Rect(toast_x, toast_y, toast_w, toast_h)
            pygame.draw.rect(screen, (40, 40, 60), toast_rect, border_radius=12)
            draw_text(screen, toast_text, toast_rect.centerx, toast_rect.centery,
                      color=(255, 255, 255), current_font=font, center=True)
        else:
            toast_text = None

        pygame.display.flip()

        # PROCESSA EVENTOS (loop local)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # ESC também volta (quando permitido)
                if event.key == pygame.K_ESCAPE and back_rect:
                    return current_pokemon, False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # 1) Voltar (retorna IMEDIATAMENTE)
                if back_rect and is_button_clicked(mouse_pos, back_rect):
                    return current_pokemon, False

                # 2) Checa seleção de Pokémon
                clicked_any = False
                for button_rect, p in buttons:
                    if is_button_clicked(mouse_pos, button_rect):
                        clicked_any = True
                        # Se fadigado -> toast e permanece
                        if not p.is_alive():
                            toast_text = f"{p.name} está fadigado!"
                            toast_expire = pygame.time.get_ticks() + TOAST_DURATION_MS
                            # não retornar, apenas permanecer no menu
                            break

                        # Se já é o atual -> toast e permanece (NÃO retorna)
                        if p is current_pokemon:
                            toast_text = f"{p.name} já está na batalha!"
                            toast_expire = pygame.time.get_ticks() + TOAST_DURATION_MS
                            break

                        # Caso válido: retorna o Pokémon selecionado (troca)
                        return p, True

                # Se clicou fora dos botões e fora do back_rect, apenas continua (ignora)
                if not clicked_any:
                    # nada — evita que clique por engano feche a tela
                    pass

        clock.tick(60)

    # fallback de segurança (não costuma chegar aqui)
    if current_pokemon is None or not current_pokemon.is_alive():
        for p in player.team:
            if p.is_alive():
                return p, True

    return current_pokemon, False


# Em battle_system.py

# Modifica a assinatura para receber 'current_zone'
def battle(screen, player, current_pokemon, enemy, current_zone):  # <--- MODIFICADO
    if not current_pokemon.is_alive():
        return "switch_required"

    turn = "player"
    battle_state = "main_menu"

    MENU_X = 20  # Ajustado para novo layout
    MENU_Y = SCREEN_HEIGHT - 170  # Ajustado para novo layout

    MAIN_ACTIONS = {0: "Lutar", 1: "Cura", 2: "Trocar", 3: "Fugir"}  # Texto mais curto para caber

    clock = pygame.time.Clock()

    while current_pokemon.is_alive() and enemy.is_alive():

        mouse_pos = pygame.mouse.get_pos()  # Pega a posição do mouse no início do loop

        # Passa current_zone para draw_battle_screen
        draw_battle_screen(screen, current_pokemon, enemy, current_zone)  # <--- MODIFICADO

        attack_buttons = []
        keys_list = ['Z', 'X', 'C', 'V']
        MENU_W = SCREEN_WIDTH - 40
        MENU_H = 150
        BTN_W = (MENU_W / 2) - 15  # Espaço entre botões
        BTN_H = (MENU_H / 2) - 15
        button_positions = [
            (MENU_X + 10, MENU_Y + 10),
            (MENU_X + 10 + BTN_W + 10, MENU_Y + 10),
            (MENU_X + 10, MENU_Y + 10 + BTN_H + 10),
            (MENU_X + 10 + BTN_W + 10, MENU_Y + 10 + BTN_H + 10)
        ]

        if turn == "player":
            if battle_state == "main_menu":
                display_message(screen, current_pokemon, enemy, f"O que {current_pokemon.name} fará?", current_zone,
                                wait_time=0)  # <--- MODIFICADO

                for i in range(4):
                    x, y = button_positions[i]
                    key = keys_list[i]
                    text = f"[{key}] {MAIN_ACTIONS[i]}"
                    button_rect = pygame.Rect(x, y, BTN_W, BTN_H)  # Cria o Rect

                    # Desenha o botão estilizado
                    draw_button_styled(screen, text, button_rect, BLACK, BATTLE_BUTTON_NORMAL,
                                       BATTLE_BUTTON_HOVER, mouse_pos=mouse_pos,
                                       font_to_use=font_large)  # <--- MODIFICADO
                    attack_buttons.append((button_rect, i))

            elif battle_state == "attack_menu":
                display_message(screen, current_pokemon, enemy, f"Escolha um ataque:", current_zone,
                                wait_time=0)  # <--- MODIFICADO

                attacks_to_show = ["Ataque Básico", "Ataque Especial", "Voltar"]  # Pode adicionar mais aqui se quiser

                for i, attack in enumerate(attacks_to_show):
                    if i >= 3: break  # Limita a 3 botões por enquanto

                    key = keys_list[i]
                    x, y = button_positions[i]

                    button_rect = pygame.Rect(x, y, BTN_W, BTN_H)  # Cria o Rect

                    # Para "Voltar", pode ter uma cor diferente ou sem hover
                    bg_color = GRAY if attack == "Voltar" else BATTLE_BUTTON_NORMAL
                    hover_color = GRAY if attack == "Voltar" else BATTLE_BUTTON_HOVER
                    text_color = BLACK

                    # Desenha o botão estilizado
                    draw_button_styled(screen, text=f"[{key}] {attack}", rect=button_rect,
                                       text_color=text_color, bg_color=bg_color, hover_color=hover_color,
                                       mouse_pos=mouse_pos, font_to_use=font_large)  # <--- MODIFICADO
                    attack_buttons.append((button_rect, i))

            pygame.display.flip()

            action_taken = False
            chosen_index = -1

            while not action_taken and turn == "player":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        for button_rect, idx in attack_buttons:
                            if is_button_clicked(mouse_pos, button_rect):
                                chosen_index = idx
                                action_taken = True
                                break

                    elif event.type == pygame.KEYDOWN:
                        key_map = {pygame.K_z: 0, pygame.K_x: 1, pygame.K_c: 2, pygame.K_v: 3}

                        if event.key in key_map:
                            idx = key_map[event.key]
                            if idx < len(attack_buttons):
                                chosen_index = idx
                                action_taken = True
                                break

                if action_taken:
                    idx = chosen_index

                    if battle_state == "main_menu":
                        # ... (lógica de Lutar, Cura, Trocar, Fugir, como antes) ...
                        if idx == 0:  # Lutar
                            battle_state = "attack_menu"
                            action_taken = False
                            break
                        elif idx == 1:  # Cura
                            if player.items["Poção"] > 0:
                                current_pokemon.hp = min(current_pokemon.hp + 50, current_pokemon.max_hp)
                                player.items["Poção"] -= 1
                                display_message(screen, current_pokemon, enemy, f"{current_pokemon.name} foi curado!",
                                                current_zone, 1000)  # <--- MODIFICADO
                                turn = "enemy"
                            else:
                                display_message(screen, current_pokemon, enemy, "Sem Poções!", current_zone,
                                                1000)  # <--- MODIFICADO
                                action_taken = False
                        elif idx == 2:  # Trocar
                            return "switch_requested"
                        elif idx == 3:  # Fugir
                            if enemy.name == "Boss Final":
                                # CORREÇÃO DO BUG: Retorna o status de bloqueio para que main.py trate.
                                display_message(screen, current_pokemon, enemy, "Você não pode fugir da Batalha Final!",
                                                current_zone, 1000)
                                return "flee_blocked"  # <--- CORREÇÃO APLICADA AQUI

                            elif random.random() < 0.5:
                                return "fled"
                            else:
                                display_message(screen, current_pokemon, enemy, "Fuga falhou!", current_zone,
                                                1000)  # <--- MODIFICADO
                                turn = "enemy"

                    elif battle_state == "attack_menu":
                        if idx == 0 or idx == 1:
                            if idx == 0:
                                damage = random.randint(10, 30)
                                attack_name = "Ataque Básico"
                            else:
                                damage = random.randint(25, 45)
                                attack_name = "Ataque Especial"

                            enemy.take_damage(damage)
                            display_message(screen, current_pokemon, enemy,
                                            f"{current_pokemon.name} usou {attack_name}! Dano: {damage}", current_zone,
                                            1500)  # <--- MODIFICADO

                            turn = "enemy"
                            battle_state = "main_menu"

                            if not enemy.is_alive():
                                current_pokemon.gain_xp(50 * enemy.level)
                                display_message(screen, current_pokemon, enemy,
                                                f"{enemy.name} desmaiou! {current_pokemon.name} ganhou XP!",
                                                current_zone, 2000)  # <--- MODIFICADO
                                return "win"
                        elif idx == 2:  # Voltar
                            battle_state = "main_menu"
                            action_taken = False
                            break

            if turn == "enemy" or action_taken:
                pygame.event.clear()

        else:  # Turno do Inimigo
            damage = random.randint(5, 20)
            if enemy.name == "Boss Final": damage *= 5

            current_pokemon.take_damage(damage)

            display_message(screen, current_pokemon, enemy, f"{enemy.name} atacou! Dano recebido: {damage}",
                            current_zone, 1500)  # <--- MODIFICADO

            if not current_pokemon.is_alive():
                display_message(screen, current_pokemon, enemy, f"Seu Pokémon {current_pokemon.name} desmaiou!",
                                current_zone, 1000)  # <--- MODIFICADO

                new_pokemon = None
                for p in player.team:
                    if p.is_alive():
                        new_pokemon = p
                        break
                if new_pokemon is None: return "lose"
                return "switch_required"

            turn = "player"
            battle_state = "main_menu"

        pygame.display.flip()
        clock.tick(60)

    # ... (Final da função battle) ...
    if current_pokemon.is_alive():
        current_pokemon.gain_xp(50 * enemy.level)
        return "win"
    return "lose"