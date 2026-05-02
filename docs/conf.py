# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys

project = "Blu"
copyright = "2024, John Larson"
author = "John Larson"
release = "0.0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]


### Manually Added ###

sys.path.append("../src")

copybutton_exclude = ".linenos, .gp"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

html_css_files = ["styles.css"]

todo_include_todos = True

autosectionlabel_prefix_document = True

# autodoc

autoclass_content = "both"

autodoc_default_options = {
    "members": True,
    "imported-members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
