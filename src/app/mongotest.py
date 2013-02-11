from mongoengine import *
from element import *
from datetime import *

if __name__ == "__main__":
    connect('vyperlink_main')
    
    e1 = Element(v_id='DOC101.1')
    e1.v_timestamp = datetime.now()
    e1.save()

    e2 = TextElement(v_id='DOC101.2',v_content='Second paragraph.')
    e2.v_timestamp = datetime.now()
    e2.save()

    e3 = TextElement(v_id='DOC101.7',v_content='Seventh paraglider. Rev 2.')
    e3.v_timestamp = datetime.now()
    e3.save()
    
    eA = CollectionElement()
    eA.v_id = 'DOC101'
    eA.v_contained_ids = [ "DOC101.1", "DOC101.2", "DOC101.7" ]
    eA.v_timestamp = datetime.now()
    eA.save()
