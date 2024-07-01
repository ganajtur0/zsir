import pygame as pg
import os
from tween import *
from enum import Enum

from zsir import *

class ANIM_DIRECTION(Enum):
    UP = 1
    DOWN = -1

CARD_WIDTH  = 112
CARD_HEIGHT = 186

if not pg.font:
    print("Warning: fonts disabled")
if not pg.mixer:
    print("Warning: audio disabled")

main_dir = os.path.split(os.path.abspath(__file__))[0]
res_dir = os.path.join(main_dir, "res")

def load_image(name, scale=1):
    full_name = os.path.join(res_dir, name)
    image = pg.image.load(full_name)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.scale(image, size)

    image = image.convert()

    return image, image.get_rect()


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (46, 186, 76)


class ButtonSprite(pg.sprite.Sprite):
    def __init__(self,
                 pos,
                 width,
                 height,
                 color,
                 hover_color,
                 disabled_color,
                 text,
                 onclick_function):
        pg.sprite.Sprite.__init__(self)

        self.onclick_function = onclick_function

        self.color = color
        self.hover_color = hover_color
        self.disabled_color = disabled_color

        self.image = pg.Surface([width, height])

        self.rect = self.image.get_rect(center=pos)
        
        self.text = text    
        self.font = pg.font.Font(None, 24)

        self.image.fill(self.color)
        self.render_text()
        
        self.handled = False
        self.enabled = False

    def update(self):
        if self.enabled:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.image.fill(self.hover_color)
                if (pg.mouse.get_pressed()[0] and 
                    not self.handled):
                    self.handled = True
                    self.rect.move_ip(0, 5)
                    self.onclick_function()
                if (not pg.mouse.get_pressed()[0] and
                    self.handled):
                    self.handled = False
                    self.rect.move_ip(0, -5)
            else:
                self.image.fill(self.color)
            self.image.blit(self.text_surface, self.text_rect)
        else:
            self.image.fill(self.disabled_color)

    def render_text(self):
        self.text_surface = self.font.render(self.text, True, BLACK)
        self.text_rect = self.text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        self.image.blit(self.text_surface, self.text_rect)


class CardSprite(pg.sprite.Sprite):
    def __init__(self,
                 card,
                 topleft_x,
                 topleft_y,
                 hidden=False,
                 flipped=False,
                 clickable=True):
        pg.sprite.Sprite.__init__(self)
        self.card = card
        self.name = card_filename(card)
        self.hidden = hidden
        self.flipped = flipped
        if self.hidden:
            self.image, self.rect = load_image(os.path.join("lapok", "hatlap.jpg"))
            self.display_image, _ = load_image(os.path.join("lapok", f"{self.name}.jpg"))
        else:
            self.image, self.rect = load_image(os.path.join("lapok", f"{self.name}.jpg"))
            self.display_image = self.image
        if self.flipped:
            self.image = pg.transform.flip(self.image, False, True)
        self.rect.topleft = (topleft_x, topleft_y)
        self.clickable = clickable

        self.timer_down = True
        self.timer_start = None
        self.timeout = None

        self.anim_target_top = self.rect.top - 20
        self.anim_target_bottom = self.rect.top
        self.anim_target = self.anim_target_top
        self.anim_direction = ANIM_DIRECTION.UP
        self.animating = False
        self.mouse_entered = False
        self.last_time = None

    def update(self):
        if self.hidden:
            return
        if (self.timer_down and not self.animating):
            mouse_state = self.rect.collidepoint(pg.mouse.get_pos())
            if (self.mouse_entered):
                if (not mouse_state and
                    self.rect.top == self.anim_target_top):
                    self.mouse_entered = False
                    self.animating = True
                    self.last_time = pg.time.get_ticks()
                    self.anim_direction = ANIM_DIRECTION.DOWN
                    self._set_timer()
            elif (mouse_state and
                  not self.rect.top == self.anim_target_top):
                self.animating = True
                self.last_time = pg.time.get_ticks()
                self.anim_direction = ANIM_DIRECTION.UP
                self._set_timer()
            self.mouse_entered = mouse_state
        elif self.animating:
            dt = pg.time.get_ticks() - self.last_time
            match self.anim_direction:
                case ANIM_DIRECTION.UP:
                    if not self.rect.top < self.anim_target_top:
                        self.rect.move_ip(0, -0.2 * dt)
                    else:
                        self.rect.top = self.anim_target_top
                        self.animating = False
                case ANIM_DIRECTION.DOWN:
                    if not self.rect.top > self.anim_target_bottom:
                        self.rect.move_ip(0, 0.2 * dt)
                    else:
                        self.rect.top = self.anim_target_bottom
                        self.animating = False
            self.last_time = pg.time.get_ticks()

        self._update_timer()

    def move_to(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def _set_timer(self, timeout=200):
        self.timer_start = pg.time.get_ticks()
        self.timeout = timeout
        self.timer_down = False

    def _update_timer(self):
        if not self.timer_start:
            return
        if (pg.time.get_ticks() - self.timer_start >= self.timeout):
            self.timer_down = True


class Timer:
    def __init__(self):
        self.timeout = 1
        self.start_time = 0
        self.started = False
    
    def start(self, timeout=1):
        self.timeout = timeout * 1000
        self.start_time = pg.time.get_ticks()
        self.started = True
    
    def tick(self):
        if not self.started:
            return True
        if pg.time.get_ticks() - self.start_time >= self.timeout:
            self.started = False
            return True
        return False


class HouseSprite(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.scr_width, self.scr_height = pg.display.get_surface().get_size()
        self.rect = self.image.get_rect(center=(self.scr_width//2, self.scr_height//2))
        self.image.fill(BACKGROUND_COLOR)
        self.clickable = False
        self.animating = False
        self.animation_max_y = self.scr_height - CARD_HEIGHT
        self.animation_max_x = self.scr_width - 2*CARD_WIDTH

    def update_image(self, image):
        self.image = image

    def animate(self, position):
        match(position):
            case 0:
                self.animation_max_y = self.scr_height
                self.animation_max_x = 2*CARD_WIDTH
            case 1:
                self.animation_max_y = -CARD_HEIGHT
                self.animation_max_x = 2*CARD_WIDTH
            case 2:
                self.animation_max_y = self.scr_height - CARD_HEIGHT
                self.animation_max_x = self.scr_width - 2*CARD_WIDTH
            case 3:
                self.animation_max_y = self.scr_height - CARD_HEIGHT
                self.animation_max_x = self.scr_width - 2*CARD_WIDTH

        self.animating = True
        self.tween_y = Tween(self.rect.y,
                           end=self.animation_max_y,
                           duration=500,
                           easing=Easing.LINEAR,
                           easing_mode=EasingMode.OUT)
        self.tween_x = Tween(self.rect.x,
                           end=self.animation_max_x,
                           duration=500,
                           easing=Easing.LINEAR,
                           easing_mode=EasingMode.OUT)
        self.tween_x.start()
        self.tween_y.start()

    def update(self):
        if self.animating:
            self.tween_y.update()
            self.tween_x.update()
            self.rect.y = self.tween_y.value
            self.rect.x = self.tween_x.value
            if (round(self.tween_y.value) == self.animation_max_y or
                round(self.tween_x.value) == self.animation_max_x):
                self.reset()

    def reset(self):
        self.animating = False
        self.image = pg.Surface((CARD_WIDTH, CARD_HEIGHT))
        self.rect = self.image.get_rect(center=(self.scr_width//2, self.scr_height//2))
        self.image.fill(BACKGROUND_COLOR)

class GameOverScreen(pg.sprite.Sprite):
    def __init__(self,
                 size,
                 padding,
                 player_names,
                 player_scores,
                 text,
                 reset_func):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(size)
        self.scr_width, self.scr_height = pg.display.get_surface().get_size()
        self.rect = self.image.get_rect(center=(self.scr_width//2, self.scr_height//2))
        self.image.fill(pg.Color("pink"))
        self.title_font = pg.font.Font(None, 40)
        self.title_font.bold = True
        self.subfont = pg.font.Font(None, 24)
        self.text = text
        self.padding = padding
        self.names = player_names
        self.scores = player_scores
        self.size = size
        self.button_click_handled = False
        self.reset_func = reset_func
        self.render_text()
    
    def render_text(self):
        self.title_font_surface = self.title_font.render(self.text, True, BLACK)
        self.title_font_rect = self.title_font_surface.get_rect(center=(self.rect.width//2, self.padding[1]))
        self.player_texts = []
        for i in range(len(self.names)):
            name_surface = self.subfont.render(self.names[i], True, BLACK)
            name_rect = name_surface.get_rect()
            name_rect.x = self.padding[0]
            name_rect.y = self.padding[1] * (i*2+4)
            score_surface = self.subfont.render(str(self.scores[i]), True, BLACK)
            score_rect = score_surface.get_rect()
            score_rect.x = self.rect.width - self.padding[0] - score_rect.width
            score_rect.y = self.padding[1] * (i*2+4)
            self.player_texts.append([(name_surface, name_rect),(score_surface, score_rect)])

        self.image.blit(self.title_font_surface, self.title_font_rect)

        for player_text in self.player_texts:
            self.image.blit(player_text[0][0], player_text[0][1])
            self.image.blit(player_text[1][0], player_text[1][1])

        self.tween = Tween(self.title_font_rect.height//2 + self.padding[1],
                           self.title_font_rect.height//2 + self.padding[1]*2,
                           duration=800, easing=EasingMode.IN_OUT,
                           boomerang=True, loop=True)
        self.tween.start()

    def update(self):
        self.tween.update()
        self.title_font_rect.y = self.tween.value
        self.image.fill(pg.Color("pink"))
        # self.restart_button.update()
        # self.image.blit(self.restart_button.image, self.restart_button.rect)
        self.image.blit(self.title_font_surface, self.title_font_rect)
        for player_text in self.player_texts:
            self.image.blit(player_text[0][0], player_text[0][1])
            self.image.blit(player_text[1][0], player_text[1][1])
            
class GameGUI:
    def __init__(self):
        self.animation_playing = False
        self.timer = Timer()
        self.has_screen = False
        self.game_over_screen_sprite = None
        self.card_spritegroup = pg.sprite.Group()
        self.button_spritegroup = pg.sprite.Group()
        self.pg_init()

    def pg_init(self):
        pg.init()
        self.screen = pg.display.set_mode((1280, 720), pg.SCALED)
        pg.display.set_caption("Zsír")
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = pg.display.get_surface().get_size()
        self.player_cards_y = self.SCREEN_HEIGHT // 2 + CARD_HEIGHT * 1.5
        self.opponent_cards_y = -1 * CARD_HEIGHT // 2

        self.font = pg.font.Font(None, 24)

        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill(BACKGROUND_COLOR)
        self.screen.blit(self.background, (0,0))
        pg.display.flip()

    def restart_game(self):
        self.zsirjatek.restart()
        if self.game_over_screen_sprite:
            self.button_spritegroup.remove(self.restart_button)
            self.button_spritegroup.remove(self.game_over_screen_sprite)
            self.game_over_screen_sprite = None
            self.has_screen = False
        self.create_card_sprites()
        self.rearrange_card_sprites(self.player_cards)
        self.rearrange_card_sprites(self.opponent1_cards)

    def start_game(self):
        self.zsirjatek = Zsir([Player("Te", False),
                              Player("Gyula", True)],
                              0, 0)
        self.zsirjatek.deal()
        self.create_button_sprites()
        self.create_card_sprites()
        self.rearrange_card_sprites(self.player_cards)
        self.rearrange_card_sprites(self.opponent1_cards)
        self.clock = pg.time.Clock()
        self.timer = Timer()
        self.mainloop()

    def create_card_sprites(self):
        if self.zsirjatek.num_players == 2:
            self.player_cards = [
                CardSprite(card, 0, self.player_cards_y)
                for card in self.zsirjatek.players[0].hand
            ]
            self.card_spritegroup.add(self.player_cards)
            self.opponent1_cards = [
                CardSprite(card, 0, self.opponent_cards_y,
                           hidden=True, flipped=True,
                           clickable=False)
                for card in self.zsirjatek.players[1].hand
            ]
            self.card_spritegroup.add(self.opponent1_cards)
        else:
            pass

    def update_card_sprites(self):
        if self.zsirjatek.num_players == 2:
            player_cards = [card_sprite.card for card_sprite in self.player_cards]
            player_new_cards = [
                CardSprite(card, 0, self.player_cards_y)
                for card in self.zsirjatek.players[0].hand
                if card not in player_cards
            ]
            self.player_cards += player_new_cards
            self.card_spritegroup.add(player_new_cards)

            opponent1_cards = [card_sprite.card for card_sprite in self.opponent1_cards]
            opponent1_new_cards = [
                CardSprite(card, 0, self.opponent_cards_y,
                           hidden=True, flipped=True,
                           clickable=False)
                for card in self.zsirjatek.players[1].hand
                if card not in opponent1_cards
            ]
            self.opponent1_cards += opponent1_new_cards
            self.card_spritegroup.add(opponent1_new_cards)

            self.rearrange_card_sprites(self.player_cards)
            self.rearrange_card_sprites(self.opponent1_cards)
        else:
            pass

    def let_it_go(self):
        self.zsirjatek.let_it_go_decision = True
        self.finish_round()
        print("ELENGED")

    def create_button_sprites(self):
        self.let_it_go_button = ButtonSprite((self.SCREEN_WIDTH//2,
                           self.SCREEN_HEIGHT//2 + 150),
                           200, 60,
                           (140, 170, 160),
                           (70, 80, 80),
                           BACKGROUND_COLOR,
                           "Elenged",
                           self.let_it_go)
        self.house_sprite = HouseSprite()
        self.button_spritegroup.add((self.let_it_go_button, self.house_sprite))

    def game_over_screen(self):
        result = self.zsirjatek.evaluate_game()
        match (result):
            case EndResult.WON:
                final_text = "Azoszt igen ez igen"
            case EndResult.LOST:
                final_text = "Gyakorolj még asztán keress meg"
        self.game_over_screen_sprite = GameOverScreen((480, 480),
                                              (20, 20),
                                              [p.name for p in self.zsirjatek.players],
                                              [p.score for p in self.zsirjatek.players],
                                              final_text,
                                              self.restart_game)
        self.restart_button = ButtonSprite((640, 500),
                                           200, 80,
                                           pg.Color("brown1"),
                                           pg.Color("brown"),
                                           pg.Color("brown1"),
                                           "Még egy kör",
                                           self.restart_game)
        self.restart_button.enabled = True
        self.button_spritegroup.add(self.game_over_screen_sprite)
        self.button_spritegroup.add(self.restart_button)     
        self.has_screen = True
    
    def rearrange_card_sprites(self, card_sprites):
        scr_width_half = self.SCREEN_WIDTH // 2
        try:
            y = card_sprites[0].rect.top
        except IndexError:
            return
        if self.zsirjatek.num_players == 2:
            match len(card_sprites):
                case 4:
                    card_sprites[0].move_to(scr_width_half - 2*CARD_WIDTH, y)
                    card_sprites[1].move_to(scr_width_half - CARD_WIDTH, y)
                    card_sprites[2].move_to(scr_width_half, y)
                    card_sprites[3].move_to(scr_width_half + CARD_WIDTH, y)
                case 3:
                    card_sprites[0].move_to(scr_width_half - 1.5*CARD_WIDTH, y)
                    card_sprites[1].move_to(scr_width_half - 0.5*CARD_WIDTH, y)
                    card_sprites[2].move_to(scr_width_half + 0.5*CARD_WIDTH, y)
                case 2:
                    card_sprites[0].move_to(scr_width_half - CARD_WIDTH, y)
                    card_sprites[1].move_to(scr_width_half, y)
                case 1:
                    card_sprites[0].move_to(scr_width_half - 0.5*CARD_WIDTH, y)
                case _:
                    return
                    
    def update_hand(self, hand, card_sprite):
        self.zsirjatek.make_move(card_sprite.card)
        hand.remove(card_sprite)
        self.house_sprite.update_image(card_sprite.display_image)
        self.rearrange_card_sprites(hand)
        card_sprite.kill()
    
    def finish_round(self):
        if self.zsirjatek.evaluate_round():
            self.let_it_go_button.enabled = True
            return
        self.house_sprite.animate(self.zsirjatek.current_player)
        self.update_card_sprites()
        self.timer.start(1)

    def wait(self, seconds):
        self.timer.start(seconds)
        while not self.timer.tick():
            self.redraw()

    def handle_click(self):
        pos = pg.mouse.get_pos()
        clicked_cards = [card for card in self.card_spritegroup if card.rect.collidepoint(pos)]
        for sprite in clicked_cards:
            if sprite.clickable:
                self.update_hand(self.player_cards, sprite)
                self.wait(0.5)
                if self.zsirjatek.next_player():
                    self.finish_round()
                else:
                    self.let_it_go_button.enabled = False
                    self.timer.start(1)
                break

    def handle_ai_move(self):
        ai_card = self.zsirjatek.ai_move(self.let_it_go_button.enabled)
        if not ai_card:
            self.let_it_go()
            self.finish_round()
            return
        for sprite in self.opponent1_cards:
            if sprite.card == ai_card:
                self.update_hand(self.opponent1_cards, sprite)
                self.wait(0.5)
                if self.zsirjatek.next_player():
                    self.finish_round()
                else:
                    self.let_it_go_button.enabled = False
                break

    def eventhandler(self, event):
        match (event.type):
            case pg.QUIT:
                self.going = False
            case pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.going = False
            case pg.MOUSEBUTTONUP:
                if not self.zsirjatek.game_over:
                    self.handle_click()

    def set_timer_down(self):
        self.timer_down = True

    def redraw(self):
        self.card_spritegroup.update()
        self.button_spritegroup.update()
        self.screen.blit(self.background, (0, 0))
        self.card_spritegroup.draw(self.screen)
        self.button_spritegroup.draw(self.screen)
        pg.display.flip()

    def mainloop(self):
        self.going = True
        while (self.going):
            self.clock.tick(60)
            if self.zsirjatek.game_over:
                if not self.has_screen:
                    self.game_over_screen()
                for event in pg.event.get():
                    self.eventhandler(event)
            else:
                if self.timer.tick():
                    if self.zsirjatek.current_player == self.zsirjatek.human:
                        for event in pg.event.get():
                            self.eventhandler(event)
                    elif self.zsirjatek.current_player != self.zsirjatek.human:
                        self.handle_ai_move()    
            self.redraw()
        pg.quit()


if __name__ == "__main__":
#     main()
    game_gui = GameGUI()
    game_gui.start_game()