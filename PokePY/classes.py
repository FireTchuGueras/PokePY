import pygame
import random
import os
from PIL import Image


# --- CONSTANTES GLOBAIS ---
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 640

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 150, 0)
GRAY = (200, 200, 200)
BUTTON_COLOR = (100, 100, 255)
SELECTED_COLOR = (0, 255, 0)
LIGHT_GRAY = (220, 220, 220)
DARK_BLUE = (50, 50, 150)
ITEM_CAPS = {"Poção": 5, "Repelente": 1}

BG_COLOR_MENU = (34, 40, 49)       # Azul escuro/grafite para o fundo
MENU_BOX_COLOR = (240, 240, 240)   # Branco-gelo para a caixa do menu
TEXT_COLOR_DARK = (50, 50, 50)     # Texto escuro para caixas claras
TEXT_COLOR_LIGHT = (238, 238, 238) # Texto claro para botões escuros

SHADOW_COLOR_DARK = (20, 20, 20)      # Sombra escura (para a caixa branca)
SHADOW_COLOR_LIGHT = (180, 180, 180)  # Sombra clara (para os botões brancos)

BUTTON_NORMAL_COLOR = (255, 255, 255) # Botão branco
BUTTON_HOVER_COLOR = (220, 220, 255)  # Levemente azulado/roxo ao passar o mouse
SELECTED_COLOR_LIGHT = (180, 255, 180) # Verde claro para seleção
CONFIRM_COLOR_OK = (76, 175, 80)       # Verde para confirmar
CONFIRM_COLOR_BAD = (244, 67, 54)      # Vermelho para "não pronto"

BATTLE_BG_OVERLAY = (0, 0, 0, 100) # Overlay escuro para fundos mais claros
BATTLE_MENU_BG = (230, 230, 230)   # Fundo do menu de batalha (quase branco)
BATTLE_MENU_BORDER = (180, 180, 180) # Borda do menu
BATTLE_BUTTON_NORMAL = (255, 255, 255) # Botão de ataque/ação
BATTLE_BUTTON_HOVER = (200, 200, 200)  # Botão ao passar o mouse
BATTLE_BUTTON_SELECTED = (150, 255, 150) # Botão selecionado (verde claro)
HP_BAR_EMPTY = (180, 50, 50)       # Vermelho mais escuro para HP vazio
HP_BAR_LOW = (255, 150, 50)        # Laranja para HP baixo
HP_BAR_MEDIUM = (200, 200, 50)     # Amarelo para HP médio
HP_BAR_FULL = (100, 200, 100)      # Verde para HP cheio
# -----------------------------------------------

# --- FUNDOS DAS ZONAS ARENA ---
BATTLE_BACKGROUNDS = {
    "Zona 1": "backgrounds/zone1_bg.png",
    "Zona 2": "backgrounds/zone2_bg.png",
    "Zona 3": "backgrounds/zone3_bg.png",
}

LOADED_BACKGROUNDS = {}

def load_background(zone_name):
    """Carrega (ou obtém do cache) a imagem de fundo da batalha para a zona."""
    if zone_name in LOADED_BACKGROUNDS:
        return LOADED_BACKGROUNDS[zone_name]

    if zone_name in BATTLE_BACKGROUNDS:
        file_name = BATTLE_BACKGROUNDS[zone_name]
        try:
            image = pygame.image.load(file_name).convert() # Não precisamos de alpha aqui
            image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            LOADED_BACKGROUNDS[zone_name] = image
            return image
        except pygame.error as e:
            print(f"Erro ao carregar fundo {file_name}: {e}")
            return None
        except FileNotFoundError:
            print(f"Arquivo de fundo não encontrado: {file_name}")
            return None
    return None

ITEM_CAPS = {"Poção": 5, "Repelente": 1}

# Dicionário de Nomes de Inimigos por Tipo
ENEMY_NAMES_BY_TYPE = {
    "Fogo": ["Vulpix", "Ponyta", "Growlithe", "Charmander"],
    "Água": ["Magikarp", "Poliwag", "Horsea", "Shellder", "Squirtle"],
    "Planta": ["Oddish", "Bellsprout", "Weepinbell", "Bulbasaur"],
    "Elétrico": ["Voltorb", "Electabuzz", "Jolteon", "Pikachu"],
    "Pedra": ["Geodude", "Onix", "Graveler", "Rhyhorn"],
    "Gelo": ["Articuno", "Cloyster", "Dewgong"]
}


# --- FUNÇÕES DE SPRITE ---

# Mapeamento de Sprites ajustado para a pasta /sprites, INCLUINDO Avatar e Inimigos
SPRITE_MAP = {
    # Avatar do Jogador na exploração
    "Player Avatar": {"front": "sprites/player_avatar.png"},

    # Sprites do Jogador na Batalha (Front e Back)
    "Bulbasaur": {"front": "sprites/bulbasaur_front.png", "back": "sprites/bulbasaur_back.png"},
    "Charmander": {"front": "sprites/charmander_front.png", "back": "sprites/charmander_back.png"},
    "Squirtle": {"front": "sprites/squirtle_front.png", "back": "sprites/squirtle_back.png"},
    "Pikachu": {"front": "sprites/pikachu_front.png", "back": "sprites/pikachu_back.png"},
    "Geodude": {"front": "sprites/geodude_front.png", "back": "sprites/geodude_back.png"},
    "Boss Final": {"front": "sprites/boss_final.png", "back": "sprites/boss_final.png"},

    # Sprites dos Inimigos (Apenas Front)
    "Vulpix": {"front": "sprites/vulpix_front.png"},
    "Ponyta": {"front": "sprites/ponyta_front.png"},
    "Growlithe": {"front": "sprites/growlithe_front.png"},
    "Magikarp": {"front": "sprites/magikarp_front.png"},
    "Poliwag": {"front": "sprites/poliwag_front.png"},
    "Oddish": {"front": "sprites/oddish_front.png"},
    "Voltorb": {"front": "sprites/voltorb_front.png"},
    "Electabuzz": {"front": "sprites/electabuzz_front.png"},
    "Onix": {"front": "sprites/onix_front.png"},
    "Cloyster": {"front": "sprites/cloyster_front.png"},
    # Adicione mais inimigos aqui conforme precisar
}

LOADED_SPRITES = {}
def load_sprite(pokemon_name, direction="front", scale=2):
    """
    Carrega (ou obtém do cache) o sprite.
    Retorna o objeto Surface do Pygame ou None se não for encontrado.
    """
    key = f"{pokemon_name}_{direction}"

    if key in LOADED_SPRITES:
        return LOADED_SPRITES[key]

    # Para o Player Avatar, o direction sempre será "front" no mapeamento
    if pokemon_name == "Player Avatar":
        direction = "front"
        scale = 1  # Avatar geralmente é menor

    # Verifica se o sprite está mapeado
    if pokemon_name in SPRITE_MAP and direction in SPRITE_MAP[pokemon_name]:
        file_name = SPRITE_MAP[pokemon_name][direction]

        try:
            # Carregamento e conversão de imagem com transparência
            image = pygame.image.load(file_name).convert_alpha()

            # Redimensionamento
            w, h = image.get_size()
            image = pygame.transform.scale(image, (w * scale, h * scale))

            LOADED_SPRITES[key] = image
            return image

        except pygame.error as e:
            # Falha ao carregar
            # print(f"Erro Pygame ao carregar {file_name}: {e}")
            return None
        except FileNotFoundError:
            # Arquivo não encontrado
            # print(f"Arquivo não encontrado: {file_name}")
            return None

    return None

# ---------------- SPRITES DO JOGADOR (Avatar com Direções) ---------------- #

def load_player_sprite(direction="Frente", frame=0):
    """
    Carrega o sprite do jogador com base na direção e no frame da animação.
    direction: 'Frente', 'Costas', 'Esquerda', 'Direita'
    frame: índice do sprite (0 = parado)
    """
    base_path = "sprites/Avatar"
    folder = os.path.join(base_path, direction)

    # Se o frame for 0, usa o sprite parado
    if frame == 0:
        file_name = f"SpriteParado{direction}.png"
    else:
        file_name = f"New Piskel-{frame}.png"

    full_path = os.path.join(folder, file_name)

    try:
        image = pygame.image.load(full_path).convert_alpha()
        image = pygame.transform.scale(image, (64, 64))  # ajuste do tamanho
        return image
    except FileNotFoundError:
        print(f"Sprite não encontrado: {full_path}")
        return None

# ----------------------------------------




# ----------------- TILES DO MAPA ----------------- #

TILE_CACHE = {}


def load_tile(name):
    """Carrega uma textura de tile e guarda em cache."""
    if name in TILE_CACHE:
        return TILE_CACHE[name]

    path = os.path.join("sprites", "tiles", name)
    try:
        image = pygame.image.load(path).convert_alpha()
        TILE_CACHE[name] = image
        return image
    except FileNotFoundError:
        print(f"Tile não encontrado: {path}")
        return None


class Pokemon:
    def __init__(self, name, type_, level=1, hp=100, attacks=None):
        self.name = name
        self.type = type_
        self.level = level
        self.hp = hp
        self.max_hp = hp
        self.xp = 0
        self.attacks = attacks or ["Ataque Básico", "Ataque Especial", "Curar (Poção)", "Trocar", "Fugir"]
        self.evolution_stage = 0

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.level * 100:
            self.level += 1
            self.xp = 0
            self.hp = min(self.hp + 20, self.max_hp + 20)
            self.max_hp += 20
            if self.level % 3 == 0 and self.evolution_stage < 1:
                self.evolve()

    def evolve(self):
        self.evolution_stage += 1
        self.hp += 50
        self.max_hp += 50
        if "Ataque Especial" not in self.attacks:
            self.attacks.insert(1, "Ataque Especial")

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def is_alive(self):
        return self.hp > 0


# Pokémon disponíveis para o jogador
POKEMON_OPTIONS = [
    Pokemon("Bulbasaur", "Planta"),
    Pokemon("Charmander", "Fogo"),
    Pokemon("Squirtle", "Água"),
    Pokemon("Pikachu", "Elétrico"),
    Pokemon("Geodude", "Pedra")
]


class Player:
    def __init__(self):
        self.team = []
        self.items = {"Poção": 5, "Repelente": 1}
        self.repelente_active = False
        self.repelente_end_time = 0
        self.repelente_pending = False
        self.x, self.y = 50, SCREEN_HEIGHT // 2
        self.zone = 0

    def add_pokemon(self, pokemon):
        if len(self.team) < 3:
            self.team.append(pokemon)

    def use_item(self, item):
        if self.items.get(item, 0) > 0:
            self.items[item] -= 1
            if item == "Repelente":
                self.repelente_pending = True
            return True
        return False


class Zone:
    def __init__(self, name, enemy_types, difficulty, grass_areas):
        self.name = name
        self.enemy_types = enemy_types
        self.difficulty = difficulty
        self.grass_areas = grass_areas

        self.enemies = []
        # Gerar a pool inicial de inimigos para a zona
        for enemy_type in enemy_types:
            # Filtra apenas os inimigos que têm sprites mapeados
            mappable_enemies = [
                name for name in ENEMY_NAMES_BY_TYPE.get(enemy_type, [])
                if name in SPRITE_MAP
            ]

            # Adiciona 5 inimigos aleatórios de cada tipo mapeado na zona
            for _ in range(5):
                if mappable_enemies:
                    enemy_name = random.choice(mappable_enemies)
                    self.enemies.append(
                        Pokemon(enemy_name, enemy_type, level=difficulty)
                    )

    def random_encounter(self):
        encounter_rate = 0.015
        if self.name == "Zona 3":
            encounter_rate = 0.025

        if random.random() < encounter_rate and self.enemies:
            original_enemy = random.choice(self.enemies)

            # Garante que o inimigo gerado é uma nova instância
            new_enemy = Pokemon(
                original_enemy.name,
                original_enemy.type,
                original_enemy.level,
                original_enemy.max_hp,
                original_enemy.attacks[:]
            )
            return new_enemy
        return None

    def random_item(self, player_x):
        if random.random() < 0.2:
            if self.name == "Zona 3" and player_x > SCREEN_WIDTH - 180:
                return None
            return random.choice(["Poção", "Repelente"])
        return None

    def is_in_grass(self, x, y):
        """
        Detecta se o jogador está sobre a grama usando o arquivo mask da zona.
        As áreas visíveis da máscara representam grama (fundo transparente).
        """
        zona_numero = self.name.split()[-1]  # "1", "2", "3"
        mask_path = f"mapa/mapa_zona{zona_numero}_mask.png"

        try:
            mask_img = pygame.image.load(mask_path).convert_alpha()
            width, height = mask_img.get_size()

            # Garante que x e y estão dentro da imagem
            if 0 <= int(x) < width and 0 <= int(y) < height:
                pixel = mask_img.get_at((int(x), int(y)))
                # pixel.a > 10 significa que o pixel não é totalmente transparente
                return pixel.a > 10
            else:
                return False
        except Exception as e:
            print(f"Erro ao verificar máscara da grama: {e}")
            return False


# Zonas (Com layout da Zona 3 simplificado no centro)
ZONES = [
    # Zona 1: Fogo e Água, Nível 1
    Zone("Zona 1", ["Fogo", "Água"], 1, [
        (50, 100, 150, 150),
        (450, 100, 150, 150),
        (200, 400, 150, 150),
        (650, 0, 150, 600)
    ]),

    # Zona 2: Planta e Elétrico, Nível 2
    Zone("Zona 2", ["Planta", "Elétrico"], 2, [
        # Faixa superior de grama
        (50, 50, 700, 150),

        # Fileiras organizadas de blocos de grama
        (100, 200, 150, 100),
        (300, 200, 150, 100),
        (500, 200, 150, 100),

        (100, 350, 150, 100),
        (300, 350, 150, 100),
        (500, 350, 150, 100),

        # Pequenos patches extras (variação natural)
        (150, 500, 100, 60),
        (400, 500, 200, 60)
    ]),

    # Zona 3: Pedra (Caminho totalmente livre no centro)
    Zone("Zona 3", ["Pedra"], 3, [
        (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2 - 50),  # Grama Superior
        (0, SCREEN_HEIGHT // 2 + 50, SCREEN_WIDTH, SCREEN_HEIGHT // 2 - 50)  # Grama Inferior
    ])
]