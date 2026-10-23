# Static recompilation of Chuck Rock: GAME (gen/), its loader ChuckProg
# (genprog/), each level's code (genlevel1-5/, unpacked by ../tools/unpack.py)
# and MusicModule 1.02 (genmus/), from SuperSpider's analyse and gen, and
# game.c, linked with libroger (the RISC OS runtime).
ROGER   ?= $(HOME)/stuff/libroger
CC      ?= gcc
CFLAGS  ?= -O2 -g -w -fno-strict-aliasing $(if $(TRACE),-DRECOMP_TRACE)
GEN     := $(wildcard gen/code*.c) gen/entries.c
GENPROG := $(wildcard genprog/code*.c) genprog/entries.c
GENMUS  := $(wildcard genmus/code*.c) genmus/entries.c
LEVELS  := 1 2 3 4 5
GENLEV  := $(foreach n,$(LEVELS),$(wildcard genlevel$(n)/code*.c) genlevel$(n)/entries.c)
OBJ     := $(GEN:.c=.o) $(GENPROG:.c=.o) $(GENMUS:.c=.o) $(GENLEV:.c=.o) game.o
LIBS    := $(shell pkg-config --libs sdl3) -ljpeg -lm -lpthread
INC     := -I$(ROGER)/include

chuckrock: $(OBJ) $(ROGER)/libroger.a
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(ROGER)/libroger.a $(LIBS)

$(ROGER)/libroger.a: FORCE
	$(MAKE) -C $(ROGER) libroger.a

%.o: %.c $(ROGER)/include/roger.h $(ROGER)/include/roger_cpu.h
	$(CC) $(CFLAGS) $(INC) -c -o $@ $<

# Code/data analysis: SuperSpider, into ../analysis/<name>.json, then
# superspider gen. Each image's ../analysis/<name>.roots adds entry points
# to the analysis: "make roots" merges the gap entries a --trace-gaps run
# logged (untranslated.log, or LOG=...) into them, so the next "make regen"
# translates them.
SS      ?= $(HOME)/stuff/superspider
SSBIN   := $(SS)/_build/default/bin/main.exe
AN      := ../analysis
APP     := ../game/!Chuck
GAME    := $(firstword $(wildcard $(APP)/GAME,*) $(APP)/GAME)
PROG    := $(firstword $(wildcard $(APP)/ChuckProg,*) $(APP)/ChuckProg)
MUSMOD  := $(firstword $(wildcard $(APP)/MUSMOD2,*) $(APP)/MUSMOD2)
LEVEL   := 25928-28c9c
LOG     ?= untranslated.log

# --roots for ../analysis/<name>.roots, if there is one
roots = $(if $(wildcard $(AN)/$(1).roots),--roots $(AN)/$(1).roots)

# $(call analyse,name,image,base[,--module])
define analyse
	$(SSBIN) analyse "$(2)" $(3) $(4) --full $(call roots,$(1)) -o $(AN)/$(1).json
endef

regen:
	cd $(SS) && dune build
	python3 -I ../tools/unpack.py
	mkdir -p $(AN)
	$(call analyse,game,$(GAME),8000)
	$(call analyse,chuckprog,$(PROG),8000)
	$(call analyse,musmod,$(MUSMOD),1800000,--module)
	for n in $(LEVELS); do \
	    $(SSBIN) analyse ../unpacked/level$$n 8000 --full $(call roots,game) --roots ../unpacked/level$$n.roots \
	        $$([ -f $(AN)/level$$n.roots ] && echo --roots $(AN)/level$$n.roots) -o $(AN)/level$$n.json || exit 1; done
	rm -rf gen genprog genmus genlevel*
	$(SSBIN) gen "$(GAME)" 8000 $(AN)/game.json --c gen --leaders=dispatch
	$(SSBIN) gen "$(PROG)" 8000 $(AN)/chuckprog.json --c genprog --leaders=dispatch \
	    --prefix=P --tabprefix=recompP --files=1 --covtag=P
	$(SSBIN) gen "$(MUSMOD)" 1800000 $(AN)/musmod.json --c genmus --leaders=dispatch \
	    --prefix=M --tabprefix=recompM --files=1 --covtag=M
	for n in $(LEVELS); do $(SSBIN) gen ../unpacked/level$$n 8000 $(AN)/level$$n.json --c genlevel$$n --range $(LEVEL) \
	    --leaders=dispatch --prefix=L$$n --tabprefix=recompL$$n --files=1 --covtag=$$n || exit 1; done

roots:
	python3 -I $(SS)/tools/gap_roots.py "$(GAME)" 8000 $(AN)/game.roots $(LOG)
	python3 -I $(SS)/tools/gap_roots.py "$(PROG)" 8000 $(AN)/chuckprog.roots $(LOG)
	python3 -I $(SS)/tools/gap_roots.py "$(MUSMOD)" 1800000 $(AN)/musmod.roots $(LOG)

# make level-roots N=<level> LOG=...: a run's gap entries in level N's code
# (the five levels' images share an address, so a log is one level's)
level-roots:
	python3 -I $(SS)/tools/gap_roots.py ../unpacked/code$(N) 25928 $(AN)/level$(N).roots $(LOG)

clean:
	rm -f gen/*.o genprog/*.o genmus/*.o genlevel*/*.o game.o chuckrock

.PHONY: FORCE regen roots level-roots clean
