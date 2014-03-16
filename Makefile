#CC=vc +aos68k
CC=vc +kick13
CFLAGS=-c99 -I$(NDK_INC)

all: openwin

clean:
	rm -f openwin

openwin: openwin.c
	$(CC) $(CFLAGS) openwin.c -lamiga -o openwin

