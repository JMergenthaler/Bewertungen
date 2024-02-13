from deep_translator import GoogleTranslator
import json
from langdetect import detect


Path = ".\/testamazon\/json\/s\/"
def Translate():
    with open(Path + 'review.json', 'r', encoding='utf-8') as f:
    
    # returns JSON object as 
    # a dictionary

        data = json.load(f)
        
        # Iterating through the json
        # list
        with open(Path + 'bert.json', 'w') as f2:

            outputs = []
            for i in data:
                bewertung = f"{i['title']} {i['text']}"
                if detect(bewertung) != 'en':
                    review = GoogleTranslator(source='auto', target='en').translate(bewertung)
                else:
                    review = bewertung
                outputs.append({"review": review})
            json.dump(outputs, f2)
        f2.close()
    f.close()

Translate()
