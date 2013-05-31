from flask import Flask,render_template,jsonify,request
from flask_debugtoolbar import DebugToolbarExtension
from pymongo import MongoClient
from element import *
from datetime import *

app = Flask(__name__)

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'pass'

toolbar = DebugToolbarExtension(app)

@app.route("/")
def hello():
    return render_template("home.html")

@app.route("/getrawforediting")
def getrawforediting():
    collection = openDB()
    id = request.args.get("id")
    r = Element.retrieveFromDB(collection,id)
    return jsonify(r=r.vars['v_content'])

@app.route("/putrawafterediting",methods=["POST"])
def putrawafterediting():
    # @todo Check that submitted revision is based on the latest
    #       revision currently in the database. If not -> conflict!
    # @todo Have any "explicit" variables been changed? If so,
    #       propagate those changes to my parent. (...and they to theirs
    #       etc etc...)
    collection = openDB()
    id = request.form["id"]
    rawtext = request.form["rawtext"]
    r = Element.retrieveFromDB(collection,id)
    r.vars['v_content'] = rawtext
    r.vars['v_ts'] = datetime.now()
    r.extractVariables()
    r.save(collection)
    return jsonify(r=rawtext)

@app.route("/insertbelow",methods=["POST"])
def insertbelow():
    return insertrelative(+1)

@app.route("/insertabove",methods=["POST"])
def insertabove():
    return insertrelative(0)

def insertrelative(offset):
    """
    Insert a new TextElement at current position +x.
    x = 1: below current element
    x = 0: at current element position (i.e. before current element)
    This draws together common functionality from insertabove and insertbelow.
    """
    id = request.form["id"]
    parentid = request.form["parentid"]
    collection = openDB()
    newid = inventNewId(collection,id,parentid)
    ts = datetime.now()
    #@todo potential race condition between inventNewId and actual save-to-database

    # create the new element
    el = TextElement( {'v_id':newid,'v_content':"newly created",'v_ts':ts} )
    el.save(collection)

    # update parent (=container)
    r = Element.retrieveFromDB(collection,parentid)
    if not isinstance(r,CollectionElement):
        raise BaseException( "parent is NOT a CollectionElement" )

    l = r.vars['v_contained_ids']
    index = l.index(id)
    l.insert(index+offset,newid)

    r.vars['v_ts'] = ts
    r.vars['v_contained_ids'] = l
    r.save(collection)

    return jsonify(id=newid,ts="11T22:22:22.222")

def inventNewId(collection,startingPoint,parentid=""):
    """Invent a new ID that looks similar to startingPoint. Ensure it
    is unique. If parent is given, use that as a stronger hint as to what
    children IDs should look like."""
    #@todo implement more sophisticated algorithms that 
    #   - run faster than linear time and/or
    #   - recognise numbering schemes such as hex, alphanumerical, etc.
    # (1) isolate last number
    # (2) increment until there is no element with such an ID in the entire database
    
    # for now, we simply add numbers to the parent ID
    i = 1
    suggestedId = ""
    while True:
        suggestedId = parentid + "." + str(i)
        # check if this id already exists in the database
        if not Element.doesIDExist(collection,suggestedId):
            break
        i = i + 1
    return suggestedId

def openDB():
    """
    Return a handle to the collection that holds our elements.
    """
    client = MongoClient('localhost',27017)
    db = client.UnitTestingDB
    collection = db.elements
    return collection

@app.route("/create/<id>")
def create(id=None):
    """Create a new CollectionElement with the given ID"""
    collection = openDB()
    ts = datetime.now()

    # (1) check ID doesn't exist already
    if Element.doesIDExist(collection,id):
        return 'Element "%s" exists already. <a href="/show/%s">Show!</a>' % (id,id)
    
    # (2) create a first contained (text) element
    newid = inventNewId(collection,"",id)
    el = TextElement( { 'v_id':newid,
                        'v_content':"Insert content here...",
                        'v_ts':ts} )
    el.save(collection)

    # (3) create a new collection element
    el = CollectionElement( { 'v_id':id,
                              'v_ts':ts,
                              'v_contained_ids':[newid] } )
    el.save(collection)

    return 'Element "%s" created. <a href="/show/%s">Show!</a>' % (id,id)

@app.route("/show/<id>")
def show(id=None):
    """Show the given document (as HTML)"""
    collection = openDB()

    # (1) retrieve contained elements (parent must be a ContainerElement)
    try:
        r = Element.retrieveFromDB(collection,id)
    except:
        return 'Element "%s" doesn\'t exist. <a href="/create/%s">Create!</a>' % (id,id)

    if not isinstance(r,CollectionElement):
        raise BaseException( "Is NOT Container" )

    print "We have a collection (container). Let's see..."

    # (recursively) retrieve all elements contained in the container
    all_elements = []
    for el_id in r.vars['v_contained_ids']:
        print "Retrieving element '%s'" % el_id
        r = Element.retrieveFromDB(collection,el_id)
        all_elements.append(r)


    #f = r.flatten()   # results in 1-dimensional list of all elements
    # h = tools.prerender_as_HTML(f)

    # further initial experiments
    #a = Element()
    #b = r
    c = TextElement({'v_id':"DOCX.a", 'v_content':"Brown fox jumps over yellow dog."})
    f = [c]
    #############################

    f = all_elements

    # (2) pass individual elements on to the template for rendering
    return render_template("show.html",entries=f,id=id)

if __name__ == "__main__":
    app.run()
