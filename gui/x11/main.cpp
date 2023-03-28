#include <assert.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#include <X11/Xlib.h>
#include <X11/keysymdef.h>

#define STB_IMAGE_IMPLEMENTATION
#define STB_ONLY_PNM
#include "stb_image.h"

#include "kartyak/makk_also.h"


int main(void) {

	static Atom wm_delete_window;
	Display *display = XOpenDisplay(NULL);
	assert(display);


	int screen = DefaultScreen(display);

	unsigned long white = WhitePixel(display, screen);
	unsigned long black = BlackPixel(display, screen);

	Window win = XCreateSimpleWindow(display,
				       XDefaultRootWindow(display),
				       0, 0,
				       800, 600,
				       0,
				       white,
				       black);


	// betöltjük a képet
	int x, y, chan;
	unsigned char *makk_also = stbi_load_from_memory(makk_also_ppm,
							 makk_also_ppm_len,
							 &x, &y, &chan, 0);
	assert(makk_also);

	XWindowAttributes wa;
	XGetWindowAttributes(display, win, &wa);

	int aligned_bytes_per_line = ((x * 3 + 7) / 8) * 8;
	XImage *image = XCreateImage(display, wa.visual, wa.depth, ZPixmap, 0, (char *) makk_also, x, y, 8, 0);
	assert(image);

	GC gc = XCreateGC(display, win, 0, NULL);

	wm_delete_window = XInternAtom(display, "WM_DELETE_WINDOW", False);
	XSetWMProtocols(display, win, &wm_delete_window, 1);

	XSelectInput(display, win, ExposureMask|KeyPressMask);

	XMapWindow(display, win);

	XEvent ev;
	
	bool quit = false;
	while (!quit) {
	while (XPending(display) > 0) {
		XNextEvent(display, &ev);
		switch (ev.type){

		case Expose:
			XPutImage(display, win, gc, image, 0, 0, 0, 0, x, y);
			XFlush(display);
			break;
		case KeyPress:
			switch (XLookupKeysym(&ev.xkey, 0)){
		
			case 'q':
				printf("Keypress event \'q\' received: exiting...\n");
				quit = true;
				break;

			default:
				break;

			} break;

		case ClientMessage:
			if ( (Atom) ev.xclient.data.l[0] == wm_delete_window ){
				printf("WM event received: exiting...\n");
				quit = true;
				break;
			}
			break;

		default:
			break;

		}
	}
	}

	stbi_image_free(makk_also);
	XCloseDisplay(display);
	return 0;
}
