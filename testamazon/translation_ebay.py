from deep_translator import GoogleTranslator
import json
from langdetect import detect



def Translate_Ebay():
    f = open("ebay.json")
    
    # returns JSON object as 
    # a dictionary

    data = json.load(f)
    
    # Iterating through the json
    # list
    with open('bert.json', 'w') as f2:

        outputs = []
        for i in data:
            if detect(i['review']) != 'en':
                review = GoogleTranslator(source='auto', target='en').translate(i['review'])
            else:
                review = i['review']
            outputs.append({"review": review})
        json.dump(outputs, f2)
    f2.close()
    f.close()

Translate_Ebay()
