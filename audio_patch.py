import pygame
import os

def init_pygame_safely():
    """Inicializa Pygame de forma segura para entornos Docker"""
    try:
        # Intentar inicializar con audio
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.init()
        print("Pygame inicializado con audio")
    except pygame.error:
        try:
            # Si falla, inicializar sin audio
            pygame.quit()
            os.environ['SDL_AUDIODRIVER'] = 'dummy'
            pygame.init()
            print("Pygame inicializado sin audio (modo silencioso)")
        except pygame.error as e:
            print(f"Error al inicializar Pygame: {e}")
            raise

def load_sound_safely(sound_path):
    """Carga sonidos de forma segura"""
    try:
        return pygame.mixer.Sound(sound_path)
    except pygame.error:
        print(f"No se pudo cargar el sonido: {sound_path}")
        return None

def play_sound_safely(sound):
    """Reproduce sonidos de forma segura"""
    try:
        if sound and pygame.mixer.get_init():
            sound.play()
    except pygame.error:
        pass  # Silenciosamente ignorar errores de audio
