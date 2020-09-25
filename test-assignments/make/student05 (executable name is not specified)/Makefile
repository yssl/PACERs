testmake1 : student01.o utility.o
	gcc student01.o utility.o

utility.o : utility.c utility.h
	gcc -c -o utility.o utility.c

student01.o : student01.c utility.h
	gcc -c -o student01.o student01.c


