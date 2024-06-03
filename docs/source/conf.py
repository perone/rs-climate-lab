# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys, os

sys.path.insert(0, os.path.abspath('../../'))

project = 'RS Climate Lab'
copyright = '2024, Christian S. Perone'
author = 'Christian S. Perone'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
pygments_style = "dracula"
html_theme = 'furo'
html_static_path = ['_static']
html_logo = "_static/climate-lab-logo.png"
html_theme_options = {
    "light_css_variables": {
        "color-sidebar-background": "#ffffff",
    },
    "source_repository": "https://github.com/perone/rs-climate-lab/",
    "source_branch": "main",
    "source_directory": "docs/",
}
html_title = "<nbsp></nbsp>"

html_show_sourcelink = False