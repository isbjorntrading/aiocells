#------------------------------------------------------------------------------
# Function for making text appear in bold sky blue
message = @echo "\033[1;38;5:123m$1\033[0m"

default: | venv

#------------------------------------------------------------------------------
# virtualenv

venv_cmd = . .venv/bin/activate && $1

.venv:
	$(call message,"Creating virtualenv for dev work...")
	virtualenv -p 3.7 .venv

.venv_installed: dev_requirements.txt .venv setup.py
	$(call message,"Upgrading pip $<")
	$(call venv_cmd, pip install --upgrade pip)

	$(call message,"Installing $<")
	$(call venv_cmd, pip install -r $<)

	$(call message,"Installing package in --editable mode")
	$(call venv_cmd, pip install --editable .)

	touch $@

activate_aiocells: .venv_installed
	$(call message,"Generating $@ script")
	scripts/generate_activate_aiocells

.PHONY: venv
venv: activate_aiocells

.PHONY: nuke
nuke:
	-rm -rf .venv
