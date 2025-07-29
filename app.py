import streamlit as st
from modules.audio_input import record_audio
from modules.speech_to_text import transcribe_audio
from modules.intent import detect_intent
from modules.response import generate_response
from modules.text_to_speech import speak_text
from modules.feedback import give_feedback
from modules.conversation_score import score_conversation
from modules.user_progress import update_user_progress, get_progress_summary
from modules.gpt_response import generate_gpt_response  # ✅ GPT Fallback
from modules.user_progress import get_next_topic

# 🎯 Page Setup
st.set_page_config(page_title="Vakta AI", page_icon="🧠", layout="centered")
st.title("🧠 Vakta AI - Voice Tutor")
st.markdown("Talk to your AI tutor in English or Hindi. Click the mic and start speaking!")

# 🔁 Session memory
if "history" not in st.session_state:
    st.session_state.history = []
if "progress" not in st.session_state:
    st.session_state.progress = []

# 🧹 Clear history
if st.button("🧹 Clear History"):
    st.session_state.history = []
    st.session_state.progress = []
    st.success("✅ History cleared!")

# 🎙️ Main interaction
if st.button("🎙️ Speak Now"):
    audio_path = record_audio(duration=5)
    st.success("✅ Recording Complete")

    try:
        result = transcribe_audio(audio_path)
        if isinstance(result, tuple):
            text, lang = result
        else:
            text, lang = "", "en"

        if not text.strip():
            st.warning("😕 Couldn't understand. Please speak clearly.")
        else:
            st.markdown(f"**📝 You said:** `{text}`")
            st.markdown(f"**🌍 Language Detected:** `{lang}`")

            # 🧠 Intent detection
            intent = detect_intent(text)
            st.markdown(f"**🧠 Intent Detected:** `{intent}`")

            # 🤖 Response generation
            response = generate_response(intent, lang=lang, text=text)
            st.markdown(f"**🤖 Response:** `{response}`")

            # 🔁 GPT fallback if default response
            if response in [
                "I didn't quite understand. Can you say it differently?",
                "मैं पूरी तरह से समझ नहीं पाया। क्या आप दोबारा कह सकते हैं?"
            ]:
                from modules.gpt_response import generate_gpt_response
                gpt_response = generate_gpt_response(text, lang=lang)
                if gpt_response:
                    response = gpt_response
                    st.markdown(f"**🤖 GPT Response:** `{response}`")

            # 🔊 Speak the final response
            speak_text(response, lang=lang)

            # 🧪 Feedback
            feedback = give_feedback(text)
            st.markdown(f"**🧪 Feedback:** {feedback}")
            speak_text(feedback, lang=lang)

            # 📊 Score
            score_data = score_conversation(text, lang=lang)
            st.markdown(f"**📊 Score:** `{score_data['score']}/100`")
            st.markdown(f"**📉 Grammar Issues:** `{score_data['grammar_issues']}`")
            st.markdown(f"**💬 Comment:** {score_data['comment']}")
            speak_text(score_data["comment"], lang=lang)

            # 💾 Update history
            st.session_state.history.append({
                "user": text,
                "ai": response,
                "intent": intent
            })
            st.session_state.history = st.session_state.history[-5:]

            # ✅ Save user progress
            st.session_state.progress = update_user_progress(
                st.session_state.progress,
                text=text,
                intent=intent,
                score=score_data["score"],
                lang=lang
            )

    except Exception as e:
        st.error(f"❌ Error: {e}")

# 🗂️ Conversation History
st.markdown("---")
st.subheader("🗂️ Conversation History")

for item in reversed(st.session_state.history):
    st.markdown(f"**🧑 You:** {item['user']}")
    st.markdown(f"**🤖 Vakta AI:** {item['ai']}")
    st.markdown(f"<span style='font-size: 0.8em; color: gray;'>Intent: {item['intent']}</span>", unsafe_allow_html=True)
    st.markdown("---")

    # 📈 Display Progress Summary
    st.markdown("## 📈 Your Progress Summary")
    st.markdown(get_progress_summary(st.session_state.progress))

    # 📚 What to learn next
    next_topic = get_next_topic(st.session_state.progress)
    st.markdown("## 📚 Suggested Next Topic")
    st.markdown(f"**👉 {next_topic}**")

