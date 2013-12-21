from datetime import *
import re
import markdown

class Element:
    """Elements are parents of TextElements, ContainerElements, etc."""
    #v_type = StringField()
    #v_timestamp = DateTimeField(required=True)
    #v_see = ListField(StringField())
    #v_depends_on = ListField(StringField())
    #v_prerequisite_for = ListField(StringField())

    def __init__(self,vars):
        self.vars = vars

    def getRawText(context=""):
        """
        Retrieve recursively computed resulting text, as seen from
        the given context. This raw text can be fed through a formatter to
        achieve HTML, Latex, etc. output.
        """
        pass

    def getID(self):
        return self.vars['v_id']

    def setID(self,id):
        self.vars['v_id'] = id

    def setTS(self,ts):
        self.vars['v_ts'] = ts

    def getHTML(self,dbcollection=None):
        """
        Convenience method for initial implementation: return
        contents in approximated HTML
        """
        return "Element-Base-Class"

    def getTSStr(self):
        """2013-01-23T17:27:31.265"""
        s = "%s.%03d"%(self.vars['v_ts'].strftime("%Y-%m-%dT%H:%M:%S"),
                       self.vars['v_ts'].microsecond/1000)
        return s

    def save(self,collection):
        """
        Save this element to the given database.
        In detail, this will atomically:
        1) check if the version currently held in the DB equals the current timestamp.
        2) if so, update timestamp to current time
        3) store new revision as new object in database
        """
        r = collection.insert(self.vars)
        print r


    @staticmethod
    def doesIDExist(collection,id):
        """
        Does or did an element with the given ID exist in the given 
        database?
        """
        if collection.find({'v_id':id}).count() > 0:
            print "ID %s exists." % id
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
        del e['_id']   # a new mongo ID will get assigned automatically on save()
        if e['v_class'] == 'TextElement':
            return TextElement(e)
        if e['v_class'] == 'CollectionElement':
            return CollectionElement(e)
        if e['v_class'] == 'QueryElement':
            return QueryElement(e)
        return CollectionElement()


class TextElement(Element):

    def __init__(self,vars):
        Element.__init__(self,vars)
        self.vars['v_class'] = 'TextElement'

    def getHTML(self,dbcollection=None):
        return markdown.markdown(self.vars['v_content'])

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
        r = c.findall(self.vars['v_content'])
        implicit_vars = {}
        for v in r:
            print v[0],v[1],implicit_vars
            implicit_vars[v[0]] = v[1]
        self.vars.update(implicit_vars)
        # http://stackoverflow.com/questions/38987/how-can-i-merge-union-two-python-dictionaries-in-a-single-expression


class CollectionElement(Element):
    """References an ordered list of elements, these elements
    are the 'content' of the CollectionElement."""

    def __init__(self,vars):
        Element.__init__(self,vars)
        self.vars['v_class'] = 'CollectionElement'

    def getHTML(self,dbcollection=None):
        return "CollectionElement"

class QueryElement(Element):
    """A database query. Displayed as a list or table containing the results."""

    def __init__(self,vars):
        Element.__init__(self,vars)
        self.vars['v_class'] = 'QueryElement'

    def getHTML(self,dbcollection=None):
        # execute query
        #
        # For now, try a hard-coded example: Find all elements with ID
        # "TICKET*.*" (latest revision, not deleted).  No nested
        # queries in MongoDB! Therefore we need to do this in multiple
        # steps. Lots of potential for optimisation! One potential
        # option might be to use the divide and conquer (aka
        # map-reduce) facility. And we still haven't totally given up
        # on a more traditional SQL backend yet. This might just be a
        # better fit for our data model. For the current prototype,
        # the choice of backend doesn't matter much, though.
        
        # Step 1: retrieve all matching element IDs
        r = dbcollection.find({'v_id':{"$regex":'^TICKET1[.]\d+'}}).distinct('v_id')

        # Step 2: for each ID, retrieve latest version (considering
        # query time)
        obj_ids = []
        for v_id in r:
            e = dbcollection.find_one({'v_id':v_id},sort=[{'v_ts',-1}])
            # omit if deleted
            if not e:
                raise "Should have returned a valid result."
            if not e.has_key('v_deleted') or not e.v_deleted:
                obj_ids.append(e)

        # Step 3: if that version hasn't been deleted (note: already
        #         taken care of by previous step), perform further
        #         filtering according to query. Add to result set if
        #         item makes it through all filters.

        # not doing this for the time being @todo

        # build result, present as table
        
        columns = [ 'v_id', 'v_class','responsible' ]
        s = "<table><tr>"
        for c in columns:
            s += "<th>"+c+"</th>"
        s += "</tr>"
        for o in obj_ids:
            s += "<tr>"
            for c in columns:
                s += '<td valign="top">'
                if o.has_key(c):
                    if c=="v_id":
                        s+="<a href='/show/"+o[c]+"'>"
                    s += o[c]
                    if c=="v_id":
                        s+="</a>"
                s += "</td>"
            s += "</tr>"
        s += "</table>"
        
        return "QueryElement: <br />"+s

if __name__ == "__main__":
    # run unit tests
    pass
