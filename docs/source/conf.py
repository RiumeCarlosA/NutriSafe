# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'NutriSafe'
copyright = '2024, Riume'
author = 'Riume'

release = '0.1'
version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

source_suffix = ['.rst', '.md']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
