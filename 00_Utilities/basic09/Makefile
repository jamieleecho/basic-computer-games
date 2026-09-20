# Convert every BASIC program in this repository to BASIC09.
#
#   make -C 00_Utilities/basic09            # convert, and write each README
#   make -C 00_Utilities/basic09 check      # also load and run each one
#   make -C 00_Utilities/basic09 clean
#   make -C 00_Utilities/basic09 help
#
# Each program lands beside the other ports of the same game, in
# 00_Alternate_Languages/<NN>_<Game>/basic09/.
#
# The conversion is done by decb-to-b09 from coco-tools, which is a separate
# checkout; point COCO_TOOLS at it if it is not next to this one.

ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))/../..
ROOT := $(abspath $(ROOT))

COCO_TOOLS ?= $(abspath $(ROOT)/../coco-tools)
DECB_TO_B09 ?= uv run --project $(COCO_TOOLS) decb-to-b09
PYTHON ?= uv run --project $(COCO_TOOLS) python

HERE := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
ALT = $(ROOT)/00_Alternate_Languages

# Scratch space. Converting a program also records the flags it was built with,
# so the README for its folder can quote the exact command.
BUILD = $(HERE)/.build

# -l  drop line numbers nothing branches to
# -O  store integer-only variables as BASIC09 INTEGERs
# -t  plain terminal, not a CoCo screen
# --basic09-for-loops  use BASIC09's own FOR semantics
COMMON_FLAGS ?= -l -O -t --basic09-for-loops

# Sources that cannot be converted, and why.
#   awari, checkers            NEXT closes a FOR opened in another block, which
#                              BASIC09 has no way to express
#   checkers.annotated         a commented listing, not a BASIC program
#   king_variable_update       a variant using long variable names DECB rejects
#   splat                      the original branches to line 540, which does not exist
SKIP = awari checkers checkers.annotated king_variable_update splat

# Programs BASIC09 itself cannot manage, reported by the check but not counted
# against it.  superstartrek compiles to one procedure larger than BASIC09 can
# hold: past about 27.7KB of source, adding any line at all -- even a comment --
# makes "load" spin forever instead of returning.  It would have to be split
# across several procedures to run.
KNOWN = superstartrek
KNOWN_ARGS = $(foreach k,$(KNOWN),--known $(k))

# FOR X = 1 TO 100000 overflows the INTEGER that -O would otherwise pick.
FLAGS_distributions = --no-optimize X

# Squares a difference that can be negative; BASIC09's ^ rejects a negative base.
FLAGS_salvo = --exact-powers

# D$ holds a 39-character card table that MID$ indexes past column 32, and
# O1$ is a 51-character rule; the default 32 bytes per string truncates both.
FLAGS_blackjack = -s 40
FLAGS_superstartrek = -s 52

# DIM W(H,V),V(H,V) sizes the maze from the width and length that are typed in.
FLAGS_amazing = --fix-array-size 'W(20,20)' --fix-array-size 'V(20,20)'

# DIM Q(P9),A$(P9),G$(P9),I(P),H$(P9) sizes from the positions and colors that
# are typed in; I(P) holds C9^P9 entries, so 4096 allows 8 colors in 4 positions.
# Single quotes keep the shell from reading A$(10) as a command substitution.
FLAGS_mastermind = --fix-array-size 'Q(10)' --fix-array-size 'A$$(10)' \
                   --fix-array-size 'G$$(10)' --fix-array-size 'I(4096)' \
                   --fix-array-size 'H$$(10)'

# OS-9 file names cannot contain '-', and '.' separates the extension.
b09name = $(subst .,_,$(subst -,_,$(basename $(notdir $(1)))))
gamedir = $(notdir $(patsubst %/,%,$(dir $(1))))

ALL_BAS = $(wildcard $(ROOT)/*/*.bas)
BAS = $(foreach f,$(ALL_BAS),$(if $(filter $(basename $(notdir $(f))),$(SKIP)),,$(f)))
B09 = $(foreach f,$(BAS),$(ALT)/$(call gamedir,$(f))/basic09/$(call b09name,$(f)).b09)
GAMES = $(sort $(foreach f,$(BAS),$(call gamedir,$(f))))
READMES = $(foreach g,$(GAMES),$(ALT)/$(g)/basic09/README.md)

.PHONY: all check check-load clean list-skipped help

## Convert every program, and write each folder's README
all: $(B09) $(READMES)

## Convert, then load and run each program under os9emu's BASIC09
check: all
	$(PYTHON) $(HERE)/check.py $(KNOWN_ARGS) $(ALT)

## Convert, then only load each program (a syntax check, no run)
check-load: all
	$(PYTHON) $(HERE)/check.py --load-only $(KNOWN_ARGS) $(ALT)

## Remove every generated basic09 folder
clean:
	rm -rf $(ALT)/*/basic09 $(BUILD)

## Show the sources that are deliberately not converted
list-skipped:
	@for s in $(SKIP); do echo "$$s"; done

## Show this help
help:
	@grep -B1 -E '^[a-zA-Z_-]+:' $(MAKEFILE_LIST) | grep -E '^##|^[a-zA-Z_-]+:' \
	  | sed 'N;s/\n/ /' | sed 's/## \(.*\) \([a-zA-Z_-]*\):.*/\2\t\1/' | sort \
	  | awk -F'\t' '{ printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2 }'

# One rule per program, so each output knows which source it came from and
# which FLAGS_<name> override applies to it.  The recipe also records the flags,
# one per line: passing them to printf as separate words is the only way to get
# them into a file with their quoting intact.
define CONVERT_RULE
$(ALT)/$(3)/basic09/$(2).b09: $(1) $$(MAKEFILE_LIST)
	@mkdir -p $$(@D) $$(BUILD)
	@echo "converting $(3)/$(2)"
	@$$(DECB_TO_B09) $$(COMMON_FLAGS) $$(FLAGS_$(2)) $$< $$@
	@printf '%s\n' '$(notdir $(1))' $$(COMMON_FLAGS) $$(FLAGS_$(2)) > $$(BUILD)/$(3)__$(2).rec
endef

$(foreach f,$(BAS),$(eval $(call CONVERT_RULE,$(f),$(call b09name,$(f)),$(call gamedir,$(f)))))

# One README per folder, listing every program the folder holds.
define README_RULE
$(ALT)/$(1)/basic09/README.md: $(2) $$(MAKEFILE_LIST) $$(HERE)/write_readme.py
	@$$(PYTHON) $$(HERE)/write_readme.py --game $(1) --records $$(BUILD) --out $$@
endef

$(foreach g,$(GAMES),$(eval $(call README_RULE,$(g),$(filter $(ALT)/$(g)/basic09/%,$(B09)))))
