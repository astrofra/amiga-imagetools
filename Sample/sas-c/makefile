.prl.gst:
	sc NOLINK CODE=F DATA=F OPTI MGST $*.gst $*.prl

.c.o:
	sc NOLINK CODE=F DATA=F OPTI TO $@ $*.c

OBJ = openwin.o

openwin: $(OBJ)
	sc LINK CODE=F DATA=F OBJ $(OBJ) TO openwin.exe

openwin.o: openwin.c test.h