import glob
import os
import sys

man_pages = []
project = "tem manual"
extensions = ["sphinx.ext.todo"]
default_role = "dfn"  # We use this because it renders as italic (underlined)

# Provides the function get_description to load descriptions for man pages
sys.path.insert(0, os.path.dirname(__file__))
from man_descriptions import *

try:
    rst_prolog
except NameError:
    rst_prolog = ""
rst_prolog = generate_description_substitutions(rst_prolog)

for f in glob.glob("tem*.rst"):
    man_pages.append(
        (
            f[:-4],  # source file (extension .rst removed)
            f[:-4],  # output file (under output dir)
            man_descriptions[f[:-4]],  # description
            "Haris Gušić <harisgusic.dev@gmail.com>",  # author
            1,  # section
        )
    )
