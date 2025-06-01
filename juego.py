import pygame
import random
import os
import math
from audio_patch import init_pygame_safely, load_sound_safely, play_sound_safely

# Inicializar Pygame
#pygame.init()
init_pygame_safely()

# Configuración de pantalla
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chimpansini Attack 💣​")

# Cargar imágenes
current_path = os.path.dirname(__file__)
assets_path = os.path.join(current_path, 'assets')
img_path = os.path.join(assets_path, 'images')

# Jugador
raw_player_img = pygame.image.load(os.path.join(img_path, 'player.png')).convert_alpha()
player_img = pygame.transform.scale(raw_player_img, (250, 190))

# Enemigos
enemy_imgs = [
    pygame.transform.scale(pygame.image.load(os.path.join(img_path, 'enemy1.png')).convert_alpha(), (90, 90)),
    pygame.transform.scale(pygame.image.load(os.path.join(img_path, 'enemy2.png')).convert_alpha(), (90, 90)),
    pygame.transform.scale(pygame.image.load(os.path.join(img_path, 'enemy3.png')).convert_alpha(), (90, 90))
]

# Balas
raw_bullet_img = pygame.image.load(os.path.join(img_path, 'bullet.png')).convert_alpha()
bullet_img = pygame.transform.scale(raw_bullet_img, (45, 45))

# Bala de enemigos
raw_enemy_bullet_img = pygame.image.load(os.path.join(img_path, 'Banano.png')).convert_alpha()  # CAMBIAR AQUÍ
enemy_bullet_img = pygame.transform.scale(raw_enemy_bullet_img, (30, 30))  # Tamaño diferente

# Fondo
background = pygame.image.load(os.path.join(img_path, 'background.jpg')).convert()

# Sonidos
#laser_sound = pygame.mixer.Sound(os.path.join(assets_path, 'sounds', 'laser.mp3'))
#explosion_sound = pygame.mixer.Sound(os.path.join(assets_path, 'sounds', 'explosion.mp3'))
laser_sound = load_sound_safely(os.path.join(assets_path, 'sounds', 'laser.mp3'))
explosion_sound = load_sound_safely(os.path.join(assets_path, 'sounds', 'explosion.mp3'))


# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8
        self.lives = 3
        self.score = 0
        self.max_health = 100
        self.health = self.max_health

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def take_damage(self, damage=20):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.lives -= 1
            if self.lives > 0:
                self.health = self.max_health

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.image = enemy_imgs[type]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.direction = 1
        # FRECUENCIA DE DISPARO INICIAL - VALORES MÁS ALTOS = MENOS DISPAROS
        # Cambia estos números: 300 = 5 segundos, 600 = 10 segundos
        self.shoot_timer = random.randint(200,500)  # Tiempo antes del primer disparo
        self.type = type

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1
            self.rect.y += 30
        
        # Sistema de disparo
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            # FRECUENCIA ENTRE DISPAROS - VALORES MÁS ALTOS = MENOS DISPAROS
            # Cambia estos números: 480 = 8 segundos, 720 = 12 segundos
            self.shoot_timer = random.randint(600, 720)  # Tiempo entre disparos
            return True  # Indica que debe disparar
        return False

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Crear una imagen más grande para el jefe (usando enemy1 pero más grande)
        self.image = pygame.transform.scale(enemy_imgs[0], (200, 200))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = 50
        self.speed = 3
        self.direction = 1
        self.health = 500
        self.max_health = 500
        self.shoot_timer = 0
        self.phase = 1  # Fases del jefe

    def update(self):
        # Movimiento del jefe
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH - 50 or self.rect.left <= 50:
            self.direction *= -1
        
        # Sistema de disparo más agresivo
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            if self.phase == 1:
                self.shoot_timer = 30  # Dispara más rápido
            else:
                self.shoot_timer = 15  # Fase 2: mucho más rápido
            return True
        return False

    def take_damage(self, damage=100):
        self.health -= damage
        if self.health <= self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.speed = 5  # Se mueve más rápido en fase 2

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, is_enemy=False):
        super().__init__()
        if is_enemy:
            # USA LA IMAGEN ESPECÍFICA PARA BALAS ENEMIGAS
            self.image = pygame.transform.rotate(enemy_bullet_img, 180)
        else:
            # USA LA IMAGEN DEL JUGADOR
            self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        if is_enemy:
            self.rect.top = y
        else:
            self.rect.bottom = y
        self.speed = speed
        self.is_enemy = is_enemy

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

def draw_health_bar(surface, x, y, health, max_health, width=200, height=20):
    # Barra de fondo (roja)
    pygame.draw.rect(surface, RED, (x, y, width, height))
    # Barra de salud (verde)
    health_width = int((health / max_health) * width)
    pygame.draw.rect(surface, GREEN, (x, y, health_width, height))
    # Borde
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 2)

def create_enemy_wave():
    """Crea una nueva oleada de enemigos"""
    enemies_group = pygame.sprite.Group()
    for row in range(3):
        for column in range(8):
            enemy = Enemy(100 + column * 120, 50 + row * 80, row)
            enemies_group.add(enemy)
    return enemies_group

# Grupos de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
bosses = pygame.sprite.Group()

# Crear jugador
player = Player()
all_sprites.add(player)

# Crear primera oleada de enemigos
enemies = create_enemy_wave()
all_sprites.add(enemies)

# Variables del juego
clock = pygame.time.Clock()
running = True
game_state = "Jugando"  # "playing", "boss", "game_over", "victory"
boss = None
wave_count = 1

# Bucle principal
while running:
    clock.tick(60)
    
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_state in ["Jugando", "Jefe_Final"]:
                bullet = Bullet(player.rect.centerx, player.rect.top, -10)
                all_sprites.add(bullet)
                player_bullets.add(bullet)
               # laser_sound.play()
                play_sound_safely(laser_sound)
            elif event.key == pygame.K_r and game_state == "Juego_Perdido":
                # Reiniciar juego
                game_state = "Jugando"
                player = Player()
                all_sprites = pygame.sprite.Group()
                enemies = create_enemy_wave()
                player_bullets = pygame.sprite.Group()
                enemy_bullets = pygame.sprite.Group()
                bosses = pygame.sprite.Group()
                all_sprites.add(player)
                all_sprites.add(enemies)
                wave_count = 1

    if game_state == "Jugando":
        # Actualizar sprites
        all_sprites.update()
        
        # Disparos de enemigos
        for enemy in enemies:
            if enemy.update():  # Si el enemigo debe disparar
                bullet = Bullet(enemy.rect.centerx, enemy.rect.bottom, 5, True)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)
        
        # Colisiones balas jugador - enemigos
        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
        for hit in hits:
            #explosion_sound.play()
            play_sound_safely(explosion_sound)
            player.score += 100
        
        # Colisiones balas enemigas - jugador
        bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in bullet_hits:
            player.take_damage(20)
        
        # Colisiones jugador - enemigos (contacto directo)
        if pygame.sprite.spritecollide(player, enemies, True):
            player.take_damage(50)
        
        # Verificar si no quedan enemigos
        if len(enemies) == 0:
            wave_count += 1
            if wave_count > 3:  # Después de 3 oleadas, aparece el jefe
                game_state = "Juego_Perdido"
                boss = Boss()
                all_sprites.add(boss)
                bosses.add(boss)
            else:
                enemies = create_enemy_wave()
                all_sprites.add(enemies)
        
        # Verificar game over
        if player.lives <= 0:
            game_state = "Juego_Perdido"
    
    elif game_state == "Jefe_Final":
        # Actualizar sprites
        all_sprites.update()
        
        # Disparos del jefe
        if boss and boss.update():
            # El jefe dispara múltiples balas
            if boss.phase == 1:
                bullet = Bullet(boss.rect.centerx, boss.rect.bottom, 6, True)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)
            else:  # Fase 2: disparo triple
                for i in range(-1, 2):
                    bullet = Bullet(boss.rect.centerx + i * 50, boss.rect.bottom, 6, True)
                    all_sprites.add(bullet)
                    enemy_bullets.add(bullet)
        
        # Colisiones balas jugador - jefe
        boss_hits = pygame.sprite.spritecollide(boss, player_bullets, True)
        for hit in boss_hits:
            boss.take_damage(100)
            #explosion_sound.play()
            play_sound_safely(explosion_sound)
            player.score += 500
        
        # Colisiones balas jefe - jugador
        bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in bullet_hits:
            player.take_damage(30)
        
        # Verificar si el jefe fue derrotado
        if boss.health <= 0:
            boss.kill()
            game_state = "Victoria"
            player.score += 5000
        
        # Verificar game over
        if player.lives <= 0:
            game_state = "Juego_Perdido"
    
    # Dibujar
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    
    # UI
    font = pygame.font.Font(None, 36)
    
    if game_state in ["Jugando", "Jefe_Final"]:
        # Mostrar puntuación y vidas
        score_text = font.render(f"Puntaje: {player.score}", True, WHITE)
        lives_text = font.render(f"Vidas: {player.lives}", True, WHITE)
        wave_text = font.render(f"Ronda: {wave_count}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(wave_text, (10, 90))
        
        # Barra de salud del jugador
        draw_health_bar(screen, 10, HEIGHT - 40, player.health, player.max_health, 200, 20)
        
        # Barra de salud del jefe
        if game_state == "Jefe_Final" and boss:
            draw_health_bar(screen, WIDTH//2 - 150, 10, boss.health, boss.max_health, 300, 30)
            boss_text = font.render("JEFE CHIMPANSINI!", True, YELLOW)
            screen.blit(boss_text, (WIDTH//2 - 100, 50))
    
    elif game_state == "Juego_Perdido":
        game_over_text = font.render("GAME OVER :(", True, RED)
        restart_text = font.render("Presiona R para reiniciar", True, WHITE)
        final_score = font.render(f"Puntuación Final: {player.score}", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH//2 - 100, HEIGHT//2 - 60))
        screen.blit(final_score, (WIDTH//2 - 150, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - 180, HEIGHT//2 + 20))
    
    elif game_state == "victory":
        victory_text = font.render("¡VICTORIA! ¡Derrotaste a los Chimpansini!", True, GREEN)
        final_score = font.render(f"Puntuación Final: {player.score}", True, WHITE)
        restart_text = font.render("Presiona R para reiniciar", True, WHITE)
        
        screen.blit(victory_text, (WIDTH//2 - 250, HEIGHT//2 - 60))
        screen.blit(final_score, (WIDTH//2 - 150, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - 180, HEIGHT//2 + 20))
    
    pygame.display.flip()

pygame.quit()
