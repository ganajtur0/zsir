#include <SDL2/SDL.h>
#include <stdio.h>
/*
#define STB_IMAGE_IMPLEMENTATION
#define STB_ONLY_PNM
#include "stb_image.h"
*/
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

SDL_Texture *
create_card_texture(SDL_Renderer *renderer, unsigned char *card_data, int card_data_len){
    	SDL_Texture* texture = SDL_CreateTexture(renderer,
						SDL_PIXELFORMAT_RGB24,
						SDL_TEXTUREACCESS_STATIC,
						CARD_WIDTH,
						CARD_HEIGHT);
	if (!texture)
		return texture;

    	SDL_UpdateTexture(texture, NULL, card_data,  CARD_WIDTH * 3);

	return texture;
}

int
main(int argc, char* argv[]) {

    // Initialize SDL
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("SDL initialization failed: %s\n", SDL_GetError());
        return 1;
    }

    // Create a window
    SDL_Window* window = SDL_CreateWindow("Zsír", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, WIN_WIDTH, WIN_HEIGHT, SDL_WINDOW_SHOWN);
    if (window == NULL) {
        printf("Failed to create window: %s\n", SDL_GetError());
        return 1;
    }

    // Create a renderer
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (renderer == NULL) {
        printf("Failed to create renderer: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Texture *tok_kiraly_texture = create_card_texture(renderer, __tok_kiraly_ppm, __tok_kiraly_ppm_len);
    if (!tok_kiraly_texture) {
	printf("Failed to create texture: %s\n", SDL_GetError());
	return 1;
    }

    // Clear the screen
    SDL_RenderClear(renderer);

    SDL_Rect tok_kiraly_rect;
    FILL_CARD_RECT(tok_kiraly_rect, CARD_WIDTH * 4, 0);

    SDL_RenderCopy(renderer, tok_kiraly_texture, NULL, &tok_kiraly_rect);

    SDL_RenderPresent(renderer);

    SDL_Event event;
    for (;;) {
        if (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                break;
            }
        }
    }

    SDL_DestroyTexture(tok_kiraly_texture);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}
