#------------------------------------------------------------------------------
# Function for making text appear in bold sky blue
message = @echo "\033[1;38;5:123m$1\033[0m"

.PHONY: default
default: test

#------------------------------------------------------------------------------
# virtualenv

python_version := 3.8
venv_dir := .tools/py38

venv_cmd = . ${venv_dir}/bin/activate && $1

${venv_dir}:
	$(call message,"Creating virtualenv for dev work...")
	virtualenv -p ${python_version} ${venv_dir}

.tools/venv_installed: dev_requirements.txt ${venv_dir} setup.py
	$(call message,"Upgrading packaging tools $<")
	$(call venv_cmd, pip install --upgrade pip setuptools wheel)

	$(call message,"Installing $<")
	$(call venv_cmd, pip install -r $<)

	$(call message,"Installing package in --editable mode")
	$(call venv_cmd, pip install --editable .)

	mkdir -p ${@D}
	touch $@

activate_aiocells: .tools/venv_installed
	$(call message,"Generating $@ script")
	scripts/generate_activate_aiocells.sh ${venv_dir}

.PHONY: venv
venv: activate_aiocells

.PHONY: nuke
nuke:
	-rm -rf .tools build dist .tox .pytest_cache
	-rm -f activate_aiocells

.PHONY: test
test: | venv
	$(call message,"Running tests...")
	$(call venv_cmd, scripts/test.sh)

#------------------------------------------------------------------------------
# distribution

dist_dir := .config/dist

.PHONY: dist
dist: #tox
	$(call message,"Building distributions...")
	$(call venv_cmd, python setup.py sdist bdist_wheel)

#------------------------------------------------------------------------------
# tox

tox_initialised := .tools/tox_initialised

.PHONY: tox
tox: ${tox_initialised} | venv
	$(call message,"Running tox...")
	$(call venv_cmd, tox)

# If tox.ini has changed, we want to rebuild tox. The file .tox-r exists only
# to record the time of the last invocation of "tox -r". If "tox.ini" is newer
# than ".tox-r", or ".tox-r" doesn't exist, we rebuild.
${tox_initialised}: tox.ini | venv
	$(call message,"Building tox environment...")
	$(call venv_cmd, tox -r --notest)
	touch $@
