import os
import sys
sys.path.insert(0, os.path.abspath('.'))

project = 'NutriSafe'
author = 'Riume Carlos'
release = '0.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []



locale_dirs = ['locale/']  
gettext_compact = False   

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
}

