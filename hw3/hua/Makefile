.PHONY: all clean

DIR=cv
FOLD_T=5
RM_T=1
TARGET=cv

all: clean $(TARGET) 

cv:
	../md2016/hw3/script/cross_validation.sh test3 $(DIR) $(RM_T) run

clean:
	rm -rf cv
