# vim: set filetype=python tw=100 cc=+1:
# https://setuptools.readthedocs.io/en/latest/pkg_resources.html#id5
"""
This is a namespace package: https://www.python.org/dev/peps/pep-0420/#namespace-packages-today
"""

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
