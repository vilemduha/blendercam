# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../cam/"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Fabex"
copyright = "2024"
author = "Vilem Novak, Alain Pelletier & Contributors"
release = "1.0.38"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
    "myst_parser",
]

autoapi_type = "python"
autoapi_dirs = ["../cam"]
autoapi_ignore = [
    "*post_processors*",
    "*presets*",
    "*ui*",
    "*tests*",
    "*wheels*",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "*post_processors*",
    "*presets*",
    "*ui*",
    "*tests*",
    "*wheels*",
]

add_module_names = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_logo = "_static/Fabex_logo_square.png"
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/pppalain/blendercam",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "Matrix",
            "url": "https://riot.im/app/#/room/#blendercam:matrix.org",
            "icon": "fa-solid fa-comments",
            "type": "fontawesome",
        },
    ]
}
