#include <SDL2/SDL.h>
#include <assert.h>
#include <stdio.h>

#include "kartyak.h"

#define WIN_WIDTH 	960
#define WIN_HEIGHT 	540

#define CARD_WIDTH	112
#define CARD_HEIGHT	186

#define FILL_CARD_RECT(r, X, Y) do { \
	r.w = CARD_WIDTH; \
	r.h = CARD_HEIGHT; \
	r.x = X; \
	r.y = Y; \
} while (0)\

#define RECT_POINT_COLLISION(R, X, Y) (R.x<X && R.x+R.w>X && R.y<Y && R.y+R.h>Y)

#define ANIM_Y 10.0f
#define ANIM_T 200

typedef
struct {
    bool prev;
    bool curr;
} StateStruct;

typedef struct {
    SDL_Rect start;
    SDL_Rect dest;
    Uint32 start_time;
    Uint32 duration;
    enum {
        NONE,
        UP,
        DOWN,
    } state;
} CardHoverAnim;

SDL_Texture *
create_card_texture(SDL_Renderer *renderer, unsigned char *card_data, int card_data_len){

    SDL_Texture* texture = SDL_CreateTexture(renderer,
                    SDL_PIXELFORMAT_RGB24,
                    SDL_TEXTUREACCESS_STATIC,
                    CARD_WIDTH,
                    CARD_HEIGHT);
    assert(texture);

    SDL_UpdateTexture(texture, NULL, card_data,  CARD_WIDTH * 3);

    return texture;
}

int
main(int argc, char* argv[]) {

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) < 0) {
        printf("SDL initialization failed: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Window* window = SDL_CreateWindow("Zsir",
            SDL_WINDOWPOS_UNDEFINED,
            SDL_WINDOWPOS_UNDEFINED,
            WIN_WIDTH, WIN_HEIGHT,
            SDL_WINDOW_SHOWN);
    assert(window);

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    assert(renderer);

    SDL_Texture *tok_kiraly_texture = create_card_texture(renderer, __makk_also_ppm, __makk_also_ppm_len);
    assert(tok_kiraly_texture);

    SDL_Rect tok_kiraly_rect;
    FILL_CARD_RECT(tok_kiraly_rect, CARD_WIDTH * 4, 69);

    const SDL_Rect down = {
        .x = CARD_WIDTH * 4, .y = 69, .w = CARD_WIDTH, .h = CARD_HEIGHT
    };

    const SDL_Rect up = {
        .x = CARD_WIDTH * 4, .y = 59, .w = CARD_WIDTH, .h = CARD_HEIGHT
    };

    CardHoverAnim anim;
    anim.state = CardHoverAnim::NONE;
    bool quit  = false;

    StateStruct hovering = {
        .prev = false, .curr = false,
    };

    while (!quit) {

        Uint32 tcurrent = SDL_GetTicks();
        SDL_Event event;
        if (SDL_PollEvent(&event)) {
            switch (event.type) {

            case SDL_QUIT:
                quit = true;
                break;

            case SDL_MOUSEMOTION:
                hovering.curr = RECT_POINT_COLLISION(tok_kiraly_rect,
                            event.motion.x,
                            event.motion.y);
                if (!hovering.prev && hovering.curr){
                    if (anim.state == CardHoverAnim::NONE){
                        anim.duration = ANIM_T;
                        anim.dest = up; anim.start = down;
                    }
                    else {
                        anim.duration = anim.duration - (tcurrent-anim.start_time);
                        anim.start = tok_kiraly_rect;
                        anim.dest  = up;
                    }
                    anim.start_time = tcurrent;
                    anim.state = CardHoverAnim::UP;
                }
                else if (hovering.prev && !hovering.curr) {
                    if (anim.state == CardHoverAnim::NONE){
                        anim.duration = ANIM_T;
                        anim.start = up; anim.dest = down;
                    }
                    else {
                        anim.duration = anim.duration - (tcurrent-anim.start_time);
                        anim.start = tok_kiraly_rect;
                        anim.dest  = down;
                    }
                    anim.start_time = tcurrent;
                    anim.state = CardHoverAnim::DOWN;
                }
                hovering.prev = hovering.curr;
                break;
            default:
                break;
            }

        }

        
        if (anim.state != CardHoverAnim::NONE) {
            if (tcurrent > anim.start_time + anim.duration){
                anim.state = CardHoverAnim::NONE;
            }
            else {
                float factor = ((float)(tcurrent - anim.start_time))/anim.duration;
                tok_kiraly_rect.y = (float)anim.start.y * (1.0f-factor) + (float)anim.dest.y * factor;
            }
        }

        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, tok_kiraly_texture, NULL, &tok_kiraly_rect);
        SDL_RenderPresent(renderer);

    }

    SDL_DestroyTexture(tok_kiraly_texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
