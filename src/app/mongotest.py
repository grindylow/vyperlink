from mongoengine import *
from element import *
from datetime import *

if __name__ == "__main__":
    connect('vyperlink_main')
    
    e1 = Element(v_id='DOC101.1')
    e1.v_timestamp = datetime.now()
    e1.save()

    e2 = Element(v_id='DOC101.2',v_content='Second paragraph.')
    e2.v_timestamp = datetime.now()
    e2.save()

    e3 = e2
    e3.v_id = 'DOC101.3'
    e3.save()
    
