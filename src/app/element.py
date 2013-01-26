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

    def getHTML(self):
        """Convenience method for initial implementation: return
        contents in approximated HTML"""
        return "Element-Base-Class"

    pass

class TextElement(Element):
    v_content = StringField()

    def getHTML(self):
        return self.v_content

    pass

class CollectionElement(Element):
    """References an ordered list of elements, these elements
    are the 'content' of the CollectionElement."""
    v_contained_ids = ListField(StringField())

    def getHTML(self):
        return "CollectionElement"

if __name__ == "__main__":
    # run unit tests
    pass


    
