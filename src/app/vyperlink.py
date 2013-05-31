from flask import Flask,render_template,jsonify,request
from flask_debugtoolbar import DebugToolbarExtension
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
    id = request.args.get("id")
    connect("vyperlink_main")
    r = Element.objects(v_id=id).order_by('-v_timestamp')[0]  #,ts<=ts
    return jsonify(r=r.v_content)

@app.route("/putrawafterediting",methods=["POST"])
def putrawafterediting():
    # @todo Check that submitted revision is based on the latest
    #       revision currently in the database. If not -> conflict!
    # @todo Have any "explicit" variables been changed? If so,
    #       propagate those changes to my parent. (...and they to theirs
    #       etc etc...)
    id = request.form["id"]
    rawtext = request.form["rawtext"]
    connect("vyperlink_main")
    el = TextElement(v_id=id,v_content=rawtext,v_timestamp = datetime.now())
    el.extractVariables()
    el.save()
    return jsonify(r=rawtext)

@app.route("/insertbelow",methods=["POST"])
def insertbelow():
    id = request.form["id"]
    parentid = request.form["parentid"]
    connect("vyperlink_main")
    newid = inventNewId(id,parentid)
    ts = datetime.now()
    #@todo potential race condition between inventNewId and actual save-to-database

    # create the new element
    el = TextElement(v_id=newid,v_content="newly created",v_timestamp = ts)
    el.save()

    # update parent (=container)
    r = Element.objects(v_id=parentid).order_by('-v_timestamp')[0]  #,ts<=ts
    if not isinstance(r,CollectionElement):
        raise BaseException( "parent is NOT a ContainerElement" )

    l = r.v_contained_ids
    index = l.index(id)
    l.insert(index+1,newid)

    el = CollectionElement()
    el.v_id = r.v_id
    el.v_timestamp = ts
    el.v_contained_ids = l
    el.save()

    return jsonify(id=newid,ts="11T22:22:22.222")

@app.route("/insertabove",methods=["POST"])
def insertabove():
    id = request.form["id"]
    parentid = request.form["parentid"]
    connect("vyperlink_main")
    newid = inventNewId(id,parentid)
    ts = datetime.now()
    #@todo potential race condition between inventNewId and actual save-to-database

    # create the new element
    el = TextElement(v_id=newid,v_content="newly created",v_timestamp = ts)
    el.save()

    # update parent (=container)
    r = Element.objects(v_id=parentid).order_by('-v_timestamp')[0]  #,ts<=ts
    if not isinstance(r,CollectionElement):
        raise BaseException( "parent is NOT a ContainerElement" )

    l = r.v_contained_ids
    index = l.index(id)
    l.insert(index,newid)

    el = CollectionElement()
    el.v_id = r.v_id
    el.v_timestamp = ts
    el.v_contained_ids = l
    el.save()

    return jsonify(id=newid,ts="11T22:22:22.222")

def inventNewId(startingPoint,parentid=""):
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
        r = Element.objects(v_id=suggestedId)
        if len(r)==0:
            break
        i = i + 1
    return suggestedId

@app.route("/create/<id>")
def create(id=None):
    """Create a new CollectionElement with the given ID"""
    connect("vyperlink_main")
    ts = datetime.now() # now

    # (1) check ID doesn't exist already
    r = Element.objects(v_id=id)
    if len(r)>0:
        return "%s exists already"%(id)
    
    # (2) create a first contained (text) element
    newid = inventNewId("",id)
    el = TextElement(v_id=newid,v_content="Insert content here...",v_timestamp = ts)
    el.save()

    # (3) create a new collection element
    el = CollectionElement()
    el.v_id = id
    el.v_timestamp = ts
    el.v_contained_ids = [newid]
    el.save()

    return "created!"

@app.route("/show/<id>")
def show(id=None):
    """Show the given document (as HTML)"""
    connect("vyperlink_main")
    #ts = datetime.datetime() # now

    # (1) retrieve contained elements (parent must be a ContainerElement)
    r = Element.objects(v_id=id).order_by('-v_timestamp')[0]
    # will fail if it doesn't exist

    if not isinstance(r,CollectionElement):
        raise BaseException( "Is NOT Container" )

    print "We have a collection (container). Let's see..."

    # (recursively) retrieve all elements contained in the container
    all_elements = []
    for el_id in r.v_contained_ids:
        print "Retrieving element '%s'" % el_id
        r = Element.objects(v_id=el_id).order_by('-v_timestamp')[0]
        all_elements.append(r)


    #f = r.flatten()   # results in 1-dimensional list of all elements
    # h = tools.prerender_as_HTML(f)

    # further initial experiments
    a = Element()
    b = r
    c = TextElement(v_id="DOCX.a", v_content="Brown fox jumps over yellow dog.")
    f = [a,b,c]
    #############################

    f = all_elements

    # (2) pass individual elements on to the template for rendering
    return render_template("show.html",entries=f,id=id)

if __name__ == "__main__":
    app.run()
