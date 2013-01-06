from flask import Flask,render_template
from flask_debugtoolbar import DebugToolbarExtension
from mongoengine import *

class Element(Document):
    """Elements are parents of TextElements, ContainerElements, etc."""
    meta = { "allow_inheritance": True }
    v_id = StringField(required=True)
    #v_type = StringField()
    v_timestamp = DateTimeField(required=True)
    #v_see = ListField(StringField())
    #v_depends_on = ListField(StringField())
    #v_prerequisite_for = ListField(StringField())

    def getRawText(context=""):
        """Retrieve recursively computed resulting text, as seen from
the given context. This raw text can be fed through a formatter to
achieve HTML, Latex, etc. output."""
        pass

    pass

class TextElement(Element):
    v_content = StringField()
    pass

class CollectionElement(Element):
    """References an ordered list of elements, these elements
    are the 'content' of the CollectionElement."""
    v_contained_ids = ListField(StringField())

if __name__ == "__main__":
    # run unit tests
    pass


    
