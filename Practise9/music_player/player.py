

import pygame
import os

pygame.init()
pygame.mixer.init()

# Base path
base_path = os.path.dirname(__file__)

# Playlist (files inside "music" folder)
playlist = [
    os.path.join(base_path, "music", "track1.mp3"),
    os.path.join(base_path, "music", "track2.mp3")
]

current = 0
playing = False

# Screen
screen = pygame.display.set_mode((500, 300))
pygame.display.set_caption("Music Player")
font = pygame.font.SysFont(None, 30)

def load_track(index):
    try:
        print("Loading:", playlist[index])
        pygame.mixer.music.load(playlist[index])
        pygame.mixer.music.play()
    except Exception as e:
        print("Error:", e)

running = True

while running:
    screen.fill((0, 0, 0))

    # Display current track
    track_name = os.path.basename(playlist[current])
    text = font.render(f"Track: {track_name}", True, (255, 255, 255))
    screen.blit(text, (50, 120))

    # Controls info
    info = font.render("P=Play S=Stop N=Next B=Back Q=Quit", True, (180, 180, 180))
    screen.blit(info, (20, 250))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Play
                load_track(current)
                playing = True

            elif event.key == pygame.K_s:  # Stop
                pygame.mixer.music.stop()
                playing = False

            elif event.key == pygame.K_n:  # Next
                current = (current + 1) % len(playlist)
                load_track(current)

            elif event.key == pygame.K_b:  # Previous
                current = (current - 1) % len(playlist)
                load_track(current)

            elif event.key == pygame.K_q:  # Quit
                running = False

    pygame.display.update()

pygame.quit()
