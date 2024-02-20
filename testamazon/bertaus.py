import tensorflow as tf
from transformers import BertTokenizer
import json

def load_model():
    model_path = 'testamazon/savemodel/'

    # Load the trained model from the SavedModel directory
    loaded_model = tf.saved_model.load(model_path)

    print(list(loaded_model.signatures.keys()))  # Prints the available signature keys
    signature_key = list(loaded_model.signatures.keys())[0]  # Typically 'serving_default', adjust if necessary
    print(loaded_model.signatures[signature_key].structured_outputs)

    # Initialize the tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    return tokenizer, loaded_model

def predict_review(review_text, tokenizer, loaded_model):
    # Tokenize the input text
    print(review_text)
    inputs = tokenizer(str(review_text), add_special_tokens=True, padding='max_length', truncation=True, max_length=512, return_tensors='tf')
    
    # Prepare the inputs for the model
    input_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    # Ensure token_type_ids are generated and included
    token_type_ids = inputs.get('token_type_ids', tf.zeros_like(input_ids))  # Default to zeros if not provided

    # Serving signature for prediction
    infer = loaded_model.signatures["serving_default"]
    
    # Make prediction. Adjust according to your model's signature.
    predictions = infer(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids)['logits']  # Adjust output key if necessary
    
    # Convert logits to probabilities
    probabilities = tf.nn.softmax(predictions, axis=1).numpy()[0]
    
    # The index of the highest probability is our predicted label
    predicted_label_index = tf.argmax(probabilities).numpy()
    
    # Convert the predicted label index to label
    label_dict = {0: 'fake', 1: 'real'}
    predicted_label = label_dict[predicted_label_index]
    
    # Print the results
    print(f"Review: {review_text}")
    print(f"Predicted Label: {predicted_label}")
    print(f"Confidence Scores: Fake: {probabilities[0]}, Real: {probabilities[1]}")
    return {
        'Fake': probabilities[0],
        'Real': probabilities[1],
    }


# Test the function with a new review
    

def auswertung():
    tokenizer, loaded_model = load_model()
    Path = 'testamazon/json/s/'
    fake = 0
    reviews = []
    try:
        with open(Path + "bert.json", "r") as f:
            table = json.load(f)
            for element in table:
                reviews.append(element["review"])
    except:
        print("No File")
    for review in reviews:
        x = predict_review(review, tokenizer, loaded_model)
        fake += x['Fake']
    fake = fake / len(reviews)
    real = 1 - fake
    return {
        'Fake': fake,
        'Real': real,
    }
    
if __name__ == "__main__":
    # This code block will only execute if bertaus.py is the entry point to the program,
    # not when it is imported as a module.
    x = auswertung()
    print(f"Fake: {x['Fake']} Real: {x['Real']}")