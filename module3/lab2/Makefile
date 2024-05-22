.PHONY: bison
bison:
	bison -d parser.y -Wcounterexamples

.PHONY: flex
flex:
	flex lexer.l

.PHONY: compile
compile:
	gcc -o scanner *.c

.PHONY: all
all: flex bison compile

.PHONY: run
run:
	./scanner input.txt