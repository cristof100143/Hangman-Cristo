import pygame
import math
import random
import sys
import os

# Initialize Pygame and screen
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game - By Cristo")

# Load fonts
BOX_FONT_PATH = "boxy-bold.ttf"
LETTER_FONT = pygame.font.Font(BOX_FONT_PATH, 20)
WORD_FONT = pygame.font.Font(BOX_FONT_PATH, 30)
TITLE_FONT = pygame.font.Font(BOX_FONT_PATH, 50)

# Load images and sounds
images = [pygame.image.load(f"hangman{i}.png") for i in range(7)]
pygame.mixer.init()
pygame.mixer.music.load("music.ogg")
pygame.mixer.music.play(-1)  # Loop background music
correct_sound = pygame.mixer.Sound("collectheart.ogg")
wrong_sound = pygame.mixer.Sound("dead.ogg")

# Game variables
hangman_status = 0
categories = ["Science", "History", "Technology"]
category = ""
word = ""
guessed = []
clue_used = False  # Tracks whether the hint button has been used

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (170, 170, 170)
BLUE = (0, 100, 255)
YELLOW = (255, 223, 0)

# Category selection menu
def draw_category_menu(selected_index):
    win.fill(WHITE)
    title = TITLE_FONT.render("SELECT A CATEGORY", True, BLACK)
    win.blit(title, (WIDTH / 2 - title.get_width() / 2, 50))

    for i, cat in enumerate(categories):
        color = BLUE if i == selected_index else BLACK
        category_text = WORD_FONT.render(cat, True, color)
        win.blit(category_text, (WIDTH / 2 - category_text.get_width() / 2, 150 + i * 50))

    instructions = LETTER_FONT.render("W/S to navigate, SPACE to select, ENTER for 1 Hint", True, GRAY)
    win.blit(instructions, (WIDTH / 2 - instructions.get_width() / 2, 400))
    pygame.display.update()

def select_category():
    global category, word
    selected_index = 0
    while True:
        draw_category_menu(selected_index)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_PAGEUP):
                    selected_index = (selected_index - 1) % len(categories)
                elif event.key in (pygame.K_s, pygame.K_PAGEDOWN):
                    selected_index = (selected_index + 1) % len(categories)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    category = categories[selected_index]
                    word = random.choice(get_word_list(category))
                    return

def get_word_list(selected_category):
    word_lists = {
        "Science": ["ASTEROID", "EVOLUTION", "PHOTOSYNTHESIS"],
        "History": ["REVOLUTION", "PYRAMIDS", "NAPOLEON"],
        "Technology": ["ALGORITHM", "MICROPROCESSOR", "ENCRYPTION"],
    }
    return word_lists[selected_category]

# Main game drawing function
def draw():
    win.fill(WHITE)

    # Title and category
    title = TITLE_FONT.render("HANGMAN GAME!", True, BLACK)
    win.blit(title, (WIDTH / 2 - title.get_width() / 2, 10))
    category_text = WORD_FONT.render(f"Category: {category}", True, GRAY)
    win.blit(category_text, (WIDTH / 2 - category_text.get_width() / 2, 70))

    # Guessing word (moved to the right)
    display_word = " ".join([letter if letter in guessed else "_" for letter in word])
    word_text = WORD_FONT.render(display_word, True, BLACK)
    small_word_font = pygame.font.Font(BOX_FONT_PATH, 20)  # Adjust size
    word_text = small_word_font.render(display_word, True, BLACK)
    win.blit(word_text, (WIDTH - 400, 200))  # Shift slightly to the left

    # Hint button
    pygame.draw.rect(win, YELLOW, (WIDTH - 2800, 345, 250, 40))  # Yellow button for hint
    hint_text = LETTER_FONT.render("HINT (Enter)", True, BLACK)
    win.blit(hint_text, (WIDTH - 250, 350))

    # Draw letters
    for letter in letters:
        x, y, ltr, visible = letter
        if visible:
            pygame.draw.circle(win, BLACK, (x, y), RADIUS, 3)
            text = LETTER_FONT.render(ltr, True, BLACK)
            win.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))
        else:
            pygame.draw.circle(win, GRAY, (x, y), RADIUS, 0)

    # Hangman image (moved left)
    win.blit(images[hangman_status], (50, 100))

    # Lives remaining (under hangman)
    lives = LETTER_FONT.render(f"Lives Remaining: {6 - hangman_status}", True, RED)
    win.blit(lives, (50, 350))

    pygame.display.update()

def display_message(message, color):
    pygame.time.delay(1000)
    win.fill(WHITE)
    small_message_font = pygame.font.Font(BOX_FONT_PATH, 17)  # Adjust size as needed
    message_text = small_message_font.render(message, True, color)
    win.blit(message_text, (WIDTH / 2 - message_text.get_width() / 2, HEIGHT / 2 - message_text.get_height() / 2 + 10))  # Slight downward adjustment
    pygame.display.update()
    pygame.time.delay(3000)

# Main game loop
def main():
    global hangman_status, guessed, clue_used
    guessed = []
    hangman_status = 0
    clue_used = False
    FPS = 60
    clock = pygame.time.Clock()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                if WIDTH - 200 <= m_x <= WIDTH - 50 and 350 <= m_y <= 490:  # Hint button
                    if not clue_used and hangman_status < 6:
                        use_clue()
                for letter in letters:
                    x, y, ltr, visible = letter
                    if visible and math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2) < RADIUS:
                        letter[3] = False
                        guessed.append(ltr)
                        check_guess(ltr)
            if event.type == pygame.KEYDOWN:
                if event.unicode.isalpha():
                    letter = event.unicode.upper()
                    for l in letters:
                        if l[2] == letter and l[3]:  # Check if the letter is visible
                            l[3] = False  # Set the letter to invisible
                            guessed.append(letter)
                            check_guess(letter)
                            break  # Stop looping once the letter is found

                if event.key == pygame.K_RETURN and not clue_used and hangman_status < 6:
                    use_clue()

        draw()

        if all(letter in guessed for letter in word):
            correct_sound.play()
            display_message("You WON! Press R to Restart", BLACK)
            break
        if hangman_status == 6:
            wrong_sound.play()
            display_message(f"You LOST! The word was {word}. Press R to Restart", RED)
            break

    restart_game()

def check_guess(letter):
    global hangman_status
    if letter in word:
        correct_sound.play()
    else:
        wrong_sound.play()
        hangman_status += 1

def use_clue():
    global hangman_status, clue_used
    clue_used = True
    hangman_status += 1  # Costs a limb
    for letter in word:
        if letter not in guessed:
            guessed.append(letter)
            break

def restart_game():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    select_category()
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Button variables
RADIUS = 20
GAP = 15
letters = []
startx = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
starty = 450
A = 65
for i in range(26):
    x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
    y = starty + ((i // 13) * (GAP + RADIUS * 2))
    letters.append([x, y, chr(A + i), True])

# Start the game
select_category()
main()
