#imports
import pygame #library for game dev
import math #library for math stuff like cos sin and pi
import random #generates random numbers/choices

#initialize pygame
pygame.init()
#set the clock
clock = pygame.time.Clock()
#define the screen size
screen_size = (800, 800)

screen = pygame.display.set_mode((screen_size)) #set the screen
font = pygame.font.SysFont(None, 36) #set default font


#set up the image for the razor
razor_img = pygame.image.load("/Users/rahulagarwal/python/cs50 final/assets/razor.png").convert_alpha()
razor_img = pygame.transform.scale(razor_img, (75,  75)) #this scales the image

#set image for soccer ball
soccer_ball_img = pygame.image.load("/Users/rahulagarwal/python/cs50 final/assets/soccer ball.png").convert_alpha()
soccer_ball_img = pygame.transform.scale(soccer_ball_img, (90, 90))

player_img = pygame.image.load("/Users/rahulagarwal/python/cs50 final/assets/player.png").convert_alpha()

player_sprite_width = 13
player_sprite_height = 12
frames_count = 4
frames = []

for i in range(frames_count):
    frame = player_img.subsurface(pygame.Rect(0, i * player_sprite_height, player_sprite_width, player_sprite_height))
    frame = pygame.transform.scale(frame, (50, 50))
    frames.append(frame)

#variables for movement
acceleration = 0.75
x_speed = 0
y_speed = 0
friction = 0.25

#variables for razors
num_balls = 0
ball_radius = 30
angle_offset = 0.0
razor_damage = 1
razor_speed = 0.07

#variables for the enemies
enemies = []
last_spawn_time = pygame.time.get_ticks() #this is for spawning enemies in increments

#fire delay for the bullet
fire_delay = 1000

#variables for the soccer ball
soccer_ball_num = 0
soccer_balls = []
soccer_ball_damage = 10

#constants
MAX_SPEED = 7.5 #cap player speed
PLAYER_MAX_HEALTH = 100 #cap player health

#default stats for enemies
ENEMY_DEFAULT_HEALTH = 20
ENEMY_DEFAULT_SPEED = 2

#the player class
class player:
    def __init__(self):
        #initialize player position, size and health
        self.x = 300
        self.y = 400
        self.width = frames[0].get_width() #get the width of the player image
        self.height = frames[0].get_height() #get the height of the player image
        self.health = PLAYER_MAX_HEALTH

        self.animation_speed = 200
        self.animation_timer = 0
        self.frame = 0

    def move(self): #to move simply change the x and y by their repspective speed
        self.x += x_speed
        self.y += y_speed

    def check_bounds(self): #check if player went of screen
        if self.x < 0: #check left side
            self.x = 0
        elif self.x + self.width > screen_size[0]: #check right side
            self.x = screen_size[0] - self.width
        if self.y < 0: #check top
            self.y = 0
        elif self.y + self.height > screen_size[1]: #check bottom
            self.y = screen_size[1] - self.height

    def draw_health_bar(self): #helath bar above player
        health_percentage = self.health / PLAYER_MAX_HEALTH #percentage of max health player currenct has
        bar_width = 50 #width of the health bar 
        bar_height = 10 #height of the bar
        corner_radius = 5 #this is for rounded corners
        #draw the bar background, so when the player loses health it looks like the bar is depleting and turning red 
        pygame.draw.rect(screen, (255, 0, 0), (self.x-self.width/2+bar_width/2+10, self.y - 20, bar_width, bar_height), border_radius=corner_radius)
        #draw the bar itself, so when the player has health it is green
        pygame.draw.rect(screen, (0, 255, 0), (self.x-self.width/2 + bar_width/2+10, self.y - 20, bar_width * health_percentage, bar_height), border_radius=corner_radius)
        #rects are draw with the arguments (x, y, width, height) so we need to adjust the x position by half the width of the player to center it
        #rects are also drawn in the order they are called so in this case the red bar is drawn first and then the green bar is drawn on top of it
   
    #check if player collides with an enemy
    def check_collision(self, enemy): #check collision with enemy
        dist = math.sqrt((self.x + self.width/2 - enemy.x)**2 + (self.y + self.height/2 - enemy.y)**2)
        return dist < (self.width/2 + enemy.radius)  
    #this formula is sqrt((x1 - x2)^2 + (y1 - y2)^2) to calculate the distance between the player and the enemy
    
    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % frames_count

    #draw the player
    def draw(self, screen):
        frame = frames[self.frame]
        sprite_rect = frame.get_rect(center=(int(self.x + self.width // 2), int(self.y + self.height // 2)))
        screen.blit(frame, sprite_rect) #draw the player image at the position of the player

# Enemy class
class Enemy:
    def __init__(self, x, y, speed = ENEMY_DEFAULT_SPEED, radius = 20, health = ENEMY_DEFAULT_HEALTH, color=(255, 0, 0), damage = 5):
        #intialize enemy position, speed, radius, health, color and damage
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.health = health
        self.max_health = health
        self.color=color
        self.damage = damage

    def move(self, player_x, player_y): #moves towards player
        #this is again the formula for distance between two points
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        #if distance is not zero then normalize the vector to get the direction
        if distance != 0:
            dx /= distance
            dy /= distance

        #multiply the direction by speed to get the movement vector
        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw_health(self): #draw health bar
        #this is the same as the player health bar but with different values
        health_percentage = self.health / self.max_health
        bar_width = self.max_health / 1.5 + 10
        bar_height = 10
        corner_radius = 5
        pygame.draw.rect(screen, (255, 0, 0), (self.x - bar_width/2, self.y - bar_height/2 - self.radius - 10, bar_width, bar_height), border_radius=corner_radius)
        pygame.draw.rect(screen, (0, 255, 0), (self.x - bar_width/2, self.y - bar_height/2 - self.radius - 10, bar_width * health_percentage, bar_height), border_radius=corner_radius)
    
    #draw the enemy
    def draw(self, screen): 
        pygame.draw.circle(screen,self.color, (int(self.x), int(self.y)), self.radius)

#bulelt class
class Bullet:
    def __init__(self, x, y, target_x, target_y, speed = 12, size = 5 ):
        #initialize bullet position, target position, speed and size
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.size = size

        self.active = True

        #we only calculate the direction once when the bullet is created so it doesn't stop at the cursor
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
        if distance != 0:
            self.dx = dx / distance
            self.dy = dy / distance

    def move(self):
        #simply move the bullet
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        if self.x < 0 or self.x > screen_size[0] or self.y < 0 or self.y > screen_size[1]:
            self.active = False
    #draw bullet
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.size)

# Soccer ball class
class soccerBall():
    #intialize the soccer ball with position, speed, radius and angle
    def __init__(self, x, y, speed=5, radius=20):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.damage = soccer_ball_damage
        self.angle = random.uniform(0, 2 * math.pi) #random angle to start out
        self.dx = 0
        self.dy = 0
    
    #move the ball
    def move(self):
        #calculate the dx and dy based on the angle and speed
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)
        self.x += self.dx 
        self.y += self.dy

        #bounce off the walls
        if(self.x > screen_size[0] - self.radius):
            self.dx = -self.dx
            self.angle = math.pi - self.angle
        elif(self.x < self.radius):
            self.dx = -self.dx 
            self.angle = math.pi - self.angle
        if(self.y > screen_size[1] - self.radius):
            self.dy = -self.dy
            self.angle = -self.angle
        elif(self.y < self.radius):
            self.dy = -self.dy
            self.angle = -self.angle
    
    #same collision logic as with everythin else
    def check_collision(self, enemy):
        collision = False
        dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
        if dist <= self.radius + enemy.radius:
            collision = True
            self.dy = -self.dy
            self.dx = -self.dx
            enemy.health -= self.damage
        return collision
    #draw the soccer ball
    def draw(self, screen):
        sprite_rect = soccer_ball_img.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(soccer_ball_img, sprite_rect)


#mange upgrades
class UpgradeManager:
    def __init__(self):
        #intiliaze the upgrade levels and description
        self.razors_upgrade_num = 0
        self.bullet_upgrade_num = 0
        self.soccer_upgrade_num = 0
        self.speed_upgrade_num = 0
        self.description = ""

    #apply the upgrades
    def apply_razor_upgrade(self):
        self.description, self.razors_upgrade_num = apply_razor_upgrade()

    def apply_bullet_upgrade(self):
        self.description, self.bullet_upgrade_num = apply_bullet_upgrade()

    def apply_soccer_upgrade(self):
       self.description, self.soccer_upgrade_num = apply_soccer_upgrade()
    
    def apply_speed_upgrade(self):
        self.description, self.speed_upgrade_num = apply_speed_upgrade()

#the manager
manager = UpgradeManager()

#class fot the upgrades
class Upgrade():
    #includes name, functions for the preview, and apply functions
    def __init__(self, name, preview_func, apply_func):
        self.name = name
        self.preview_func = preview_func
        self.apply_func = apply_func

#list of upgrades
upgrades_list = [
    Upgrade("Razors", lambda: preview_razor_upgrade(), manager.apply_razor_upgrade),
    Upgrade("Bullet", lambda: preview_bullet_upgrade(), manager.apply_bullet_upgrade),
    Upgrade("Soccer ball", lambda: preview_soccer_upgrade(), manager.apply_soccer_upgrade),
    Upgrade("Speed", lambda: preview_speed_upgrade(), manager.apply_speed_upgrade), 
] 

#razor upgrade function  
def apply_razor_upgrade():
    global num_balls, razor_damage, razor_speed
    level = manager.razors_upgrade_num

    if level == 0:
        description = f'Number of razors {num_balls} → {num_balls + 2}'
        num_balls += 2
    elif level == 1:
        description = f'Number of razors {num_balls} → {num_balls + 2}\nDamage {razor_damage} → {razor_damage + 0.5}'
        num_balls += 2
        razor_damage += 0.5
    elif level == 2:
        description = f'Number of razor {num_balls} → {num_balls + 1}\nSpeed {razor_speed} → {round(razor_speed + 0.03, 2)}'
        razor_speed = round(razor_speed + 0.03, 2)
        num_balls += 1
    level += 1
    return description, level

#previe the upgrade
def preview_razor_upgrade():
    level = manager.razors_upgrade_num
    if level == 0:
        description = f'Number of razors {num_balls} → {num_balls + 2}'
    elif level == 1:
        description = f'Number of razors {num_balls} → {num_balls + 2}\nDamage {razor_damage} → {razor_damage + 0.5}'
    elif level == 2:
        description = f'Number of razor {num_balls} → {num_balls + 1}\nSpeed {razor_speed} → {round(razor_speed + 0.03, 2)}'
    return description

#upgrades for bullets
def apply_bullet_upgrade():
    global fire_delay
    level = manager.bullet_upgrade_num
    if level == 0:
        description = f'Fire delay {int(fire_delay)/1000} → {int(fire_delay * 0.9)/1000}'
        fire_delay *= 0.9
    level += 1
    return description, level

def preview_bullet_upgrade():
    level = manager.bullet_upgrade_num
    description = ""
    if level == 0:
        description = f'Fire delay {int(fire_delay)/1000} → {int(fire_delay * 0.9)/1000}'
    return description

#soccer upgrades
def apply_soccer_upgrade():
    global soccer_ball_num, soccer_ball_damage
    level = manager.soccer_upgrade_num
    if level == 0:
        description = f'Soccer ball count {soccer_ball_num} → {soccer_ball_num + 1}'
        soccer_ball_num += 1
    elif level == 1:
        description = f'Soccer ball bdamage {soccer_ball_damage} → {soccer_ball_damage + 5}'
        soccer_ball_damage += 5
    elif level == 2:
        description = f'Soccer ball count {soccer_ball_num} → {soccer_ball_num + 1}'
        soccer_ball_num += 1
    level += 1
    return description, level

def preview_soccer_upgrade():
    description = ""
    level = manager.soccer_upgrade_num
    if level == 0:
        description = f'Soccer ball count {soccer_ball_num} → {soccer_ball_num + 1}'
    elif level == 1:
        description = f'Soccer ball bdamage {soccer_ball_damage} → {soccer_ball_damage + 5}' 
    elif level == 2:
        description = f'Soccer ball count {soccer_ball_num} → {soccer_ball_num + 1}'
    return description

def apply_speed_upgrade():
    global MAX_SPEED, acceleration
    description = ""
    level = manager.speed_upgrade_num
    if level == 0:
        description = f'Player speed {MAX_SPEED} → {MAX_SPEED * 1.2}'
        MAX_SPEED *= 1.2
    elif level == 1:
        description = f'Player speed {MAX_SPEED} → {MAX_SPEED * 1.25}\nAcceleration {acceleration} → {acceleration * 1.1}'
        MAX_SPEED *= 1.25
        acceleration *= 1.1
    elif level == 2:
        description = f'Player speed {acceleration} → {acceleration * 1.2}'
    level += 1
    return description, level

def preview_speed_upgrade():
    description = ""
    level = manager.speed_upgrade_num
    if level == 0:
        description = f'Player speed {MAX_SPEED} → {MAX_SPEED * 1.2}'
    elif level == 1:
        description = f'Player speed {MAX_SPEED} → {MAX_SPEED * 1.25}\nAcceleration {acceleration} → {acceleration * 1.1}'
    elif level == 2:
        description = f'Player speed {acceleration} → {acceleration * 1.2}'
    level += 1
    return description

#only return upgrades where upgrade num < 5
def filter_upgrades(upgrades, limit = 5):
    return [upgrade for upgrade in upgrades if 
            manager.razors_upgrade_num < limit or
            manager.bullet_upgrade_num < limit or
            manager.soccer_upgrade_num < limit or
            manager.speed_upgrade_num < limit]

#menu for upgrade
def upgrade_menu():
    card_width = 230
    card_height = 330
    padding = 50
    card_color = (50, 50, 50)
    hover_color = (100, 100, 100)
    text_color = (255, 255, 255)

    title_font = pygame.font.SysFont('arial', 24, bold=True)
    name_font = pygame.font.SysFont('arial', 18, bold=True)
    desc_font = pygame.font.SysFont('arial', 16)

    filtered = filter_upgrades(upgrades_list)
    selected_upgrades = random.sample(filtered, 3)

    total_width = len(selected_upgrades) * (card_width + padding) - padding
    start_x = (screen_size[0] - total_width) // 2
    start_y = (screen_size[1] - card_height) // 2

    while True:
        screen.fill((10, 10, 10))

        #draw the title
        title_text = title_font.render("Choose an Upgrade", True, text_color)
        screen.blit(title_text, (
            screen_size[0] // 2 - title_text.get_width() // 2,
            start_y - 70
        ))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        # Draw each upgrade card
        for i, upgrade in enumerate(selected_upgrades):
            x = start_x + i * (card_width + padding)
            y = start_y
            card_rect = pygame.Rect(x, start_y, card_width, card_height)

            is_hovered = card_rect.collidepoint(mouse_x, mouse_y)
            color = hover_color if is_hovered else card_color

            pygame.draw.rect(screen, color, card_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), card_rect, 3, border_radius=10)

            # Draw upgrade name
            name_text = name_font.render(upgrade.name, True, text_color)
            name_x = x + (card_width - name_text.get_width()) // 2
            screen.blit(name_text, (name_x, y + 20))

            #description
            description = upgrade.preview_func()


            desc_lines = description.split('\n')
            for j, line in enumerate(desc_lines):
                desc_text = desc_font.render(line.strip(), True, text_color)
                desc_x = x + (card_width - desc_text.get_width()) // 2
                desc_y = start_y + 50 + j * 30
                screen.blit(desc_text, (desc_x,desc_y ))

            if is_hovered and clicked:
                upgrade.apply_func()
                return

        pygame.display.flip()
        clock.tick(60)

#enemy color when for when spawning becomes dynamic ans not set types
def get_enemy_color(speed, health, max_speed = 5, max_health = 70):
    speed_norm = min(1, speed / max_speed)
    health_norm = min(1, health / max_health)

    b = int(255 * speed_norm)
    g = int(255 * health_norm)
    r = 255 - max(g,b)

    return (r, g, b)

#calculate enemy damage based on health
def calculate_damage(health, base_damage=3, max_health=70, scaling_factor=5):
    health_ratio = min(health / max_health, 1.0)
    return int(base_damage + health_ratio * scaling_factor)

#spawn enemy function 
def spawn_enemy(START_TIME):
    border = random.choice(['top', 'bottom', 'left', 'right'])
    offset = 20

    #spawn around the edge of the screen
    if border == 'top':
        x = random.randint(0, screen_size[0])
        y = -offset
    elif border == 'bottom':
        x = random.randint(0, screen_size[0])
        y = screen_size[1] + offset
    elif border == 'left':
        x = -offset
        y = random.randint(0, screen_size[1])
    elif border == 'right':
        x = screen_size[0] + offset
        y = random.randint(0, screen_size[1])

    time_since_start = pygame.time.get_ticks() - START_TIME

    #fast and weaker enemy
    if(time_since_start >= 15000 and random.randint(0,3) == 1):
        return Enemy(x, y, speed=ENEMY_DEFAULT_SPEED+2+time_since_start/30000, radius=15, health=ENEMY_DEFAULT_HEALTH-10, color=(0,0,255), damage=3)
    #stronger and slower enemy
    if(time_since_start >= 30000 and random.randint(0,5) == 1):
        return Enemy(x, y, speed=ENEMY_DEFAULT_SPEED-0.5, radius=25, health=ENEMY_DEFAULT_HEALTH+10+time_since_start/45000, color=(0,255,0), damage=7)
    #dynamic enemy
    if(time_since_start >= 30000 and random.randint(0,2) == 1):
        speed = ENEMY_DEFAULT_SPEED + random.randint(0, 5) + time_since_start/15000
        health = ENEMY_DEFAULT_HEALTH + random.randint(0, 20) + time_since_start/15000
        damage = calculate_damage(health)
        color = get_enemy_color(speed, health)
        return Enemy(x, y, speed=speed, radius=25, health=health, color=color, damage=damage)
    return Enemy(x,y) #basic enemy

#spawns the enemies at x intervals
def spawn_enemies(last_spawn_time, START_TIME, spawn_interval=2000):
    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time >= spawn_interval:
        enemies.append(spawn_enemy(START_TIME))
        return enemies, current_time
    return enemies, last_spawn_time

#calculates the spawn interval based on time since start
def calc_interval(time_since_start, spawn_interval):
    if(time_since_start % 60000 == 0 and spawn_interval > 500):
        spawn_interval -= 500
    return spawn_interval

#player movement
def movement(x_speed, y_speed):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        if(x_speed < MAX_SPEED):
            x_speed += acceleration
    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
        if(x_speed > -MAX_SPEED):
            x_speed -= acceleration

    if keys[pygame.K_UP] or keys[pygame.K_w]:    
        if(y_speed > -MAX_SPEED):
            y_speed -= acceleration
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        if(y_speed < MAX_SPEED):
            y_speed += acceleration
    else:
        if x_speed > 0:
            x_speed -= friction
        elif x_speed < 0:
            x_speed += friction
        if y_speed > 0:
            y_speed -= friction
        elif y_speed < 0:
            y_speed += friction
    return x_speed, y_speed

#draws the spinning balls around the player
def draw_balls(screen, x, y, num_balls, radius = 75, angle_offset=0):
    balls = []
    for i in range(num_balls):
        angle = (i * 2 * math.pi) / num_balls + angle_offset
        ball_x = x + radius * math.cos(angle)
        ball_y = y + radius * math.sin(angle)
        sprite_rect = razor_img.get_rect(center=(int(ball_x), int(ball_y)))
        screen.blit(razor_img, sprite_rect)
        balls.append((ball_x, ball_y))
    return balls

def get_soccer_balls(num_balls):
    soccer_balls = []
    for i in range(num_balls):
        ball = soccerBall(random.randint(10, screen_size[0]-10), random.randint(10, screen_size[1]-10))
        soccer_balls.append(ball)
    return soccer_balls

def draw_soccer_balls(soccer_balls):
    for ball in soccer_balls:
        ball.move()
        ball.draw(screen)

def check_enemy_soccer_ball_collision(soccer_balls, enemies, kills):
    for ball in soccer_balls:
        for enemy in enemies:
            if(ball.check_collision(enemy)):
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    kills += 1
                    return True, kills
    return False, kills

#checks if the spinning balls collided with the player
def check_enemy_collision(balls, enemies):
    for ball_x,ball_y in balls:
        for enemy in enemies:
            dist = math.sqrt((ball_x - enemy.x)**2 + (ball_y - enemy.y)**2)
            if dist <= enemy.radius + ball_radius:
                enemy.health -= razor_damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    return True


# check if bullet hit an enemy
def check_bullet_enemy_collision(bullets, enemies):
    for bullet in bullets:
        bullet.move()
        if not bullet.active:
            bullets.remove(bullet)
            continue
        for enemy in enemies:
            dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
            if dist <= enemy.radius + bullet.size:
                enemy.health -= 10
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    return True
                bullet.active = False
                break
        bullet.draw(screen)
#home screen
def home_screen():
    title_font = pygame.font.SysFont(None, 72)
    instruction_font = pygame.font.SysFont(None, 36)

    title_text = title_font.render("Attack of the orbs", True, (0, 255, 0))
    instruction_text = instruction_font.render("Press any key to start", True, (255, 255, 255))

    while True:
        screen.fill((0, 0, 0))
        screen.blit(title_text, (screen_size[0] // 2 - title_text.get_width() // 2, screen_size[1] // 3))
        screen.blit(instruction_text, (screen_size[0] // 2 - instruction_text.get_width() // 2, screen_size[1] // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                return 


#death screen
def death_screen():
    title_font = pygame.font.SysFont(None, 72)
    instruction_font = pygame.font.SysFont(None, 36)

    title_text = title_font.render("Game Over", True, (255, 0, 0))
    instruction_text = instruction_font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))

    while True:
        screen.fill((0, 0, 0))
        screen.blit(title_text, (screen_size[0] // 2 - title_text.get_width() // 2, screen_size[1] // 3))
        screen.blit(instruction_text, (screen_size[0] // 2 - instruction_text.get_width() // 2, screen_size[1] // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game()
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()

#bar to show upgrade progress
def draw_upgrade_bar(kills_since_upgrade, req_kills):
    bar_x = 150
    bar_y = 100
    bar_width = 500
    bar_height = 20 
    corner_radius = 10
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=corner_radius)
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * kills_since_upgrade/req_kills, bar_height), border_radius=corner_radius)

    progress_label = font.render(f"Upgrade Progress", True, (255, 255, 255))
    screen.blit(progress_label, (bar_x+(bar_width/2)-progress_label.get_width()//2, bar_y - 30))

# function to display FPS
def display_fps():
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 100))

# main game function
def game():
    global x_speed, y_speed, angle_offset, enemies, last_spawn_time, fire_delay, soccer_ball_num, soccer_balls, razor_speed

    START_TIME = pygame.time.get_ticks() #time when game starter
    last_spawn_time = pygame.time.get_ticks()
    last_shot = 0 
    player_obj = player()
    enemies = []
    spawn_interval = 2000 
    bullets = []
    kills = 0
    req_kills = 2
    kills_since_upgrade = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
    
        time_since_start = pygame.time.get_ticks() - START_TIME
        current_time = pygame.time.get_ticks()
        #clear the screen
        screen.fill((0, 0, 0))

        #fire a bullet every one second
        if(current_time - fire_delay >= last_shot):
            last_shot = current_time
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_center_x = player_obj.x + player_obj.width // 2
            player_center_y = player_obj.y + player_obj.height // 2
            bullets.append(Bullet(player_center_x, player_center_y, mouse_x, mouse_y))
        
        spawn_interval = calc_interval(time_since_start, spawn_interval) #calculate spawn interval based on time since start
        enemies, last_spawn_time = spawn_enemies(last_spawn_time, START_TIME, spawn_interval) #spawn enemies

        dt = clock.get_time()
        x_speed, y_speed = movement(x_speed, y_speed) #calc player speed
        
        player_obj.update(dt) #update player animation
        player_obj.move() #move the player
        player_obj.check_bounds() #check if player hit a wall
        player_obj.draw(screen)# draw the player
        player_obj.draw_health_bar() #draw the players health bar

        #draw spinning balls
        balls = draw_balls(screen, player_obj.x + player_obj.width // 2, player_obj.y + player_obj.height // 2, num_balls, angle_offset=angle_offset)
        #draw soccer balls
        draw_soccer_balls(soccer_balls)
        killed, kills = check_enemy_soccer_ball_collision(soccer_balls, enemies, kills)
        if killed: 
            kills_since_upgrade += 1
        #check if if enemy hit a spinning ball or bullet
        if(check_bullet_enemy_collision(bullets, enemies)):
            kills+=1
            kills_since_upgrade+=1
        if(check_enemy_collision(balls, enemies)):
            kills += 1
            kills_since_upgrade+=1
        #check if player hit an enemy
        for enemy in enemies:
            if(player_obj.check_collision(enemy)):
                player_obj.health -= enemy.damage
                enemies.remove(enemy)
                if player_obj.health <= 0:
                   death_screen()
                   return
            #move the enemies
            enemy.move(player_obj.x + player_obj.width // 2, player_obj.y + player_obj.height // 2)
            enemy.draw(screen)
            enemy.draw_health()   

        #rotate the balls
        angle_offset += razor_speed 

        #display the time since
        elapsed_sec = time_since_start // 1000
        minutes = elapsed_sec // 60
        seconds = elapsed_sec % 60
        elapsed_time_text = f"Time: {minutes:02}:{seconds:02}"
        elapsed_time_surface = font.render(elapsed_time_text, True, (255, 255, 255))
        screen.blit(elapsed_time_surface, (10, 10))

        #display kills
        kills_text = f"Kills: {kills}"
        kills_surface = font.render(kills_text, True, (255, 255, 255))
        screen.blit(kills_surface, (10, 50))

        draw_upgrade_bar(kills_since_upgrade, req_kills)

        if kills_since_upgrade >= req_kills:
            upgrade_menu()
            kills_since_upgrade = 0
            req_kills = int(req_kills * 1.85)
            soccer_balls = get_soccer_balls(soccer_ball_num)

        #display FPS
        display_fps()
        #update the screen
        pygame.display.flip()
        #cap FPS
        clock.tick(60)

home_screen()
game()
pygame.quit()
