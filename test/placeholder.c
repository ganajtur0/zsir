#include <stdio.h>
#include <stdlib.h>

void
bruh(int *a){
	*a = 69;
}

int
main(void) {
	bruh(NULL);
	return 0;	
}
