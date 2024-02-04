import pygame
import math
import random

pygame.mixer.init()
SFX_JUMP    :pygame.mixer.Sound = pygame.mixer.Sound("assets/sounds/jump.wav")
def CalculateRotationFromVelocity(VEL_Y: tuple(), SENSITIVITY :float = 5) -> float:
    """ Inputs y velocity, outputs a rotation derived from it
        Sensitivity defines how much velocity we need to rotate the sprite by some rotation. 
        i.e, small sensitivity value means we need a small velocity to rotate by a large angle."""

    return (math.atan2(VEL_Y, SENSITIVITY) * 180 / math.pi * -1)


class Birb:
    def __init__(self, 
                SPRITE :pygame.surface, 
                RADIUS :float, 
                LOC_X :float, LOC_Y :float, 
                VEL_X :float, VEL_Y :float, 
                ACC_X :float, ACC_Y :float, 
                WINDOW :pygame.surface,
                ALIGN_ROTATION :bool = True,
                JUMP_COOLDOWN :float = 0.5,
                JUMP_STRENGTH :float = 3,
                ) -> None:
        
        self.display_x, self.display_y = WINDOW.get_size()
        self.__pygame_events__ = None

        self.sprite         = SPRITE
        self.radius         = RADIUS
        self.width          = SPRITE.get_width()
        self.height         = SPRITE.get_height()
        self.x              = LOC_X
        self.y              = LOC_Y
        self.vel_x          = VEL_X
        self.vel_y          = VEL_Y
        self.acc_x          = ACC_X
        self.acc_y          = ACC_Y
        self.window         = WINDOW
        self.align_rotation = ALIGN_ROTATION
        self.jump_strength  = JUMP_STRENGTH
        self.jump_cooldown  = JUMP_COOLDOWN
        self.jumping        = False
        self.alive          = True
        self.rect           = pygame.Rect(self.x, self.y, self.width, self.height)

    def HandleInput(self):
        for event in self.__pygame_events__:
            if event.type == pygame.KEYDOWN and event.key == (pygame.K_UP or pygame.K_SPACE) and not self.jumping and self.alive:
                self.jumping = True
                self.vel_y = -self.jump_strength
                SFX_JUMP.play()

            elif event.type == pygame.KEYUP and event.key == (pygame.K_UP or pygame.K_SPACE) and self.jumping:
                self.jumping = False

    def Update(self):
        self.HandleInput()
        self.window.blit(
            pygame.transform.rotate(self.sprite, 
                CalculateRotationFromVelocity(
                    (self.vel_y)
                )
            ),
            (self.x - self.radius, self.y - self.radius)
        )
        
        self.rect  = pygame.Rect(self.x - (self.width/4), self.y - (self.height/4), self.width, self.height)
        if self.alive:                  # Only update location and velocity if alive
            self.x     += self.vel_x
            self.y     += self.vel_y
            self.vel_x += self.acc_x
            self.vel_y += self.acc_y


class Pipe:
    def __init__(self, SPRITE :pygame.surface, 
                SCROLL_SPEED :float,
                PLAYER :Birb,
                GAP_MIN :float, GAP_MAX :float, 
                WINDOW :pygame.surface) -> None:
        
        self.display_x, self.display_y = WINDOW.get_size()

        self.sprite      = SPRITE
        self.speed       = SCROLL_SPEED
        self.gap_min     = GAP_MIN
        self.gap_max     = GAP_MAX
        self.window      = WINDOW
        self.player_birb = PLAYER
        self.pipe_width  = SPRITE.get_width()
        self.pipe_height = SPRITE.get_height()
        self.magic_num   = random.randint(30, 100)/100      # The bottom pipe is always above 30% of it's height
        self.gap         = random.randrange(self.gap_min, self.gap_max)
        self.y1_location = self.display_y - self.pipe_height * self.magic_num
        self.y2_location = self.y1_location - (self.pipe_height + self.gap)
        self.x_location  = self.display_x
        self.lower_rect  = pygame.Rect(self.x_location, self.y1_location, self.pipe_width, self.pipe_height)
        self.upper_rect  = pygame.Rect(self.x_location, self.y2_location, self.pipe_width, self.pipe_height)
        self.score_rect  = pygame.Rect(self.x_location, self.y1_location, self.pipe_width, self.pipe_height)
        self.passed      = False
        
    def Update(self):
        if self.player_birb.alive:
            self.x_location += self.speed
        lower_pipe = self.sprite
        upper_pipe = pygame.transform.flip(lower_pipe, flip_x=False, flip_y=True)

        # Lower pipe
        self.lower_rect  = self.sprite.get_rect(topleft = (self.x_location, self.y1_location))
        self.window.blit(
            lower_pipe,
            (self.x_location, self.y1_location)
        )

        # Upper pipe
        self.upper_rect  = self.sprite.get_rect(topleft = (self.x_location, self.y2_location))
        self.window.blit(
            upper_pipe,
            (self.x_location, self.y2_location)
        )

        # Score rect
        self.score_rect = pygame.Rect(self.x_location + self.pipe_width/2 - 5, 
                                      self.y2_location + self.pipe_height, 
                                      10, self.gap)
