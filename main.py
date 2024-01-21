import pygame
import pickle
import math
import os
import time
from data import Birb, Pipe

# Init pygame
pygame.init()
pygame.mixer.init()
Running :bool = True
DISPLAY_X, DISPLAY_Y = 288, 512
window :pygame.surface = pygame.display.set_mode((DISPLAY_X, DISPLAY_Y))
pygame.display.set_caption("Flabby Birb")
clock = pygame.time.Clock()

# Init assets
FONT        :pygame.font        = pygame.font.Font("assets/flappy-font.ttf", 20)
FONT_L      :pygame.font        = pygame.font.Font("assets/flappy-font.ttf", 30)
BG_IMG      :pygame.surface     = pygame.transform.scale_by(pygame.image.load("assets/img/background-day.png"), 1)
GROUND_IMG  :pygame.surface     = pygame.transform.scale_by(pygame.image.load("assets/img/base.png")          , 1)
PLAYER_IMG  :pygame.surface     = pygame.transform.scale_by(pygame.image.load("assets/img/yellowbird.png")    , 1)
PIPE_IMG    :pygame.surface     = pygame.transform.scale_by(pygame.image.load("assets/img/pipe.png")          , 1)
SFX_DEATH   :pygame.mixer.Sound = pygame.mixer.Sound("assets/sounds/die.wav")
SFX_RESPAWN :pygame.mixer.Sound = pygame.mixer.Sound("assets/sounds/respawn.wav")
MUSIC       :pygame.mixer.Sound = pygame.mixer.Sound("assets/sounds/HeatleyBros - HeatleyBros I - 09 8 Bit Onward.mp3")

# Init global variables
BG_X       :float       = 0.0 
GROUND_X   :float       = 0.0 
PIPE_LIST  :list[Pipe]  = []
SCORE      :int         = 0
SAVEPATH   :str         = "Save"
HIGHSCORE  :int         = 0


# Functions
def AddBGOffset(BG_OFFSET :float) -> None:
    """Adds an offset to the background image in the X axis"""
    global BG_X
    if math.fabs(BG_X) >= DISPLAY_X:                    # If offset is greater than the screen width, reset to 0
        BG_X = 0
    BG_X = BG_X + BG_OFFSET
    return

def AddGroundOffset(BG_OFFSET :float) -> None:
    """Adds an offset to the ground image in the X axis"""
    global GROUND_X
    if math.fabs(GROUND_X) >= DISPLAY_X:                    # If offset is greater than the screen width, reset to 0
        GROUND_X = 0
    GROUND_X = GROUND_X + BG_OFFSET
    return

def SpawnPipe() ->None:
    """Spawns a pipe at the edge of the screen"""
    global PIPE_LIST
    PIPE_LIST.append(
        Pipe(
            PIPE_IMG,
            -2,
            PLAYER_BIRB,
            100,200,
            window,
        )
    )
    return

def SaveGame() -> None:
    """Attempts to save variables to a binary save file, creates required folders and file if not present."""
    try:
        with open(f"{SAVEPATH}/save.birb", "rb") as savefile:
            savefile.close()
    except FileNotFoundError:
        try:
            os.mkdir(SAVEPATH)
        except FileExistsError:
            pass

        with open(f"{SAVEPATH}/save.birb", "+wb") as savefile:
            savefile.close()
    
    with open(f"{SAVEPATH}/save.birb", "wb") as savefile:
        savedata = {}
        savedata["playerdata"] = {"HighScore" : SCORE}
        pickle.dump(savedata, savefile)
    return

def LoadGame() -> None:
    """Load variables from the save file, doesn't do anything if it doesnt exist."""
    try:
        with open(f"{SAVEPATH}/save.birb", "rb") as savefile:
            try:
                global HIGHSCORE
                savedata = pickle.load(savefile)
                HIGHSCORE = savedata["playerdata"]["HighScore"]
            except Exception:
                pass
                
    except FileNotFoundError:
        pass

def Die():
    PLAYER_BIRB.alive = False
    SFX_DEATH.play()
    MUSIC.stop()
    if SCORE > HIGHSCORE: 
        SaveGame()
    return

def Respawn():
    """Reset values and repawn the player."""
    global LASTDEATH
    SFX_RESPAWN.play()
    MUSIC.play(-1)
    LASTDEATH = time.time()
    global SCORE
    PIPE_LIST.clear()
    SCORE              = 0
    PLAYER_BIRB.x      = DISPLAY_X * 0.2
    PLAYER_BIRB.y      = DISPLAY_Y / 2
    PLAYER_BIRB.vel_x  = 0
    PLAYER_BIRB.vel_y  = 0
    PLAYER_BIRB.alive  = True
    return


# Init player variables
LoadGame()
PLAYER_BIRB = Birb(
    SPRITE = PLAYER_IMG,
    RADIUS = 10,
    LOC_X  = DISPLAY_X * 0.2,
    LOC_Y  = DISPLAY_Y/2,
    VEL_X  = 0,
    VEL_Y  = 0,
    ACC_X  = 0,
    ACC_Y  = 0.15,                                       # Gravity
    WINDOW = window
)
LASTDEATH     = 0
HIGHSCORETEXT = FONT.render(f"High Score: {HIGHSCORE}", False, (255,255,255))
DEATHTEXT     = FONT_L.render(" Game Over ", False, (255,255,255), (0,0,0))
RESPAWNTIP    = FONT.render("Press 'R' to respawn", False, (255,255,255), (0,0,0))
MUSIC.play(-1)

# Game loop
while Running:
    PYGAME_EVENTS = pygame.event.get()
    PLAYER_BIRB.__pygame_events__ = PYGAME_EVENTS
    for event in PYGAME_EVENTS:
        if event.type == pygame.KEYDOWN and event.key == (pygame.K_r) and not PLAYER_BIRB.alive:
            Respawn()
        if event.type == pygame.QUIT:
            Running = False
            break

    window.blit(BG_IMG, (BG_X,0))                     # First background tile
    window.blit(BG_IMG, (BG_X + DISPLAY_X,0))         # Second background tile ahead of the first one for endless scrolling
    
    PLAYER_BIRB.Update()

    # Pipe spawning
    if len(PIPE_LIST) < 1 and PLAYER_BIRB.alive:
        SpawnPipe()
    else:
        for PIPE in PIPE_LIST:
            PIPE.Update()
            
            # Pipe collision
            if (pygame.Rect.colliderect(PLAYER_BIRB.rect, (PIPE.lower_rect)) or pygame.Rect.colliderect(PLAYER_BIRB.rect, (PIPE.upper_rect))) and PLAYER_BIRB.alive:
                Die()
            
            # Score adding
            if pygame.Rect.colliderect(PLAYER_BIRB.rect, PIPE.score_rect) and not PIPE.passed:
                SCORE += 1
                PIPE.passed = True
            
            if PIPE.x_location + PIPE.pipe_width <= 0:
                PIPE_LIST.remove(PIPE)

    if PLAYER_BIRB.alive: 
        AddBGOffset(-1)             # Add offset to the background to create an illusion of moving forwards
        AddGroundOffset(-2)         # Different offset for the ground for parallax
        
        # Handle collision on the edges of the screen
        if PLAYER_BIRB.y < PLAYER_BIRB.radius and PLAYER_BIRB.alive:                                # Top edge
            PLAYER_BIRB.y = PLAYER_BIRB.radius
            PLAYER_BIRB.vel_y = 0
            Die()

        if PLAYER_BIRB.y > PLAYER_BIRB.display_y - PLAYER_BIRB.radius - 50 and PLAYER_BIRB.alive:   # Bottom edge
            PLAYER_BIRB.y = PLAYER_BIRB.display_y - PLAYER_BIRB.radius - 50                 # Set bird to ground level
            PLAYER_BIRB.vel_y = 0
            Die()
    else:
        window.blit(DEATHTEXT, (DISPLAY_X/2 - 90, DISPLAY_Y/2 - 50))
        window.blit(RESPAWNTIP, (DISPLAY_X/2 - 100, DISPLAY_Y/2 - 20))

    # HUD
    SCORETEXT = FONT.render(f"Score: {SCORE}", False, (255,255,255))
    window.blit(HIGHSCORETEXT, (DISPLAY_X - 150, 10))
    window.blit(SCORETEXT, (DISPLAY_X - 100, 35))

    window.blit(GROUND_IMG, (GROUND_X,  DISPLAY_Y - 50))                     # Same as background tiles but for ground tiles
    window.blit(GROUND_IMG, (GROUND_X + DISPLAY_X,DISPLAY_Y - 50))

    clock.tick(60)
    pygame.display.update()