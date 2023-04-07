#include "GUICard.h"

#include <SDL2/SDL.h>
#include <assert.h>
#include <stdio.h>

#include "kartyak.h"

#define WIN_WIDTH 	960
#define WIN_HEIGHT 	540

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

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    assert(renderer);

    SDL_Rect down;
    SDL_Rect up;
    down.y = 69; down.x = 69;
    up.y   = 59; up.x   = 69;

    // GUICard guicards[4];
    
    GUICard c = GUICard(renderer, __tok_kiraly_ppm, __tok_kiraly_ppm_len, 69, 69, up, down);

    /*
    for (int i = 0; i<1; i++){
        up.x = down.x = 69 + i*CARD_WIDTH; 
        guicards[i] = GUICard(renderer, __tok_kiraly_ppm, __tok_kiraly_ppm_len, up.x, 69, up, down);
    }
    */

    bool quit = false;

    while (!quit) {

        Uint32 tcurrent = SDL_GetTicks();
        SDL_Event event;
        if (SDL_PollEvent(&event)) {
            switch (event.type) {

            case SDL_QUIT:
                quit = true;
                break;

            case SDL_MOUSEMOTION:
                c.handle_mouse_motion(event.motion.x, event.motion.y, tcurrent);
                /*
                for (int i = 0; i<1; i++)
                    guicards[i].handle_mouse_motion(event.motion.x, event.motion.y, tcurrent);
                */
                break;

            }
        }


        SDL_RenderClear(renderer);
        c.hover_anim.animate(tcurrent);        
        SDL_RenderCopy(renderer, c.texture, NULL, &c.rect);
        /*
        for (int i = 0; i<1; i++){
            guicards[i].hover_anim.animate(tcurrent);        
            SDL_RenderCopy(renderer, guicards[i].texture, NULL, &guicards[i].rect);
        }
        */
        SDL_RenderPresent(renderer);

    }

    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
