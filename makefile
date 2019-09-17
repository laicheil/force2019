SHELL=bash
current_makefile:=$(lastword $(MAKEFILE_LIST))
current_makefile_dirname:=$(dir $(current_makefile))
current_makefile_dirname_abspath:=$(dir $(abspath $(current_makefile)))
current_makefile_dirname_realpath:=$(dir $(realpath $(current_makefile)))

python_cmd=python3
python_args=
python=$(python_cmd) $(python_args)
pip_cmd=$(python) -m pip
pip_args=
pip=$(pip_cmd) $(pip_args)
pip_install_cmd=$(pip) install
pip_install_args=
pip_install=$(pip_install_cmd) $(pip_install_args)
pylint_cmd=$(python) -m pylint
pylint_args=
pylint=$(pylint_cmd) $(pylint_args)
pytest_cmd=$(python) -m pytest
pytest_args=
pytest=$(pytest_cmd) $(pytest_args)
virtualenv_cmd=$(python) -m virtualenv
virtualenv_args=
virtualenv=$(virtualenv_cmd) $(virtualenv_args)
twine_cmd=$(python) -m twine
twine_args=
twine=$(twine_cmd) $(twine_args)
twine_upload_cmd=$(twine) upload
twine_upload_args=$${PYPIRC_PATH:+--config-file=$${PYPIRC_PATH}} --skip-existing
twine_upload=$(twine_upload_cmd) $(twine_upload_args)
python_setup_py_cmd=$(python) setup.py
python_setup_py_args=
python_setup_py=$(python_setup_py_cmd) $(python_setup_py_args)
python_setup_py_test_cmd=$(python_setup_py) test
python_setup_py_test_args=
python_setup_py_test=$(python_setup_py_test_cmd) $(python_setup_py_test_args)

package_extras=

all:

lvenv_dir=$(HOME)/.local/venvs/
lvenv_name:=$(shell git remote get-url origin | sha1sum | cut -c 1-10)
lvenv_path=$(HOME)/.local/venvs/$(lvenv_name)

.PHONY: lvenv
lvenv:
	mkdir -p "$(lvenv_dir)"
	$(org_python) -m virtualenv --no-site-packages --python=$$(which python3) $(lvenv_path)
	$(pip_install) --upgrade wheel twine pylint pytest

ifeq ($(WITH_LVENV),yes)
lvenv_target=lvenv
lvenv_prefix=PATH=$(lvenv_path)/bin$${PATH:+:$${PATH}}
org_python:=$(python)
python=$(lvenv_path)/bin/$(python_cmd) $(python_args)
$(info org_python=$(org_python))
$(info python=$(python))

include /dev/null
.PHONY: /dev/null
/dev/null: lvenv
else
org_python:=$(python)
endif

pypkg_name:=$(shell $(org_python) setup.py --name)
pypkg_version:=$(shell $(org_python) setup.py --version 2>/dev/null)

$(info pypkg_version=$(pypkg_version))
$(info pypkg_name=$(pypkg_name))

.PHONY: winstall
winstall:
	$(pip_install) --user --upgrade $(shell $(python_setup_py) --name)$(package_extras)

.PHONY: install
install:
	$(pip_install) --user --upgrade .$(package_extras)

.PHONY: einstall
einstall:
	$(pip_install) --user --upgrade --editable .$(package_extras)

.PHONY: xinstall
xinstall:
	$(pip_install) $(xinstall_args)

.PHONY: uninstall
uninstall:
	$(pip) uninstall --yes $(shell $(python_setup_py) --name)

.PHONY: setup-test
setup-test:
	$(python_setup_py_test)

.PHONY: pytest
pytest:
	$(pytest)

.PHONY: pytest-log
pytest-log:
	$(pytest) --log-cli-level=DEBUG

.PHONY: test
test: pytest

.PHONY: lint
lint:
	find . \( -name build -o -name .eggs -o -name '*.egg-info' -o -name docs -o -name generated -o -name venv -o -name trash \) -prune -o -name '*.py' -type f -print0 | xargs -t -0 $(pylint)

.PHONY: validate
validate: test lint

.PHONY: clean
clean: venv-clean
	$(python_setup_py) clean
	rm -vrf build/
	rm -vrf docker/build/
	rm -vrf dist/

.PHONY: distclean
distclean: clean
	find . -name '__pycache__' | xargs --no-run-if-empty -t rm -r
	find . -name '*.pyc' | xargs --no-run-if-empty -t rm
	find . \( -name '*.egg-info' -o -name '*.dist-info' \) | xargs --no-run-if-empty -t rm -r
	find . \( -name '.eggs' -o -name '.pytest_cache' \) | xargs --no-run-if-empty -t rm -r

.PHONY: venv
venv:
	$(virtualenv) --no-site-packages ./venv/
	./venv/bin/pip install --upgrade --editable .

.PHONY: venv-clean
venv-clean:
	rm -rf venv

.PHONY: wheel
wheel:
	$(python_setup_py) clean --all
	rm -rf dist/ *.egg-info
	$(python_setup_py) bdist_wheel
	$(twine) check dist/*

.PHONY: wheel-upload
wheel-upload: wheel
	$(twine_upload) dist/*

.PHONY: versioneer
versioneer:
	$(python) versioneer.py setup
	sed -i '/^[^*].*_version.py/d' .gitattributes
	sed -i '/^include .*_version.py/d' MANIFEST.in
	git add .gitattributes MANIFEST.in

.PHONY: mark
mark:
	date > mark
	git add mark
	git commit -m "change mark" mark
	git push
