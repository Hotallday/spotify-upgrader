# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_rtd_theme

sys.path.append(os.path.abspath('../../'))


# -- Project information -----------------------------------------------------

project = u'Spotify Member API'
copyright = u'2018, General Software Inc.'
author = u'General Software Inc'

# If you set today to some non-false value, then it is used:
today = ''

# highlight_language: The default language to highlight source code in.
# highlight_language = 'python'
# pygments_style: The style name to use for Pygments highlighting
# of source code.
pygments_style = 'sphinx'
#add_function_parentheses: If true, ‘()’ will be appended to
# :func: etc. cross-reference text.
add_function_parentheses = True

#add_module_names: If true, the current module name will be prepended to
#  all description unit titles (such as .. function::).
add_module_names = True

# show_authors: If true, sectionauthor and moduleauthor directives will be
#  shown in the output. They are ignored by default.
show_authors = False

# modindex_common_prefix: A list of ignored prefixes for module index sorting.
modindex_common_prefix = []

# The short X.Y version
version = u''
# The full version, including alpha/beta/rc tags
release = u'0.01'


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
]


# sphinx.ext.autodoc Options

# This value selects what content will be inserted into the main body of an
# autoclass directive. The possible values are:
#
# "class"
# Only the class’ docstring is inserted. This is the default. You can still
# document __init__ as a separate method using automethod or the members
# option to autoclass.
# "both"
# Both the class’ and the __init__ method’s docstring are concatenated
# and inserted.
# "init"
# Only the __init__ method’s docstring is inserted.
# Nuevo en la versión 0.3.
#
# If the class has no __init__ method or if the __init__ method’s docstring is
#  empty, but the class has a __new__ method’s docstring, it is used instead.
#
# Nuevo en la versión 1.4.
# http://www.sphinx-doc.org/es/stable/ext/autodoc.html#confval-autoclass_content
autoclass_content = "both"


# This value selects if automatically documented members are sorted
# alphabetical (value 'alphabetical'), by member type (value 'groupwise')
# or by source order (value 'bysource'). The default is alphabetical.
#
# Note that for source order, the module must be a Python module
# with the source code available.
#
# Nuevo en la versión 0.6.
#
# Distinto en la versión 1.0: Support for 'bysource'.
# http://www.sphinx-doc.org/es/stable/ext/autodoc.html#confval-autodoc_member_order
autodoc_member_order = "groupwise"

# This value is a list of autodoc directive flags that should be automatically
# applied to all autodoc directives. The supported flags are
# 'members', 'undoc-members', 'private-members', 'special-members',
# 'inherited-members' and 'show-inheritance'.
#
# If you set one of these flags in this config value, you can
# use a negated form, 'no-flag', in an autodoc directive, to disable it once.
# For example,
# if autodoc_default_flags is set to ['members', 'undoc-members'],
# and you write a directive like this:
# http://www.sphinx-doc.org/es/stable/ext/autodoc.html#confval-autodoc_default_flags
autodoc_default_flags = ['members',
                         'undoc-members',
                         # 'inherited-members',
                         # 'show - inheritance'
                         ]

# Functions imported from C modules cannot be introspected, and therefore
# the signature for such functions cannot be automatically determined.
# However, it is an often-used convention to put the signature into the
# first line of the function’s docstring.
#
# If this boolean value is set to True (which is the default), autodoc will
# look at the first line of the docstring for functions and methods, and
# if it looks like a signature, use the line as the signature and remove
# it from the docstring content.
# http://www.sphinx-doc.org/es/stable/ext/autodoc.html#confval-autodoc_docstring_signature
autodoc_docstring_signature = True


# This value contains a list of modules to be mocked up. This is useful
# when some external dependencies are not met at build time and break
# the building process.
# http://www.sphinx-doc.org/es/stable/ext/autodoc.html#confval-autodoc_mock_imports
autodoc_mock_imports = []


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']
html_theme_path = ["_themes", ]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'typekit_id': 'hiw1hhg',
    'canonical_url': False,
    'analytics_id': False,
    'collapse_navigation': False,
    'sticky_navigation': False,
    'navigation_depth': 4,
    #'includehidden': True,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
}

# html_style: The style sheet to use for HTML pages.
html_style = None

# html_title: The name for this set of Sphinx documents.If None, it defaults
# to < project > v < release > documentation.
# html_title = ''

# html_short_title: A shorter title for the navigation bar. Default is
# the same as html_title.
html_short_title = 'Spotify Member API'

# html_logo: The name of an image file (relative to this directory) to
#  place at the top of the sidebar.
# html_logo = None

# html_favicon: The name of an image file (within the static path) to use
#  as favicon of the docs. This file should be a Windows icon file (.ico)
# being 16x16 or 32x32 pixels large.
# html_favicon = None

# html_static_path: Add any paths that contain custom static files
# (such as style sheets) here, relative to this directory. They are copied
# after the builtin static files, so a file named default.css will overwrite
# the builtin default.css. CodeChat note:
# This must always include CodeChat.css. #html_static_path = ['CodeChat.css']

# html_last_updated_fmt: If not ‘’, a ‘Last updated on:’ timestamp is
# inserted at every page bottom, using the given strftime format.
# html_last_updated_fmt = '%b, %d, %Y'

# html_use_smartypants: If true, SmartyPants will be used to convert quotes
#  and dashes to typographically correct entities.
html_use_smartypants = True

# html_sidebars: Custom sidebar templates, maps document names to template
# names.
html_sidebars = {}

# html_additional_pages: Additional templates that should be rendered to pages,
# maps page names to template names.
#html_additional_pages = {}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'example_projectdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'example_project.tex', u'example\\_project Documentation',
     u'General Software Inc', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'example_project', u'example_project Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'example_project', u'example_project Documentation',
     author, 'example_project', 'One line description of project.',
     'Miscellaneous'),
]


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}
