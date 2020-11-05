#------------------------------------------------------------------------------
# Function for making text appear in bold sky blue
message = @echo "\033[1;38;5:123m$1\033[0m"

.PHONY: default
default: test

#------------------------------------------------------------------------------
# virtualenv

python_version := 3.8
venv_dir := .tools/venv/aiocells

venv_cmd = . ${venv_dir}/bin/activate && $1

.tools/venv_initialised: dev_requirements.txt setup.py
	build_scripts/initialise_virtualenv ${python_version} ${venv_dir}
	touch $@

activate_aiocells: .tools/venv_initialised
	$(call message,"Generating $@ script")
	build_scripts/generate_activate_aiocells ${venv_dir}

.PHONY: venv
venv: activate_aiocells

.PHONY: nuke
nuke:
	-rm -rf .tools build dist .tox .pytest_cache
	-rm -f activate_aiocells

.PHONY: test
test: | venv
	$(call message,"Running tests...")
	$(call venv_cmd, build_scripts/run_tests)

#------------------------------------------------------------------------------
# distribution

dist_dir := .config/dist

.PHONY: dist
dist: tox
	-rm -rf dist build
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

#------------------------------------------------------------------------------
# pypi
.PHONY: upload
upload: dist | venv
	$(call venv_cmd, build_scripts/add_version_tag)
	$(call venv_cmd, twine upload dist/*)
