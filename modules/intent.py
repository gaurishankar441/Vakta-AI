# modules/intent.py
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

intent_examples = {
    "greeting": ["hello", "hi", "hey", "good morning", "good evening"],
    "introduction": ["my name is", "let me introduce myself", "i want to introduce"],
    "learn_english": ["i want to learn english", "how to speak english", "help me with english"],
    "ask_story": ["tell me a story", "share a funny story", "can you tell an english story"],
    "default": []
}

def detect_intent(text):
    text_emb = model.encode(text, convert_to_tensor=True)
    best_intent = "default"
    best_score = 0.0

    for intent, examples in intent_examples.items():
        for ex in examples:
            ex_emb = model.encode(ex, convert_to_tensor=True)
            score = util.pytorch_cos_sim(text_emb, ex_emb).item()
            if score > best_score:
                best_score = score
                best_intent = intent

    # optional: only return if above a threshold
    if best_score < 0.5:
        return "default"
    return best_intent
