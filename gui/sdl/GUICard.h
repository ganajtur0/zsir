#ifndef GUICARD_H
#define GUICARD_H

#include <SDL2/SDL.h>
#include <assert.h>
#include "card.h"

static const int CARD_WIDTH = 112;
static const int CARD_HEIGHT = 186;

class GUICard {

    static const bool RECT_POINT_COLLISION(SDL_Rect R, Sint32 X, Sint32 Y) {
        return (R.x<X && R.x+R.w>X && R.y<Y && R.y+R.h>Y);
    }
    static const int  HOVER_ANIM_DURATION = 150;

    // is this too C-ish ?
    struct StateStruct {
        bool prev;
        bool curr;
        StateStruct() {
            prev = false;
            curr = false;
        };
        void update(bool n){
            prev = curr;
            curr = n;
        }
    };

    struct HoverAnim {

        typedef enum { NONE, UP, DOWN } State;

        SDL_Rect *rect;
        SDL_Rect up;
        SDL_Rect down;
        SDL_Rect start;
        SDL_Rect dest;
        Uint32   start_time;
        Uint32   duration;
        State    state;

        HoverAnim() = default;
        HoverAnim(SDL_Rect *rect, SDL_Rect up, SDL_Rect down) : rect(rect), up(up), down(down) {
            state = NONE;
        };

        void update(State _state, Uint32 tcurrent) {
            switch (_state){
            case UP:
                if (state == NONE){
                    duration = HOVER_ANIM_DURATION;
                    dest = up; start = down;
                } else {
                    duration = duration - (tcurrent-start_time);
                    start    = *rect;
                    dest     = up;
                }
                start_time = tcurrent;
                state = _state;
                break;
            case DOWN:
                if (state == NONE){
                    duration = HOVER_ANIM_DURATION;
                    dest = down; start = up;
                } else {
                    duration = duration - (tcurrent-start_time);
                    start    = *rect;
                    dest     = down;
                }
                start_time = tcurrent;
                state = _state;
                break;
            default:
                break;
            }
        };

        void animate(Uint32 tcurrent) {
            if (state != NONE) {
                if (tcurrent > start_time + duration)
                    state = NONE;
                else {
                    float factor = ((float)(tcurrent - start_time))/duration;
                    rect->y = (float)start.y * (1.0f-factor) + (float)dest.y * factor;
                }
            }
        }
    };

    StateStruct hover_state;

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

public:

    SDL_Rect    rect;
    SDL_Texture *texture;
    HoverAnim   hover_anim;
    
    GUICard() = default;
    GUICard(SDL_Renderer *renderer,
            unsigned char *card_data,
            int card_data_len, int x, int y,
            SDL_Rect hover_up, SDL_Rect hover_down) {

        texture = create_card_texture(renderer, card_data, card_data_len);
        rect.w = CARD_WIDTH; rect.h = CARD_HEIGHT;
        rect.x = x; rect.y = y;
        hover_state = StateStruct();
        hover_anim  = HoverAnim(&rect, hover_up, hover_down);

    };

    ~GUICard() { SDL_DestroyTexture(texture); };

    void handle_mouse_motion(Sint32 x, Sint32 y, Uint32 tcurrent){
        // printf("rect.x - rect.y: %d - %d\n", rect.x, rect.y);
        hover_state.update(RECT_POINT_COLLISION(rect, x, y));
        if (!hover_state.prev && hover_state.curr){
            hover_anim.update(HoverAnim::UP, tcurrent);
        } else if (hover_state.prev && !hover_state.curr){
            hover_anim.update(HoverAnim::DOWN, tcurrent);
        }
    }

};

#endif //GUICARD_H
