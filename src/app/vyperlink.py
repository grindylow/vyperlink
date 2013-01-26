from flask import Flask,render_template
from flask_debugtoolbar import DebugToolbarExtension
from element import *

app = Flask(__name__)

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'pass'

toolbar = DebugToolbarExtension(app)

@app.route("/")
def hello():
    return render_template("home.html")

@app.route("/show/<id>")
def show(id=None):
    """Show the given document (as HTML)"""
    connect("vyperlink_main")
    #ts = datetime.datetime() # now
    r = Element.objects(v_id=id)[0]  #,ts<=ts
    #f = r.flatten()   # results in 1-dimensional list of all elements
    # h = tools.prerender_as_HTML(f)

    # (1) retrieve contained elements (parent must be a ContainerElement)
    a = Element()
    b = r
    c = TextElement(v_content="Brown fox jumps over yellow dog.")
    f = [a,b,c]

    # (2) pass individual elements on to the template for rendering
    return render_template("show.html",entries=f,id=id)

if __name__ == "__main__":
    app.run()
