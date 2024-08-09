import pygame
import sys
from time import sleep
from settings import Settings
from ship import Ship
from bullets import Bullet
from alien import Aliens
from gamestats import GameStats
from button import Button
from scoreboard import ScoreBoard
class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.game_active = False
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        pygame.display.set_caption('Alien Invasion')
        self.stats = GameStats(self)
        self.sb = ScoreBoard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.create_fleet()
        self.play_button = Button(self,"Play")
    def ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.bullets.empty()
            self.aliens.empty()
            self.create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)
        

    def check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self.ship_hit()
                break
    def update_aliens(self):
        self.check_feet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self.ship_hit()
        self.check_aliens_bottom()
    def check_feet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction()
                break
    def change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
    def run_game(self):
        while True:
            self.check_events()
            if self.game_active:
                self.ship.update()
                self.bullets.update()
                self.update_bullets()
                self.update_aliens()
            self.update_screen()
            self.clock.tick(60)
    def create_aliens(self,x_position,y_position):
        new_alien = Aliens(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)
    def create_fleet(self):
        alien = Aliens(self)
        alien_width,alien_height = alien.rect.size
        current_x,current_y = alien_width,alien_height
        while current_y < (self.settings.screen_height -5*alien_height):
            while current_x < (self.settings.screen_width -2*alien_width):
                self.create_aliens(current_x,current_y)
                current_x += 2 * alien_width
            current_x = alien_width
            current_y += 2 * alien_height
    def update_bullets(self):
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        print(len(self.bullets))
        collisions = pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points*len(aliens)
            self.stats.score += self.settings.alien_points
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            self.bullets.empty()
            self.create_fleet()
            self.settings.increase_speed()
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.check_play_button(mouse_pos)
    def check_play_button(self,mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_ships()
            self.game_active = True
            self.bullets.empty()
            self.aliens.empty()
            self.create_fleet()
            self.ship.center_ship()
            pygame.mouse.set_visible(False)
            
    def check_keydown_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()
    def fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    def check_keyup_events(self,event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    def update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        if not self.game_active:
            self.play_button.draw_button()
        pygame.display.flip()
if __name__=='__main__':
    ai = AlienInvasion()
    ai.run_game()