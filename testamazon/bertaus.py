import tensorflow as tf
from transformers import BertTokenizer
import json

# Path to the directory where the saved model is
model_path = './savemodel/'

# Load the trained model from the SavedModel directory
loaded_model = tf.saved_model.load(model_path)

print(list(loaded_model.signatures.keys()))  # Prints the available signature keys
signature_key = list(loaded_model.signatures.keys())[0]  # Typically 'serving_default', adjust if necessary
print(loaded_model.signatures[signature_key].structured_outputs)

# Initialize the tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

def predict_review(review_text):
    # Tokenize the input text
    inputs = tokenizer(review_text, add_special_tokens=True, padding='max_length', truncation=True, max_length=512, return_tensors='tf')
    
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
    fake = 0
    reviews = []
    try:
        with open("./bert.json", "r") as f:
            table = json.load(f)
            for element in table:
                reviews.append(element["review"])
    except:
        print("No File")
    for review in reviews:
        x = predict_review(review)
        fake += x['Fake']
    fake = fake / len(reviews)
    real = 1 - fake
    return {
        'Fake': fake,
        'Real': real,
    }
x = auswertung()
print(f"Fake: {x['Fake']} Real: {x['Real']}")
    