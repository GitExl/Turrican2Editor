CFLAGS= -O3 -c -std=c99 -Werror -Wpedantic -Wall -Wextra -mtune=generic -msse2
LIBS= -lpng -lz -lgdi32

all:

	mkdir -p obj

	gcc $(CFLAGS) -o obj/font.o src/font.c
	gcc $(CFLAGS) -o obj/render.o src/render.c
	gcc $(CFLAGS) -o obj/surface.o src/surface.c
	gcc $(CFLAGS) -o obj/utils.o src/utils.c
	gcc $(CFLAGS) -o obj/bitplane.o src/bitplane.c
	gcc $(CFLAGS) -o obj/streamread.o src/streamread.c
	gcc $(CFLAGS) -o obj/streamwrite.o src/streamwrite.c
	gcc $(CFLAGS) -o obj/png.o src/png.c
	gcc $(CFLAGS) -o obj/presenter.o src/presenter.c
	gcc $(CFLAGS) -o obj/palette.o src/palette.c

	gcc -shared -static-libgcc -o renderlib.dll obj/*.o $(LIBS)
	strip renderlib.dll

	mv renderlib.dll ../renderlib.dll


clean:

	rm -rf obj
	rm -f renderlib.a
