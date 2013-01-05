from flask import Flask,render_template
from flask_debugtoolbar import DebugToolbarExtension

class Element:
    """Elements are parents of TextElements, ContainerElements, etc."""

    def getRawText(context=""):
        """Retrieve recursively computed resulting text, as seen from
the given context. This raw text can be fed through a formatter to
achieve HTML, Latex, etc. output."""
        pass

    pass

class TextElement(Element):
    

if __name__ == "__main__":
    # run unit tests
