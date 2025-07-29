# modules/response.py

from modules.gpt_response import generate_gpt_response

def generate_response(intent, lang="en", text=None):
    responses = {
        "greeting": {
            "en": "Hello! How can I help you learn today?",
            "hi": "नमस्ते! आज आप क्या सीखना चाहेंगे?"
        },
        "introduction": {
            "en": "Nice to meet you! Let's begin with some simple conversation.",
            "hi": "आपसे मिलकर खुशी हुई! चलिए आसान बातचीत से शुरुआत करते हैं।"
        },
        "learn_english": {
            "en": "Great! Let's practice English together.",
            "hi": "बहुत बढ़िया! चलिए साथ में अंग्रेज़ी का अभ्यास करते हैं।"
        },
        "ask_story": {
            "en": "Sure! Once upon a time, there was a curious learner just like you...",
            "hi": "ज़रूर! एक समय की बात है, एक जिज्ञासु विद्यार्थी था बिलकुल आपकी तरह..."
        },
        "ask_tip": {
            "en": "Here are some tips: Practice daily, watch English shows, and speak confidently.",
            "hi": "कुछ सुझाव हैं: रोज़ अभ्यास करें, अंग्रेज़ी शो देखें, और आत्मविश्वास से बोलें।"
        },
        "default": {
            "en": "I didn't quite understand. Can you say it differently?",
            "hi": "मैं पूरी तरह से समझ नहीं पाया। क्या आप दोबारा कह सकते हैं?"
        }
    }

    if intent in responses:
        return responses[intent].get(lang, responses[intent]["en"])
    
    # GPT fallback if intent not found
    if text:
        return generate_gpt_response(text)

    return responses["default"].get(lang, responses["default"]["en"])
