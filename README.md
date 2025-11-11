# 🎮 PokePY
---
> 
> "Lógica de Programação II"
> 
> "Alunos: Maycon Willians, Jéssica Freitas, João Lucas, Eduardo Lopes e Luiz Ricardo"
> 
> **Este é um RPG 2D de simulação de Pokémon desenvolvido em Python com a biblioteca Pygame.
O jogo foca na gestão do time, exploração por zonas e batalhas de turno contra inimigos selvagens. Ele apresenta um sistema de UI moderna com menus estilizados  e uma lógica de progressão funcional, onde seus Pokémon ganham XP, sobem de nível, evoluem e têm seu poder de ataque escalado, tornando o treinamento essencial para avançar pelas diferentes zonas de dificuldade. O sistema inclui gerenciamento de itens (Poções, Repelentes) e uma mecânica de troca e fuga durante o combate.**

## ✨ Funcionalidades

O jogo implementa um sistema completo de exploração, gestão e batalha:

### ⚔️ Sistema de Batalha (battle_system.py)
* **Interface Estilizada:** Menus de ação (Lutar, Cura, Trocar, Fugir) desenhados com caixas arredondadas e feedback visual de **hover** e **seleção** (usando funções como `draw_button_styled`).
* **Status Dinâmico:** Barras de HP que mudam de cor conforme a saúde do Pokémon.
* **Dano Escalonado:** O dano de ataque agora é **escalado pelo Nível** do Pokémon do jogador, tornando o treinamento significativo.
* **Troca de Pokémon:** Tela dedicada (`select_pokemon_in_battle`) para gerenciamento do time com *toasts* (mensagens curtas) de feedback.

### 📈 Progressão (classes.py)
1.  **Ganhos de XP e Nível:** Aumento de **HP Máximo** e **HP Atual** (+20) a cada nível.
2.  **Evolução:** Ao atingir Nível 3 (`level % 3 == 0`), o Pokémon ganha um bônus de **+50 HP** e garante o `Ataque Especial`.
3.  **Sistema de Itens:** Uso de `Poção` (cura 50 HP) e `Repelente` (bloqueia encontros).

### 🗺️ Exploração e Zonas
* **Zonas de Batalha:** O inimigo encontrado depende da `Zone` atual, cada uma com níveis e tipos específicos de Pokémon (`Fogo`, `Água`, `Pedra`, etc.).
* **Encontros em Grama:** Utiliza arquivos de **máscara** para detectar colisões com áreas de grama.

---

## 🛠️ Tecnologias e Ferramentas

| Categoria | Tecnologia | Uso no Projeto |
| :--- | :--- | :--- |
| **Linguagem Principal** | Python | Lógica do jogo e classes. |
| **Framework de Jogo** | Pygame | Renderização gráfica, loop de jogo e eventos. |
| **Assets/Estilo** | PNGs/Masks | Sprites, fundos e detecção de área de grama. |

**Stack de Desenvolvimento:**

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge">

---

## 📂 Estrutura de Arquivos

| Arquivo | Descrição |
| :--- | :--- |
| `classes.py` | Define as classes base: **Pokemon**, **Player** e **Zone**. Contém a lógica de progressão (XP, Nível, Evolução) e o carregamento de assets. |
| `battle_system.py` | Implementa a função principal de **batalha** (`battle`) e toda a lógica de **UI dos menus de combate**. |
| `main.py` (assumido) | O ponto de entrada do jogo. Gerencia o *game loop*, a movimentação e a transição entre exploração e batalha. |
| `backgrounds/` | Armazena as imagens de fundo para as diferentes zonas de batalha (zone1_bg.png, zone2_bg.png, etc.). |
| `mapa/` | Contém os arquivos de máscara de grama (mapa_zonaX_mask.png) usados para detectar colisões e encontros aleatórios no mapa de exploração. |
| `sprites/` | Armazena todos os sprites dos Pokémon (frontais e traseiros) e os assets do Avatar do Jogador e dos Tiles do mapa. |

---

## ⚙️ Como Rodar o Projeto

### **Pré-requisitos**

Certifique-se de ter **Python 3.x14 ou Superior** e o pacote **Pygame** instalados.

Instala o Pygame (Obrigatório)
pip install pygame

Clone o repositório:

Bash

1- Clone o repositório:
git clone https://github.com/FireTchuGueras/PokePY
cd [PokePY]

2- Execute o arquivo principal:
python main.py


