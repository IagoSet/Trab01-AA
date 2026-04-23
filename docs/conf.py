import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'Assistente de Lances'
copyright = '2026, Grupo de Algen'
author = 'Grupo de Algen'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'pt_BR'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
