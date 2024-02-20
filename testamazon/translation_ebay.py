from deep_translator import GoogleTranslator
import json
from langdetect import detect
import re

def remove_emoji(text):
  """
  Removes all emojis from a string.

  Args:
      text: The string to remove emojis from.

  Returns:
      A new string with all emojis removed.
  """  
  emoji_pattern = re.compile(
      "["
      u"\U0001F600-\U0001F64F"  # Emoticons
      u"\U0001F300-\U0001F5FF"  # Symbols & pictographs
      u"\U0001F680-\U0001F6FF"  # Transport & map symbols
      u"\U0001F1E0-\U0001F1FF"  # Flags (iOS)
      u"\U00002702-\U000027B0"  # Dingbats
      "]+",
      flags=re.UNICODE
  )
  return emoji_pattern.sub(r'', text)

def Translate_Ebay():
    Path = './testamazon/json/s/'
    f = open(Path + "review.json", "r", encoding='utf-8')
    
    # returns JSON object as 
    # a dictionary

    data = json.load(f)
    
    # Iterating through the json
    # list
    with open(Path + 'bert.json', 'w') as f2:

        outputs = []
        for i in data:
            item = remove_emoji(i['review'])
            if item == None or item == "":
                continue
            if detect(item) != 'en':
                review = GoogleTranslator(source='auto', target='en').translate(item)
            else:
                review = item
            outputs.append({"review": review})
        json.dump(outputs, f2)
    f2.close()
    f.close()
if __name__ == "__main__":
    Translate_Ebay()
