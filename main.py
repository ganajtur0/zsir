import pygame as pg
import os
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


class CardSprite(pg.sprite.Sprite):
    def __init__(self,
                 card,
                 topleft_x,
                 topleft_y,
                 hidden=False,
                 flipped=False):
        pg.sprite.Sprite.__init__(self)
        self.card = card
        self.name = card_filename(card)
        self.hidden = hidden
        self.flipped = flipped
        if self.hidden:
            self.image, self.rect = load_image(os.path.join("lapok", "hatlap.jpg"))
        else:
            self.image, self.rect = load_image(os.path.join("lapok", f"{self.name}.jpg"))
        if self.flipped:
            self.image = pg.transform.flip(self.image, False, True)
        self.rect.topleft = (topleft_x, topleft_y)

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


def rearrange_card_sprites(card_sprites):
    try:
        y = card_sprites[0].rect.top
    except IndexError:
        return
    SCREEN_WIDTH, _ = pg.display.get_surface().get_size()
    scr_width_half = SCREEN_WIDTH//2
    print(len(card_sprites))
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
        

def main():
    zsirjatek = Zsir([Player("Te", False),
                     Player("Gyula", True)])
    pg.init()
    screen = pg.display.set_mode((1280, 720), pg.SCALED)
    pg.display.set_caption("Zsír")
    pg.mouse.set_visible(True)
    SCREEN_WIDTH, SCREEN_HEIGHT = pg.display.get_surface().get_size()
    player_cards_y = SCREEN_HEIGHT/2 + CARD_HEIGHT*1.5
    opponent_cards_y = -1 * CARD_HEIGHT/2

    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((46, 186, 76))
    screen.blit(background, (0,0))
    pg.display.flip()

    zsirjatek.deal()

    player_hand = [CardSprite(zsirjatek.players[0].hand[i],
                               400 + i * CARD_WIDTH,
                               player_cards_y)
                    for i in range(4)]
    rearrange_card_sprites(player_hand)
    opponent_hand = [CardSprite(zsirjatek.players[1].hand[i],
                               400 + i * CARD_WIDTH,
                               opponent_cards_y,
                               hidden=True,
                               flipped=True)
                    for i in range(4)]
    
    card_sprites = player_hand + opponent_hand

    allsprites = pg.sprite.RenderPlain(card_sprites)

    clock = pg.time.Clock()

    going = True
    while going:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False
            elif event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                clicked_cards = [card for card in allsprites if card.rect.collidepoint(pos)]
                for card_sprite in clicked_cards:
                    print(card_sprite.name)
                    zsirjatek.house.append(card_sprite.card)
                    player_hand.remove(card_sprite)
                    rearrange_card_sprites(player_hand)
                    card_sprite.kill()
        allsprites.update()
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()