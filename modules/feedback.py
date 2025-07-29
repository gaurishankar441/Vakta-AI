# modules/feedback.py

import language_tool_python
from langdetect import detect

def give_feedback(text):
    if not text or not text.strip():
        return "⚠️ No input provided for feedback."

    try:
        lang_code = detect(text)

        # Match language for tool
        if lang_code == "hi":
            tool = language_tool_python.LanguageTool('hi-IN')
        else:
            tool = language_tool_python.LanguageTool('en-US')

        matches = tool.check(text)

        if not matches:
            return "✅ Great job! No major grammar issues found."

        suggestions = []
        for match in matches[:3]:  # Limit feedback to top 3 issues
            suggestions.append(f"• {match.message} (Suggestion: {match.replacements[:1]})")

        feedback_text = "🔍 Here’s some feedback:\n" + "\n".join(suggestions)
        return feedback_text

    except Exception as e:
        return f"❌ Error in feedback: {str(e)}"
