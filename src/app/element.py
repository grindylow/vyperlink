from flask import Flask,render_template
from flask_debugtoolbar import DebugToolbarExtension
from mongoengine import *
import re

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

    def getID(self):
        return self.v_id

    def getHTML(self):
        """Convenience method for initial implementation: return
        contents in approximated HTML"""
        return "Element-Base-Class"

    def getTSStr(self):
        """2013-01-23T17:27:31.265"""
        s = "%s.%03d"%(self.v_timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                       self.v_timestamp.microsecond/1000)
        return s

    pass

class TextElement(Element):
    v_content = StringField()
    v_implicit_vars = DictField()

    def getHTML(self):
        return self.v_content

    def extractVariables(self):
        """Extract variable definitions from my rawtext. Store these variables
        (and their contents) as fields in the element/database."""
        # for now, all raw text that matches the following pattern is
        # recognised as a variable definition:
        # <ws> = whitespace
        # [<ws>]<variable-name-without-whitespace>:[ws]contents<line-break>
        #
        # Future: We may want to allow for multi-line contents. For example
        # using "::" instead of ":". Or by using some heuristic or other.
        e = r"^\s*(\S+):\s*(.*)$"
        c = re.compile(e,re.MULTILINE)
        # this will catch all variables in one go and return a list of
        # name-value pairs
        r = c.findall(self.v_content)
        self.v_implicit_vars = {}
        for v in r:
            print v[0],v[1],self.v_implicit_vars
            self.v_implicit_vars[v[0]] = v[1]

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


    
