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
    id = request.form["id"]
    rawtext = request.form["rawtext"]
    connect("vyperlink_main")
    el = TextElement(v_id=id,v_content=rawtext,v_timestamp = datetime.now())
    el.save()
    return jsonify(r="Processed: %s"%rawtext)

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

    a = Element()
    b = r
    c = TextElement(v_id="DOCX.a", v_content="Brown fox jumps over yellow dog.")
    f = [a,b,c]

    f = all_elements

    # (2) pass individual elements on to the template for rendering
    return render_template("show.html",entries=f,id=id)

if __name__ == "__main__":
    app.run()
