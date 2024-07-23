import pygame
from pygame.locals import *
import random
import sys

# Inisialisasi Pygame
pygame.init()
pygame.mixer.init()

# Mengatur frame rate
clock = pygame.time.Clock()
fps = 60

# Mengatur ukuran layar
screen_width = 864
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bee')

# Memuat font khusus
font_path = 'Handjet-SemiBold.ttf'  # Path ke font khusus Anda
font = pygame.font.Font(font_path, 40)
regular_font = pygame.font.Font(font_path, 35)

# Mengatur warna
white = (255, 255, 255)
black = (0, 0, 0)
yellow = (255, 255, 0)

# Mengatur variabel permainan
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
logs_gap = 100
logs_frequency = 1500  # milliseconds
last_logs = pygame.time.get_ticks() - logs_frequency
score = 0
pass_logs = False
high_score = 0

# Memuat gambar
bg = pygame.image.load('img/background2.jpg')
ground_img = pygame.image.load('img/ground.png')
ground_img = pygame.transform.scale(ground_img, (890, 102))  # Mengubah ukuran ground_img
button_img = pygame.image.load('img/restart.png')
quit1_button_img = pygame.image.load('img/quit.png')
bee_image = pygame.image.load('img/bee1.png')
header_img = pygame.image.load('img/text.png')
header_img = pygame.transform.scale(header_img, (400, 150))

# Memuat suara
button_click_sound = pygame.mixer.Sound('sounds/button.wav')
game_music = pygame.mixer.Sound('sounds/game_music.mp3')
bee_fly_sound = pygame.mixer.Sound('sounds/bee_fly.wav')
score_sound = pygame.mixer.Sound('sounds/score.wav')  # Tambahkan suara skor

# Fungsi untuk menggambar teks di layar
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Fungsi untuk mereset permainan
def reset_game():
    global score, scroll_speed, logs_frequency
    logs_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    scroll_speed = 4  # Reset kecepatan scroll saat game direset
    logs_frequency = 1500  # Reset frekuensi logs saat game direset
    # Memainkan musik latar lagi
    pygame.mixer.Sound.play(game_music, loops=-1)
    return score

# Kelas Tombol
class Button():
    def __init__(self, x, y, image, scale=1):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False
        # Mendapatkan posisi mouse
        pos = pygame.mouse.get_pos()
        # Memeriksa kondisi mouseover dan klik
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                # Memainkan suara klik tombol
                button_click_sound.play()
                action = True
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        # Menggambar tombol
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# Memuat gambar latar belakang
background = pygame.image.load('img/background.jpg')

# Fungsi untuk menampilkan menu utama
def main_menu():
    # Memuat gambar tombol
    play_button_img = pygame.image.load('img/play.png')
    quit_button_img = pygame.image.load('img/quit.png')

    # Menghitung posisi tombol untuk menempatkannya di tengah
    button_width = 200
    button_height = 80
    play_button_x = screen_width // 2 - button_width // 2
    play_button_y = screen_height // 2 - button_height // 2 - 50
    quit_button_x = screen_width // 2 - button_width // 2
    quit_button_y = screen_height // 2 - button_height // 2 + 50

    # Membuat tombol
    play_button = Button(play_button_x, play_button_y, play_button_img, scale=1)
    quit_button = Button(quit_button_x, quit_button_y, quit_button_img, scale=1)

    # Memainkan musik latar
    pygame.mixer.Sound.play(game_music, loops=-1)

    while True:
        screen.blit(background, (0, 0))

        # Menggambar gambar header di atas tombol "Play"
        header_x = screen_width // 2 - header_img.get_width() // 2
        header_y = play_button_y - header_img.get_height() - 20
        screen.blit(header_img, (header_x, header_y))

        if play_button.draw():
            return
        if quit_button.draw():
            pygame.quit()
            sys.exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

# class lebah
class Bee(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/bee{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        if flying:
            # Menerapkan gravitasi
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < screen_height - ground_img.get_height():
                self.rect.y += int(self.vel)
            else:
                self.rect.bottom = screen_height - ground_img.get_height()
                self.vel = 0

        if not game_over:
            # Lompat
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
                # Memainkan suara lebah terbang
                bee_fly_sound.play()
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Mengatur animasi
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # Memutar lebah
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # Mengarahkan lebah ke tanah
            self.image = pygame.transform.rotate(self.images[self.index], -90)

# Logs
class Logs(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/logs.png")
        self.rect = self.image.get_rect()
        # Variabel posisi menentukan apakah logs berasal dari bawah atau atas
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(logs_gap / 1)]
        elif position == -1:
            self.rect.topleft = [x, y + int(logs_gap / 1)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

# Membuat grup sprite
logs_group = pygame.sprite.Group()
bee_group = pygame.sprite.Group()
flappy = Bee(100, int(screen_height / 2))
bee_group.add(flappy)

# Menghitung posisi tombol restart di tengah layar
button_x = screen_width // 2 - button_img.get_width() // 2
button_y = screen_height // 2 - button_img.get_height() // 2

# Menempatkan di bawah tombol restart
quit1_button_x = screen_width // 2 - button_img.get_width() // 2
quit1_button_y = button_y + button_img.get_height() + 20

# Membuat instance tombol restart di posisi tengah
button = Button(button_x, button_y, button_img)

# Menempatkan di bawah tombol restart
quit1_button = Button(quit1_button_x, quit1_button_y, quit1_button_img)

# Menampilkan menu utama sebelum permainan dimulai
main_menu()

# Loop utama permainan
run = True
while run:
    clock.tick(fps)

    # Menggambar latar belakang
    screen.blit(bg, (0, 0))

    logs_group.draw(screen)
    bee_group.draw(screen)
    bee_group.update()

    # Menggambar dan menggulirkan tanah
    screen.blit(ground_img, (ground_scroll, screen_height - ground_img.get_height()))
    screen.blit(ground_img, (ground_scroll + 890, screen_height - ground_img.get_height()))

    # Menggulung tanah hanya jika game tidak game over
    if not game_over and flying:
        ground_scroll -= scroll_speed
    if abs(ground_scroll) > 890:
        ground_scroll = 0

    # Memeriksa skor
    if len(logs_group) > 0:
        if bee_group.sprites()[0].rect.left > logs_group.sprites()[0].rect.left \
                and bee_group.sprites()[0].rect.right < logs_group.sprites()[0].rect.right \
                and not pass_logs:
            pass_logs = True
        if pass_logs:
            if bee_group.sprites()[0].rect.left > logs_group.sprites()[0].rect.right:
                score += 5
                # Memainkan suara skor
                score_sound.play()
                pass_logs = False

    # Menampilkan skor
    draw_text(f'{score}', regular_font, white, int(screen_width / 2) - 20, button_y - 330)

    # Menambah kecepatan scroll setiap kali skor bertambah kelipatan 10
    if score > 0 and score % 10 == 0:
        scroll_speed = 4 + score // 10
        logs_frequency = max(1000, 1500 - (score // 10) * 100)  # Mengurangi frekuensi logs seiring peningkatan skor

    # Memeriksa tabrakan
    if pygame.sprite.groupcollide(bee_group, logs_group, False, False) or flappy.rect.top < 0:
        game_over = True
    if flappy.rect.bottom >= screen_height - ground_img.get_height():
        game_over = True
        flying = False

    if flying and not game_over:
        # Menghasilkan logs baru
        time_now = pygame.time.get_ticks()
        if time_now - last_logs > logs_frequency:
            logs_height = random.randint(-100, 100)
            btm_logs = Logs(screen_width, int(screen_height / 2) + logs_height, -1)
            top_logs = Logs(screen_width, int(screen_height / 2) + logs_height, 1)
            logs_group.add(btm_logs)
            logs_group.add(top_logs)
            last_logs = time_now

        logs_group.update()

    # Memeriksa kondisi game over dan menggambar tombol restart dan quit
    if game_over:
        pygame.mixer.Sound.stop(game_music)
        if score > high_score:
            high_score = score
        draw_text(f'SCORE : {score}', regular_font, white, int(screen_width / 2) - 80, button_y - 120)
        draw_text(f'HIGH SCORE : {high_score}', regular_font, white, int(screen_width / 2) - 80, button_y - 60)
        if button.draw():
            game_over = False
            score = reset_game()
        if quit1_button.draw():
            pygame.quit()
            sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    pygame.display.update()

pygame.quit()
