# modules/user_progress.py

learning_path = {
    "beginner": ["greeting", "introduction", "common_phrases"],
    "intermediate": ["asking_questions", "story_telling", "giving_opinions"],
    "advanced": ["debate", "interview_practice", "roleplay"]
}

# Optional: You can expand this based on your curriculum
intent_labels = {
    "greeting": {"en": "Greeting", "hi": "अभिवादन"},
    "introduction": {"en": "Introduction", "hi": "परिचय"},
    "common_phrases": {"en": "Common Phrases", "hi": "सामान्य वाक्य"},
    "asking_questions": {"en": "Asking Questions", "hi": "सवाल पूछना"},
    "story_telling": {"en": "Story Telling", "hi": "कहानी सुनाना"},
    "giving_opinions": {"en": "Giving Opinions", "hi": "राय देना"},
    "debate": {"en": "Debate", "hi": "वाद-विवाद"},
    "interview_practice": {"en": "Interview Practice", "hi": "साक्षात्कार अभ्यास"},
    "roleplay": {"en": "Roleplay", "hi": "भूमिका निभाना"},
}


def update_user_progress(progress, text, intent, score, lang="en"):
    """Update progress tracking for given intent and score."""
    if not intent:
        return progress

    for item in progress:
        if item["intent"] == intent:
            item["count"] += 1
            item["scores"].append(score)
            return progress

    # New intent entry
    progress.append({
        "intent": intent,
        "scores": [score],
        "count": 1
    })
    return progress


def get_progress_summary(progress, lang="en"):
    """Generate readable progress summary based on user's history."""
    if not progress:
        return "🚀 Start speaking to see your progress here."

    lines = []
    for item in progress:
        avg = sum(item["scores"]) / len(item["scores"])
        label = intent_labels.get(item["intent"], {}).get(lang, item["intent"].capitalize())
        lines.append(f"**{label}**: {avg:.1f}/100 ({item['count']} attempts)")

    return "\n\n".join(lines)


def get_next_topic(progress):
    """Decide next topic for user based on completion and performance."""
    completed = {item["intent"]: sum(item["scores"]) / len(item["scores"]) for item in progress}

    for level in ["beginner", "intermediate", "advanced"]:
        for topic in learning_path[level]:
            if topic not in completed or completed[topic] < 60:
                return topic

    return "✅ All topics completed! Great job!"
