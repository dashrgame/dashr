import pygame


# Repo config
UPSTREAM_REPO_URL = "https://github.com/dashrgame/dashr.git"

# Window config
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 480
FULLSCREEN = False
UI_SCALE = 1
BACKGROUND_COLOR = (255, 255, 255)

# Debug overlay config
DEBUG_BOX_COLOR = (255, 255, 255)
DEBUG_TEXT_COLOR = (0, 0, 0)

# Title screen config
TITLE_EXTRA_SCALE = 10
SUBTITLE_EXTRA_SCALE = 3
SPLASH_EXTRA_SCALE = 2

SPLASH_MIN = 2.0
SPLASH_MAX = 2.5
SPLASH_ANIMATION_SPEED = 1.0  # seconds for a full cycle

TITLE_COLOR = (255, 255, 255)
SUBTITLE_COLOR = (50, 58, 50)
SPLASH_COLOR = (255, 215, 0)

# Number key mappings for F5 combinations
NUMBER_KEY_MAP = {
    pygame.K_0: "0",
    pygame.K_1: "1",
    pygame.K_2: "2",
    pygame.K_3: "3",
    pygame.K_4: "4",
    pygame.K_5: "5",
    pygame.K_6: "6",
    pygame.K_7: "7",
    pygame.K_8: "8",
    pygame.K_9: "9",
    pygame.K_KP0: "0",
    pygame.K_KP1: "1",
    pygame.K_KP2: "2",
    pygame.K_KP3: "3",
    pygame.K_KP4: "4",
    pygame.K_KP5: "5",
    pygame.K_KP6: "6",
    pygame.K_KP7: "7",
    pygame.K_KP8: "8",
    pygame.K_KP9: "9",
}
