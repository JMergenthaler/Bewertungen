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

def add_title_with_check(i):
  """
  Adds the title in front of the text, but checks if the title is already the start of the text.

  Args:
      i: A dictionary containing the keys 'title' and 'text'.

  Returns:
      A string with the title and text combined, with a space in between if the title is not already the start of the text.
  """
  title = i['title']
  text = i['text']
  if text != None:
    if not text.startswith(title):
        bewertung = f"{title} {text}"
    else:
        bewertung = text
    return bewertung
  else:
    return title

def Translate():
    Path = ".\/testamazon\/json\/s\/"
    with open(Path + 'review.json', 'r', encoding='utf-8') as f:
    
    # returns JSON object as 
    # a dictionary

        data = json.load(f)
        
        # Iterating through the json
        # list
        with open(Path + 'bert.json', 'w') as f2:
            j = 0
            outputs = []
            for i in data:
                bewertung = i['text']
                trans_title = i['title']
                bewertung = remove_emoji(bewertung)
                trans_title = remove_emoji(trans_title)
                if trans_title == None or trans_title == "" or trans_title == " ":
                   continue
                if len(outputs) <= 6 and j + 7 > len(data):
                   if bewertung == None:
                      continue
                   if len(bewertung) <= 50:
                      continue
                print(bewertung)
                if detect(bewertung) != 'en':
                    review = GoogleTranslator(source='auto', target='en').translate(bewertung)
                    trans_title = GoogleTranslator(source='auto', target='en').translate(trans_title)
                else:
                    review = bewertung
                outputs.append({"text": review, "rating":i['rating'], "title": trans_title})
                j += 1
            json.dump(outputs, f2)
        f2.close()
    f.close()

if __name__ == "__main__":
    Translate()