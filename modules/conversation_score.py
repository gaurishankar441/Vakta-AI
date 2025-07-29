def score_conversation(text, lang="en"):
    # You can expand this logic for multilingual scoring later
    grammar_issues = 0
    comment = "✅ Great job! No major grammar issues found."

    # Very simple heuristic for now:
    if lang == "en":
        if "i am" in text.lower() or "my name" in text.lower():
            grammar_issues = 0
        elif "he go" in text.lower() or "she go" in text.lower():
            grammar_issues = 1
            comment = "⚠️ Small grammar issue: Use 'goes' with he/she."
        elif len(text.split()) < 4:
            grammar_issues = 2
            comment = "💡 Try speaking a full sentence to improve fluency."
    elif lang == "hi":
        comment = "✅ अच्छा काम! आपकी हिंदी समझ में आई।"

    score = 100 - (grammar_issues * 10)

    return {
        "score": max(score, 60),
        "grammar_issues": grammar_issues,
        "comment": comment
    }
