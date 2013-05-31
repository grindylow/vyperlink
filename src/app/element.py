from datetime import *
import re

class Element:
    """Elements are parents of TextElements, ContainerElements, etc."""
    #v_type = StringField()
    #v_timestamp = DateTimeField(required=True)
    #v_see = ListField(StringField())
    #v_depends_on = ListField(StringField())
    #v_prerequisite_for = ListField(StringField())

    def __init__(self,v_id="ELE.001",v_ts=None):
        self.v_ts = v_ts
        self.v_id = v_id

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
        s = "%s.%03d"%(self.v_ts.strftime("%Y-%m-%dT%H:%M:%S"),
                       self.v_ts.microsecond/1000)
        return s

    def save(self,mongoclient):
        """
        Save this element to the given database.
        In detail, this will atomically:
        1) check if the version currently held in the DB equals the current timestamp.
        2) if so, update timestamp to current time
        3) store new revision as new object in database
        """
        pass

    @staticmethod
    def doesIDExist(collection,id):
        """
        Does or did an element with the given ID exist in the given 
        database?
        """
        if collection.find({'v_id':id}).count() > 0:
            return True
        return False

    @staticmethod
    def retrieveFromDB(collection,id):
        """Retrieve the latest revision of the element with the given ID
        from the database."""
        r = collection.find({'v_id':id}).sort("v_ts",-1)
        if not r.count():
            raise BaseException("no element with id %s found" % id)
        e = r[0]
        print e
        if e['v_class'] == 'TextElement':
            return TextElement(v_id=e['v_id'],
                               v_content=e['v_content'],
                               v_ts=e['v_ts'])
        if e['v_class'] == 'CollectionElement':
            return CollectionElement(v_id=e['v_id'],
                                     v_contained_ids=e['v_contained_ids'],
                                     v_ts=e['v_ts'])
        return CollectionElement()


class TextElement(Element):

    def __init__(self,v_id="TEXT.001",v_content="initial content",v_ts=None):
        Element.__init__(self,v_ts=v_ts)
        self.v_id = v_id
        self.v_content = v_content
        self.v_implicit_vars = {}

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

    def save(self,collection):
        """Save to database"""
        r = collection.insert({'v_class':'TextElement','v_id':self.v_id,
                               'v_content':self.v_content,'v_ts':self.v_ts})
        print r

class CollectionElement(Element):
    """References an ordered list of elements, these elements
    are the 'content' of the CollectionElement."""

    def __init__(self,v_id="CONTAINER.001",v_contained_ids=[],v_ts=None):
        Element.__init__(self,v_id=v_id,v_ts=v_ts)
        self.v_contained_ids = v_contained_ids

    def getHTML(self):
        return "CollectionElement"

    def save(self,collection):
        """Save to database"""
        r = collection.insert({'v_class':'CollectionElement','v_id':self.v_id,
                               'v_contained_ids':self.v_contained_ids,'v_ts':self.v_ts})
        print r

if __name__ == "__main__":
    # run unit tests
    pass


    
