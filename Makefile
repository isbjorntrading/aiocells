#------------------------------------------------------------------------------
# Function for making text appear in bold sky blue
message = @echo "\033[1;38;5:123m$1\033[0m"

default: | venv

.venv_initialised:
	scripts/init_venv

.PHONY: venv
venv: .venv_initialised

.PHONY: nuke
nuke:
	-rm -f .venv_initialised
