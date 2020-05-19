#------------------------------------------------------------------------------
# Function for making text appear in bold sky blue
message = @echo "\033[1;38;5:123m$1\033[0m"

.PHONY: default
default: test

#------------------------------------------------------------------------------
# virtualenv

python_version := 3.8
venv_dir := .config/py38

venv_cmd = . ${venv_dir}/bin/activate && $1

${venv_dir}:
	$(call message,"Creating virtualenv for dev work...")
	virtualenv -p ${python_version} ${venv_dir}

.config/venv_installed: dev_requirements.txt ${venv_dir} setup.py
	$(call message,"Upgrading pip $<")
	$(call venv_cmd, pip install --upgrade pip)

	$(call message,"Installing $<")
	$(call venv_cmd, pip install -r $<)

	$(call message,"Installing package in --editable mode")
	$(call venv_cmd, pip install --editable .)

	mkdir -p ${@D}
	touch $@

activate_aiocells: .config/venv_installed
	$(call message,"Generating $@ script")
	scripts/generate_activate_aiocells.sh

.PHONY: venv
venv: activate_aiocells

.PHONY: nuke
nuke:
	-rm -rf .config
	-rm -f activate_aiocells

.PHONY: test
test: | venv
	$(call message,"Running tests...")
	$(call venv_cmd, scripts/test.sh)
