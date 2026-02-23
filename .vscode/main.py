
import sys  
import pygame
import math  
import random  

'''
Fix the player and monster collisions, the player is taking  infinite damage as soon as in contact with enemy, 
create a buffer in time to prevent multiple hits in one second.
Then fix the end screen and the monster spawn location.
'''
# Base game entity class providing shared attributes and basic movement
class GameEntity:
    # Base class for all game entities (Player, Monster, etc.)
    def __init__(self, name, health, max_health, x, y, width=50, height=50):
        self.name = name  # store the entity's name
        self.health = health  # current health value
        self.max_health = max_health  # maximum health value
        self.rect = pygame.Rect(x, y, width, height)  # rectangular position/size for rendering and collisions
        self.speed = 5  # default movement speed (pixels per frame)
        self.bullets = []  # list to hold bullets fired by this entity
    
    def move(self, dx, dy):
        # Move the entity by dx and dy (adjust rectangle in place)
        self.rect.move_ip(dx, dy)

# Player entity inherits from GameEntity and can fire bullets
class Player(GameEntity):
    def __init__(self, name, health, max_health, x, y, width=50, height=50):
        super().__init__(name, health, max_health, x, y, width, height)  # initialize base attributes
    def fire(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()  # get mouse cursor coordinates
        px, py = self.rect.center  # get player's center coordinates for bullet spawn
        dx = mouse_x - px  # horizontal difference from player to mouse
        dy = mouse_y - py  # vertical difference from player to mouse
        distance = math.hypot(dx, dy)  # straight-line distance between player and mouse
        if distance == 0:  # if distance zero, avoid dividing by zero
            return  # nothing to do if the mouse is exactly at the player center
        dx /= distance  # normalize horizontal component to unit length
        dy /= distance  # normalize vertical component to unit length
        bullet_speed = 7  # speed at which bullets travel (pixels per frame)
        bullet = {
            'x': px,  # bullet initial x position
            'y': py,  # bullet initial y position
            'dx': dx * bullet_speed,  # bullet velocity x component
            'dy': dy * bullet_speed,  # bullet velocity y component
        }
        self.bullets.append(bullet)  # add the new bullet to the player's bullet list
        # Longer explanation of the firing behavior (kept as comments rather than a string literal):
        # 1. Get mouse and player center positions.
        # 2. Compute direction vector (dx, dy) from player to mouse.
        # 3. Normalize direction to unit length so only direction remains.
        # 4. Multiply normalized direction by bullet speed to obtain velocity.
        # 5. Spawn bullet at player's center with the computed velocity.

# Monster entity with velocity-based smooth movement and simple AI
class Monster(GameEntity):
    def __init__(self, name, health, max_health, x, y, width=50, height=50):
        super().__init__(name, health, max_health, x, y, width, height)  # initialize base attributes
        # Velocity components for smooth diagonal movement
        self.vx = 0  # current x velocity (pixels per frame)
        self.vy = 0  # current y velocity (pixels per frame)
        self.speed = 3  # AI chase speed (pixels per frame)
    
    def move_ai(self):
        """Move monster according to its velocity components."""
        self.rect.x += self.vx  # apply horizontal velocity to x position
        self.rect.y += self.vy  # apply vertical velocity to y position
    
    def move_towards_player(self, player_x, player_y):
        """Compute velocity toward player and move the monster smoothly."""
        delta_x = player_x - self.rect.x  # horizontal distance to player
        delta_y = player_y - self.rect.y  # vertical distance to player
        distance = math.hypot(delta_x, delta_y)  # straight-line distance to player
        if distance > 0:  # avoid division by zero
            self.vx = (delta_x / distance) * self.speed  # normalized x velocity scaled by speed
            self.vy = (delta_y / distance) * self.speed  # normalized y velocity scaled by speed
        else:
            self.vx = 0  # stop horizontal movement when at player
            self.vy = 0  # stop vertical movement when at player
        self.move_ai()  # apply the computed velocity to position

def run():
    pygame.init()  # initialize all imported pygame modules
    size = (800, 600)  # window size (width, height)
    screen = pygame.display.set_mode(size)  # create a display surface of the given size
    pygame.display.set_caption('Player vs Monster - Pygame 2D Game')  # set window title
    clock = pygame.time.Clock()  # create a clock to manage frame rate
    font = pygame.font.SysFont(None, 28)  # default system font at size 28
    # Instantiate main game objects: player and single monster
    player_obj = Player("Hero", 100, 100, x=100, y=250)  # player starts near left side
    monsters = []  # list to hold multiple monsters (currently only one)
    monster_obj = Monster("monster", 100, 100, x=600, y=250)  # monster starts near right side
    monsters.append(monster_obj)  # add the monster to the list
    player_speed = 5  # movement speed for player input
    game_active = True  # whether gameplay (collisions, AI) is active
    running = True  # main loop control flag
    while running:  # game loop
        for event in pygame.event.get():  # handle all pending events
            if event.type == pygame.QUIT:  # window close requested
                running = False  # exit main loop
            elif event.type == pygame.KEYDOWN:  # key pressed
                if event.key == pygame.K_f:  # 'f' key triggers firing
                    player_obj.fire()  # player shoots a bullet
            elif event.type == pygame.MOUSEBUTTONDOWN:  # mouse button pressed
                if event.button == 1:  # left-click
                    player_obj.fire()  # player shoots a bullet
        keys = pygame.key.get_pressed()  # get current key states
        if keys[pygame.K_ESCAPE]:  # escape key to quit
            running = False  # exit main loop
        # Accumulate movement input from arrow keys and WASD
        dx = 0  # horizontal movement accumulator
        dy = 0  # vertical movement accumulator
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # left or 'A'
            dx -= player_speed  # move left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # right or 'D'
            dx += player_speed  # move right
        if keys[pygame.K_UP] or keys[pygame.K_w]:  # up or 'W'
            dy -= player_speed  # move up
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  # down or 'S'
            dy += player_speed  # move down
        # Normalize diagonal movement to avoid faster diagonal speed (scale by sqrt(2))
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)  # scale horizontal component
            dy /= math.sqrt(2)  # scale vertical component
        player_obj.move(int(dx), int(dy))  # move player by the computed integer offset
        # Keep player inside screen bounds (clamp coordinates)
        player_obj.rect.x = max(0, min(player_obj.rect.x, size[0] - player_obj.rect.width))
        player_obj.rect.y = max(0, min(player_obj.rect.y, size[1] - player_obj.rect.height))
        if game_active:  # only update AI while game is active
            for monster_obj in monsters:
                monster_obj.move_towards_player(player_obj.rect.centerx, player_obj.rect.centery)  # chase player
        # Prevent monster from going off-screen by clamping its position
        for monster_obj in monsters:
            monster_obj.rect.x = max(0, min(monster_obj.rect.x, size[0] - monster_obj.rect.width))
            monster_obj.rect.y = max(0, min(monster_obj.rect.y, size[1] - monster_obj.rect.height))
        # Update bullets: move each bullet and remove if it leaves the screen
        for bullet in player_obj.bullets[:]:  # iterate over a shallow copy to allow removal
            bullet['x'] += bullet['dx']  # move bullet horizontally
            bullet['y'] += bullet['dy']  # move bullet vertically
            if bullet['x'] < 0 or bullet['x'] > size[0] or bullet['y'] < 0 or bullet['y'] > size[1]:
                player_obj.bullets.remove(bullet)  # remove off-screen bullets
        # Drawing phase: clear screen and draw all objects
        screen.fill((30, 30, 40))  # fill background with dark color
        if player_obj.health <= 0:  # check for player death
            game_active = False  # stop game interactions
            lose = font.render('Game Over!', True, (255, 50, 50))  # render game over text
            screen.blit(lose, (size[0] // 2 - 40, size[1] // 2 - 20))  # draw game over text
            pygame.display.flip()  # update the full display
            pygame.time.wait(2000)  # pause for 2 seconds before exiting
            running = False  # exit main loop
            continue  # skip rest of loop and break out after delay
        else:
            pygame.draw.rect(screen, (70, 160, 70), player_obj.rect)  # draw player as green rectangle
        for monster_obj in monsters:
            if monster_obj.health > 0:  # only draw monster when alive
                pygame.draw.rect(screen, (160, 70, 70),  monster_obj.rect)  # draw monster as red rectangle
        # Draw bullets as yellow circles and keep their pygame shapes for collision checks
        bullet_projectiles = []  # list to hold (bullet_dict, pygame_shape) tuples
        for bullet in player_obj.bullets:
            bullet_projectile = pygame.draw.circle(screen, (255, 255, 0), (int(bullet['x']), int(bullet['y'])), 10)
            bullet_projectiles.append((bullet, bullet_projectile))  # store for collision checks
        info = font.render('Move with arrow keys or WASD. Esc to quit. F or click to fire.', True, (220, 220, 220))
        screen.blit(info, (10, 10))  # draw instruction text at top-left
        # Check bullet collisions against the monster
        for bullet, bullet_projectile in bullet_projectiles:
            if bullet_projectile.colliderect(monster_obj.rect):  # collision detected
                if bullet in player_obj.bullets:
                    player_obj.bullets.remove(bullet)  # remove bullet that hit
                hit = font.render('Collision!', True, (255, 255, 50))  # render collision text
                screen.blit(hit, (size[0] // 2 - 40, 60))  # draw collision indicator
                for monster_obj in monsters:
                    if bullet_projectile.colliderect(monster_obj.rect):  # collision detected
                        monster_obj.health -= 20  # reduce monster health on hit
                break  # stop checking other bullets after a hit to prevent multiple hits from one bullet
        # Collision between player and monster reduces player health
        hit = False
        for monster_obj in monsters:
            if player_obj.rect.colliderect(monster_obj.rect) and monster_obj.health > 0 and hit == False:
                hit = font.render('Player hit!', True, (255, 50, 50))  # render player hit text
                screen.blit(hit, (size[0] // 2 - 40, 40))  # draw hit indicator
                player_obj.health -= 10  # reduce player health on contact
                hit = True 
        player_health = font.render(f'Player Health: {player_obj.health}', True, (255, 255, 0))  # render player health
        screen.blit(player_health, (10, 560))  # draw player health at bottom-left
        for monster_obj in monsters:
            if monster_obj.health > 0:
                monster_health = font.render(f'Monster Health: {monster_obj.health}', True, (255, 50, 50))  # render monster health
                screen.blit(monster_health, (size[0] - 250, 560))  # draw monster health at bottom-right
        
        for monster_obj in monsters:
            if monster_obj.health <= 0:  # check if monster died
                game_active = False  # stop gameplay interactions
                win = font.render('You Win! Press R to Restart to Next Level', True, (50, 255, 50))  # render victory text
                screen.blit(win, (size[0] // 2 - 40, size[1] // 2 - 20))  # draw victory text centered
                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:  # restart game on 'R' key press
                    player_obj.health = player_obj.max_health  # reset player health
                    for monster_obj in monsters:
                        monster_obj.health = monster_obj.max_health  # reset monster health
                        monster_obj.rect.topleft = (600, 250)  # reset monster position
                    player_obj.rect.topleft = (100, 250)  # reset player position
                player_obj.bullets.clear()  # clear any existing bullets
                game_active = True  # reactivate gameplay

        pygame.display.flip()  # swap display buffers to show drawn frame
        clock.tick(60)  # cap the frame rate at 60 FPS
    pygame.quit()  # clean up all pygame modules and exit

if __name__ == '__main__':
    try:
        run()  # start the game loop when executed as script
    except Exception as e:  # catch any exception to ensure pygame quits cleanly
        print('Error running pygame window:', e)  # print error message
        pygame.quit()  # attempt to shut down pygame gracefully
        sys.exit(1)  # exit with error status
