CC=g++
SRCS=student02.c utility/utility.c
OBJS=$(SRCS:%.c=%.o)
TARGET=testmake2

.SUFFIXES : .c .o 

$(TARGET): $(OBJS)
	$(CC) -o $(TARGET) $(OBJS)
 
utility.o : utility/utility.c utility/utility.h
student02.o : student02.c utility/utility.h

