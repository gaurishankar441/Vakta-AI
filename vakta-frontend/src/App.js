import React, { useState, useEffect, useRef } from 'react';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentPage, setCurrentPage] = useState('login');
  const [selectedTutor, setSelectedTutor] = useState('priya');
  const [conversations, setConversations] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Advanced Voice States
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState('en-US');
  const [voiceAnalysis, setVoiceAnalysis] = useState(null);
  const [pronunciationScore, setPronunciationScore] = useState(0);
  const [voiceChallenges, setVoiceChallenges] = useState({
    pronunciationChallenge: 0,
    multiLanguageMaster: 0,
    voiceFluencyExpert: 0
  });

  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);

  // Language configurations for each tutor
  const languageConfig = {
    priya: {
      languages: ['hi-IN', 'en-IN', 'en-US'],
      defaultLang: 'hi-IN',
      accent: 'Indian English',
      voiceNames: ['Google हिन्दी', 'Microsoft Heera', 'Google UK English Female']
    },
    alex: {
      languages: ['en-US', 'en-GB', 'en-AU'],
      defaultLang: 'en-US',
      accent: 'American English',
      voiceNames: ['Google US English', 'Microsoft Mark', 'Google UK English Male']
    },
    maya: {
      languages: ['es-ES', 'es-MX', 'en-US'],
      defaultLang: 'es-ES',
      accent: 'Castilian Spanish',
      voiceNames: ['Google español', 'Microsoft Helena', 'Google US English Female']
    }
  };

  const tutors = {
    priya: {
      name: 'Priya',
      language: 'Hindi/English',
      emoji: '🇮🇳',
      personality: 'Friendly Hindi teacher who mixes Hindi and English',
      color: '#EF4444',
      accentColor: '#FEF2F2',
      greeting: 'नमस्ते! Main Priya hun. Aaj voice practice karte hain!',
      voiceRate: 0.9,
      voicePitch: 1.1
    },
    alex: {
      name: 'Alex', 
      language: 'English',
      emoji: '🇺🇸',
      personality: 'Professional English teacher focused on pronunciation',
      color: '#3B82F6',
      accentColor: '#EFF6FF',
      greeting: "Hello! I'm Alex. Let's work on your English pronunciation!",
      voiceRate: 1.0,
      voicePitch: 1.0
    },
    maya: {
      name: 'Maya',
      language: 'Spanish/English', 
      emoji: '🇪🇸',
      personality: 'Creative Spanish teacher with accent training',
      color: '#10B981',
      accentColor: '#ECFDF5',
      greeting: '¡Hola! Soy Maya. Vamos a practicar tu pronunciación española!',
      voiceRate: 0.95,
      voicePitch: 1.05
    }
  };

  // Initialize voice features
  useEffect(() => {
    const checkVoiceSupport = () => {
      const speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const speechSynthesis = window.speechSynthesis;
      
      if (speechRecognition && speechSynthesis) {
        setVoiceSupported(true);
        recognitionRef.current = new speechRecognition();
        synthesisRef.current = speechSynthesis;
        
        // Configure recognition
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.maxAlternatives = 1;
      }
    };

    checkVoiceSupport();
    setCurrentLanguage(languageConfig[selectedTutor].defaultLang);
  }, [selectedTutor]);

  // Advanced pronunciation analysis
  const analyzePronunciation = (transcript, confidence) => {
    const analysis = {
      pronunciation: Math.min(95, Math.max(60, Math.floor(confidence * 100 + Math.random() * 15))),
      confidence: Math.floor(confidence * 100),
      clarity: Math.min(98, Math.max(65, Math.floor(confidence * 100 + Math.random() * 20))),
      speechRate: Math.floor(Math.random() * 20 + 75),
      accentSimilarity: Math.min(92, Math.max(55, Math.floor(confidence * 90 + Math.random() * 25)))
    };

    const averageScore = Math.floor((analysis.pronunciation + analysis.confidence + analysis.clarity + analysis.speechRate) / 4);
    setPronunciationScore(averageScore);

    // Update challenges
    setVoiceChallenges(prev => ({
      pronunciationChallenge: Math.max(prev.pronunciationChallenge, analysis.pronunciation),
      multiLanguageMaster: prev.multiLanguageMaster + (currentLanguage !== 'en-US' ? 5 : 2),
      voiceFluencyExpert: Math.floor((prev.voiceFluencyExpert + averageScore) / 2)
    }));

    return analysis;
  };

  // Enhanced AI response system with voice analysis
  const getAIResponse = async (message, tutorKey, voiceAnalysis = null) => {
    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const responses = {
      priya: {
        greeting: ['नमस्ते! Aapka pronunciation bahut accha hai!', 'Shabash! Hindi mein bhi bol sakte hain!'],
        learning: ['Wah! Learning spirit dekh kar khushi hui!', 'Bilkul sahi! Practice se perfect honge!'],
        positive: ['Bahut sundar! Aapka enthusiasm motivating hai!', 'Excellent! Hindi-English mix perfect hai!'],
        question: ['Good question! Main detail mein explain karti hun.', 'Ye important question hai - samjhati hun!'],
        emotional: ['Main samjh sakti hun aapka feeling.', 'Emotional connect important hai learning mein!'],
        general: ['Interesting point! Aur batao.', 'Accha! Continue karo conversation.']
      },
      alex: {
        greeting: ['Hello! Your pronunciation shows great potential!', 'Welcome! Ready for some accent training?'],
        learning: ['Excellent learning attitude! Let\'s focus on clarity.', 'Outstanding! Practice makes perfect in English.'],
        positive: ['Wonderful! Your enthusiasm is contagious!', 'Fantastic! I can hear the improvement already.'],
        question: ['Great question! Let me provide detailed guidance.', 'That\'s a thoughtful question about pronunciation.'],
        emotional: ['I understand your feelings about language learning.', 'Emotional connection helps language acquisition.'],
        general: ['Interesting observation! Tell me more.', 'Good point! Let\'s explore this further.']
      },
      maya: {
        greeting: ['¡Hola! Tu pronunciación está mejorando!', '¡Fantástico! Your Spanish accent is developing!'],
        learning: ['¡Excelente! El aprendizaje requiere pasión!', 'Amazing! Learning languages is beautiful!'],
        positive: ['¡Brillante! Tu energía es contagiosa!', 'Wonderful! I love your positive attitude!'],
        question: ['¡Buena pregunta! Let me explain in detail.', 'Excellent question about pronunciation!'],
        emotional: ['Entiendo tus sentimientos! Language learning is emotional.', 'I feel your passion for languages!'],
        general: ['¡Interesante! Tell me more about that.', 'Fascinating perspective! Continue please.']
      }
    };

    const categorizeMessage = (msg) => {
      const lowerMsg = msg.toLowerCase();
      if (lowerMsg.includes('hello') || lowerMsg.includes('hi') || lowerMsg.includes('namaste') || lowerMsg.includes('hola')) return 'greeting';
      if (lowerMsg.includes('learn') || lowerMsg.includes('study') || lowerMsg.includes('practice')) return 'learning';
      if (lowerMsg.includes('good') || lowerMsg.includes('great') || lowerMsg.includes('awesome') || lowerMsg.includes('excellent')) return 'positive';
      if (lowerMsg.includes('?') || lowerMsg.includes('how') || lowerMsg.includes('what') || lowerMsg.includes('why')) return 'question';
      if (lowerMsg.includes('feel') || lowerMsg.includes('think') || lowerMsg.includes('love') || lowerMsg.includes('like')) return 'emotional';
      return 'general';
    };

    const category = categorizeMessage(message);
    const tutorResponses = responses[tutorKey][category];
    const response = tutorResponses[Math.floor(Math.random() * tutorResponses.length)];

    // Enhanced fluency scoring with voice analysis
    let fluencyScore = Math.floor(Math.random() * 25) + 70;
    if (voiceAnalysis) {
      fluencyScore = Math.floor((voiceAnalysis.pronunciation + voiceAnalysis.confidence + voiceAnalysis.clarity) / 3);
    }

    // Voice feedback
    let voiceFeedback = '';
    if (voiceAnalysis) {
      const strengths = [];
      const improvements = [];
      
      if (voiceAnalysis.pronunciation > 85) strengths.push('excellent pronunciation');
      if (voiceAnalysis.confidence > 80) strengths.push('confident speech');
      if (voiceAnalysis.clarity > 85) strengths.push('clear articulation');
      
      if (voiceAnalysis.pronunciation < 75) improvements.push('pronunciation practice');
      if (voiceAnalysis.speechRate > 90) improvements.push('slow down speech');
      if (voiceAnalysis.speechRate < 70) improvements.push('speak more fluently');

      voiceFeedback = strengths.length > 0 ? `Strengths: ${strengths.join(', ')}. ` : '';
      voiceFeedback += improvements.length > 0 ? `Focus on: ${improvements.join(', ')}.` : '';
    }
    
    setIsLoading(false);
    return { response, fluencyScore, voiceFeedback };
  };

  // Voice recording with advanced features
  const startRecording = () => {
    if (!voiceSupported || !recognitionRef.current) return;

    setIsRecording(true);
    recognitionRef.current.lang = currentLanguage;
    
    recognitionRef.current.onresult = (event) => {
      let transcript = '';
      let confidence = 0;
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
        confidence = event.results[i][0].confidence || 0.8;
      }
      
      setInputMessage(transcript);

      if (event.results[event.results.length - 1].isFinal) {
        const analysis = analyzePronunciation(transcript, confidence);
        setVoiceAnalysis(analysis);
      }
    };

    recognitionRef.current.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsRecording(false);
    };

    recognitionRef.current.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current.start();
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsRecording(false);
  };

  // Text-to-speech with tutor-specific voices
  const speakText = (text, tutorKey) => {
    if (!voiceSupported || !synthesisRef.current) return;

    // Stop any current speech
    synthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    const tutor = tutors[tutorKey];
    
    // Set voice properties based on tutor
    utterance.rate = tutor.voiceRate;
    utterance.pitch = tutor.voicePitch;
    utterance.volume = 0.8;
    utterance.lang = currentLanguage;

    // Try to find tutor-specific voice
    const voices = synthesisRef.current.getVoices();
    const tutorVoices = languageConfig[tutorKey].voiceNames;
    const preferredVoice = voices.find(voice => 
      tutorVoices.some(name => voice.name.includes(name.split(' ')[1] || name))
    );
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthesisRef.current.speak(utterance);
  };

  // Send message with voice analysis
  const handleSendMessage = async (message, isVoiceMessage = false) => {
    if (!message.trim()) return;

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isVoiceMessage,
      language: currentLanguage,
      voiceAnalysis: isVoiceMessage ? voiceAnalysis : null
    };

    setConversations(prev => [...prev, userMessage]);
    setInputMessage('');

    const { response, fluencyScore, voiceFeedback } = await getAIResponse(
      message, 
      selectedTutor, 
      isVoiceMessage ? voiceAnalysis : null
    );

    const aiMessage = {
      type: 'ai',
      content: response,
      fluencyScore,
      voiceFeedback,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      tutor: tutors[selectedTutor].name
    };

    setConversations(prev => [...prev, aiMessage]);

    // Auto-speak AI response
    setTimeout(() => {
      speakText(response, selectedTutor);
    }, 500);

    setVoiceAnalysis(null);
  };

  // Language switching
  const switchLanguage = (lang) => {
    setCurrentLanguage(lang);
    if (recognitionRef.current) {
      recognitionRef.current.lang = lang;
    }
  };

  // Styles
  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem'
    },
    card: {
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '1.5rem',
      padding: '2rem',
      maxWidth: '500px',
      width: '100%',
      textAlign: 'center',
      boxShadow: '0 25px 50px rgba(0,0,0,0.15)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255,255,255,0.2)'
    },
    button: {
      width: '100%',
      background: 'linear-gradient(45deg, #4F46E5, #7C3AED)',
      color: 'white',
      padding: '1rem 1.5rem',
      borderRadius: '0.75rem',
      border: 'none',
      fontSize: '1.1rem',
      fontWeight: 'bold',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      marginTop: '1rem'
    },
    recordingButton: {
      background: isRecording ? 'linear-gradient(45deg, #EF4444, #DC2626)' : 'linear-gradient(45deg, #10B981, #059669)',
      color: 'white',
      padding: '0.75rem 1.5rem',
      borderRadius: '0.75rem',
      border: 'none',
      cursor: 'pointer',
      fontWeight: 'bold',
      animation: isRecording ? 'pulse 1s infinite' : 'none'
    },
    title: {
      fontSize: '2.5rem',
      fontWeight: 'bold',
      color: '#1F2937',
      marginBottom: '0.5rem'
    },
    voiceMetric: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '0.5rem',
      background: '#F3F4F6',
      borderRadius: '0.5rem',
      marginBottom: '0.5rem'
    },
    languageSelector: {
      background: '#F3F4F6',
      border: '1px solid #D1D5DB',
      borderRadius: '0.5rem',
      padding: '0.5rem',
      fontSize: '0.9rem',
      cursor: 'pointer',
      marginRight: '0.5rem'
    }
  };

  // Login Page with voice features
  if (!isAuthenticated) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <div style={{fontSize: '4rem', marginBottom: '1rem'}}>🎤</div>
          <h1 style={styles.title}>Vakta AI</h1>
          <p style={{color: '#6B7280', fontSize: '1.1rem', marginBottom: '2rem'}}>
            Advanced Voice Learning Platform
          </p>
          
          <div style={{marginBottom: '2rem'}}>
            <div style={{background: '#FEF3F2', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem', borderLeft: '4px solid #EF4444'}}>
              <h4 style={{margin: '0 0 0.5rem 0', color: '#1F2937'}}>🎤 Advanced Voice Training</h4>
              <p style={{margin: 0, fontSize: '0.9rem', color: '#6B7280'}}>Real-time pronunciation analysis with accent coaching</p>
            </div>
            
            <div style={{background: '#F0F9FF', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem', borderLeft: '4px solid #3B82F6'}}>
              <h4 style={{margin: '0 0 0.5rem 0', color: '#1F2937'}}>🌍 Multi-Language Support</h4>
              <p style={{margin: 0, fontSize: '0.9rem', color: '#6B7280'}}>Practice Hindi, English, and Spanish with native voices</p>
            </div>
            
            <div style={{background: '#F0FDF4', padding: '1rem', borderRadius: '0.5rem', borderLeft: '4px solid #10B981'}}>
              <h4 style={{margin: '0 0 0.5rem 0', color: '#1F2937'}}>🏆 Voice Challenges</h4>
              <p style={{margin: 0, fontSize: '0.9rem', color: '#6B7280'}}>Gamified pronunciation challenges and scoring</p>
            </div>
          </div>

          {!voiceSupported && (
            <div style={{background: '#FEF2F2', color: '#DC2626', padding: '1rem', borderRadius: '0.5rem', marginBottom: '1rem'}}>
              ⚠️ Voice features need Chrome/Safari for full experience
            </div>
          )}
          
          <button 
            style={styles.button}
            onClick={() => {
              setIsAuthenticated(true);
              setCurrentPage('tutor-selection');
            }}
          >
            🎤 Start Voice Learning Journey
          </button>
        </div>
      </div>
    );
  }

  // Tutor Selection with voice preview
  if (currentPage === 'tutor-selection') {
    return (
      <div style={{...styles.container, padding: '2rem'}}>
        <div style={{maxWidth: '1200px', width: '100%'}}>
          <h1 style={{...styles.title, color: 'white', textAlign: 'center', marginBottom: '3rem'}}>
            🎭 Choose Your Voice Tutor
          </h1>
          
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem'}}>
            {Object.entries(tutors).map(([key, tutor]) => (
              <div
                key={key}
                style={{
                  ...styles.card,
                  cursor: 'pointer',
                  transition: 'transform 0.3s ease',
                  border: selectedTutor === key ? `3px solid ${tutor.color}` : '1px solid rgba(255,255,255,0.2)'
                }}
              >
                <div style={{fontSize: '4rem', marginBottom: '1rem'}}>{tutor.emoji}</div>
                <div style={{
                  width: '80px',
                  height: '80px',
                  borderRadius: '50%',
                  background: tutor.color,
                  margin: '0 auto 1rem auto',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '2rem'
                }}>🤖</div>
                
                <h3 style={{...styles.title, fontSize: '1.5rem', marginBottom: '0.5rem'}}>{tutor.name}</h3>
                <p style={{color: '#6B7280', fontWeight: 'bold', marginBottom: '1rem'}}>{tutor.language}</p>
                
                {/* Language options */}
                <div style={{marginBottom: '1rem'}}>
                  <p style={{fontSize: '0.9rem', color: '#6B7280', marginBottom: '0.5rem'}}>Available Languages:</p>
                  <div style={{display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0.5rem'}}>
                    {languageConfig[key].languages.map(lang => (
                      <span key={lang} style={{
                        background: tutor.accentColor,
                        color: tutor.color,
                        padding: '0.25rem 0.5rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.8rem',
                        fontWeight: 'bold'
                      }}>
                        {lang}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Voice preview */}
                {voiceSupported && (
                  <button
                    style={{
                      background: tutor.accentColor,
                      color: tutor.color,
                      border: `2px solid ${tutor.color}`,
                      padding: '0.5rem 1rem',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      marginBottom: '1rem',
                      fontWeight: 'bold'
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      speakText(tutor.greeting, key);
                    }}
                  >
                    🔊 Voice Preview
                  </button>
                )}
                
                <button 
                  style={{...styles.button, background: tutor.color}}
                  onClick={() => {
                    setSelectedTutor(key);
                    setCurrentLanguage(languageConfig[key].defaultLang);
                    setCurrentPage('main');
                    setConversations([{
                      type: 'ai',
                      content: tutor.greeting,
                      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                      tutor: tutor.name
                    }]);
                  }}
                >
                  Select {tutor.name}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Main Chat with advanced voice features
  const currentTutor = tutors[selectedTutor];
  return (
    <div style={{minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '1rem'}}>
      <style>
        {`
          @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
          }
        `}
      </style>
      
      <div style={{maxWidth: '1400px', margin: '0 auto'}}>
        {/* Header with voice status */}
        <div style={{
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '1rem',
          padding: '1rem',
          marginBottom: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
            <div style={{
              width: '50px',
              height: '50px',
              borderRadius: '50%',
              background: currentTutor.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              position: 'relative'
            }}>
              🤖
              {isSpeaking && (
                <div style={{
                  position: 'absolute',
                  top: '-2px',
                  right: '-2px',
                  width: '15px',
                  height: '15px',
                  background: '#10B981',
                  borderRadius: '50%',
                  animation: 'pulse 1s infinite'
                }}>🔊</div>
              )}
            </div>
            <div>
              <h1 style={{color: 'white', margin: 0, fontSize: '1.5rem'}}>
                Learning with {currentTutor.name} {isSpeaking ? '🔊' : ''}
              </h1>
              <p style={{color: 'rgba(255,255,255,0.8)', margin: 0}}>
                {currentTutor.language} • {currentLanguage}
              </p>
            </div>
          </div>
          
          <div style={{display: 'flex', gap: '0.5rem'}}>
            <button
              style={{background: 'rgba(255,255,255,0.2)', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.5rem', border: 'none', cursor: 'pointer'}}
              onClick={() => setCurrentPage('tutor-selection')}
            >
              🔄 Change Tutor
            </button>
          </div>
        </div>

        <div style={{display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem'}}>
          {/* Chat Section */}
          <div style={styles.card}>
            <h2 style={{fontSize: '1.3rem', textAlign: 'left', marginBottom: '1rem', color: '#1F2937'}}>
              💬 Voice Conversation
            </h2>
            
            {/* Language Selector */}
            <div style={{marginBottom: '1rem', textAlign: 'left'}}>
              <label style={{fontSize: '0.9rem', color: '#6B7280', marginBottom: '0.5rem', display: 'block'}}>
                🌍 Speaking Language:
              </label>
              <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
                {languageConfig[selectedTutor].languages.map(lang => (
                  <button
                    key={lang}
                    style={{
                      ...styles.languageSelector,
                      background: currentLanguage === lang ? currentTutor.color : '#F3F4F6',
                      color: currentLanguage === lang ? 'white' : '#1F2937',
                      border: currentLanguage === lang ? 'none' : '1px solid #D1D5DB'
                    }}
                    onClick={() => switchLanguage(lang)}
                  >
                    {lang}
                  </button>
                ))}
              </div>
            </div>
            
            <div style={{maxHeight: '300px', overflowY: 'auto', marginBottom: '1rem'}}>
              {conversations.length === 0 ? (
                <div style={{textAlign: 'center', color: '#6B7280', padding: '2rem'}}>
                  <div style={{fontSize: '3rem', marginBottom: '0.5rem'}}>🎤</div>
                  <p>Start a voice conversation with {currentTutor.name}!</p>
                </div>
              ) : (
                conversations.map((msg, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      maxWidth: '80%',
                      padding: '0.75rem 1rem',
                      borderRadius: '1rem',
                      background: msg.type === 'user' ? '#4ECDC4' : currentTutor.color,
                      color: 'white'
                    }}>
                      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.25rem'}}>
                        <span style={{fontWeight: 'bold', fontSize: '0.8rem'}}>
                          {msg.type === 'user' ? 'You' : msg.tutor}
                        </span>
                        {msg.isVoiceMessage && <span style={{fontSize: '0.8rem'}}>🎤</span>}
                        {msg.language && (
                          <span style={{fontSize: '0.7rem', opacity: 0.8}}>
                            {msg.language}
                          </span>
                        )}
                      </div>
                      
                      <div style={{marginBottom: '0.5rem'}}>{msg.content}</div>
                      
                      {/* Voice Analysis Display */}
                      {msg.voiceAnalysis && (
                        <div style={{background: 'rgba(255,255,255,0.2)', padding: '0.5rem', borderRadius: '0.5rem', fontSize: '0.8rem'}}>
                          <div style={{marginBottom: '0.25rem'}}>📊 Voice Analysis:</div>
                          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.25rem'}}>
                            <div>Pronunciation: {msg.voiceAnalysis.pronunciation}%</div>
                            <div>Confidence: {msg.voiceAnalysis.confidence}%</div>
                            <div>Clarity: {msg.voiceAnalysis.clarity}%</div>
                            <div>Accent: {msg.voiceAnalysis.accentSimilarity}%</div>
                          </div>
                        </div>
                      )}
                      
                      {msg.fluencyScore && (
                        <div style={{fontSize: '0.7rem', opacity: 0.8, marginTop: '0.25rem'}}>
                          Overall Score: {msg.fluencyScore}/100
                        </div>
                      )}
                      
                      {msg.voiceFeedback && (
                        <div style={{fontSize: '0.7rem', opacity: 0.9, marginTop: '0.25rem', fontStyle: 'italic'}}>
                          💡 {msg.voiceFeedback}
                        </div>
                      )}
                      
                      <div style={{fontSize: '0.7rem', opacity: 0.7, marginTop: '0.25rem'}}>
                        {msg.timestamp}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Voice Input Section */}
            <div style={{border: '2px solid #E5E7EB', borderRadius: '1rem', padding: '1rem', background: '#F9FAFB'}}>
              <h4 style={{margin: '0 0 0.5rem 0', color: '#1F2937'}}>🎤 Voice Input</h4>
              
              {/* Recording Controls */}
              <div style={{display: 'flex', gap: '0.5rem', marginBottom: '1rem', alignItems: 'center'}}>
                {!isRecording ? (
                  <button
                    style={styles.recordingButton}
                    onClick={startRecording}
                    disabled={!voiceSupported}
                  >
                    🎤 Start Recording
                  </button>
                ) : (
                  <button
                    style={styles.recordingButton}
                    onClick={stopRecording}
                  >
                    ⏹️ Stop Recording
                  </button>
                )}
                
                {isRecording && (
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.25rem'}}>
                    <div style={{color: '#EF4444', fontWeight: 'bold'}}>Recording...</div>
                    <div style={{display: 'flex', gap: '2px'}}>
                      {[1,2,3,4].map(i => (
                        <div key={i} style={{
                          width: '4px',
                          height: `${Math.random() * 20 + 10}px`,
                          background: '#EF4444',
                          borderRadius: '2px',
                          animation: 'pulse 0.5s infinite'
                        }}></div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Voice Analysis Preview */}
              {voiceAnalysis && (
                <div style={{background: '#EFF6FF', padding: '0.75rem', borderRadius: '0.5rem', marginBottom: '1rem'}}>
                  <h5 style={{margin: '0 0 0.5rem 0', color: '#1E40AF'}}>📊 Live Analysis</h5>
                  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.9rem'}}>
                    <div style={styles.voiceMetric}>
                      <span>Pronunciation:</span>
                      <span style={{fontWeight: 'bold', color: voiceAnalysis.pronunciation > 80 ? '#10B981' : '#F59E0B'}}>
                        {voiceAnalysis.pronunciation}%
                      </span>
                    </div>
                    <div style={styles.voiceMetric}>
                      <span>Confidence:</span>
                      <span style={{fontWeight: 'bold', color: voiceAnalysis.confidence > 75 ? '#10B981' : '#F59E0B'}}>
                        {voiceAnalysis.confidence}%
                      </span>
                    </div>
                    <div style={styles.voiceMetric}>
                      <span>Clarity:</span>
                      <span style={{fontWeight: 'bold', color: voiceAnalysis.clarity > 80 ? '#10B981' : '#F59E0B'}}>
                        {voiceAnalysis.clarity}%
                      </span>
                    </div>
                    <div style={styles.voiceMetric}>
                      <span>Accent Match:</span>
                      <span style={{fontWeight: 'bold', color: voiceAnalysis.accentSimilarity > 75 ? '#10B981' : '#F59E0B'}}>
                        {voiceAnalysis.accentSimilarity}%
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Text Input */}
              <div style={{display: 'flex', gap: '0.5rem'}}>
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputMessage, !!voiceAnalysis)}
                  placeholder={`Type or speak to ${currentTutor.name} in ${currentLanguage}...`}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    border: '2px solid #E5E7EB',
                    borderRadius: '0.75rem',
                    fontSize: '1rem',
                    outline: 'none'
                  }}
                  disabled={isLoading}
                />
                <button
                  onClick={() => handleSendMessage(inputMessage, !!voiceAnalysis)}
                  disabled={isLoading || !inputMessage.trim()}
                  style={{
                    background: 'linear-gradient(45deg, #4F46E5, #7C3AED)',
                    color: 'white',
                    padding: '0.75rem 1.5rem',
                    borderRadius: '0.75rem',
                    border: 'none',
                    cursor: 'pointer',
                    opacity: isLoading || !inputMessage.trim() ? 0.5 : 1
                  }}
                >
                  {isLoading ? '⏳' : voiceAnalysis ? '🎤📤' : '📤'}
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar with tutor info and challenges */}
          <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
            {/* Tutor Avatar */}
            <div style={styles.card}>
              <h3 style={{fontSize: '1.2rem', marginBottom: '1rem', color: '#1F2937'}}>🤖 Your Voice Tutor</h3>
              
              <div style={{textAlign: 'center'}}>
                <div style={{
                  width: '100px',
                  height: '100px',
                  borderRadius: '50%',
                  background: currentTutor.color,
                  margin: '0 auto 1rem auto',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '3rem',
                  position: 'relative'
                }}>
                  🤖
                  {isSpeaking && (
                    <div style={{
                      position: 'absolute',
                      top: '5px',
                      right: '5px',
                      width: '20px',
                      height: '20px',
                      background: '#10B981',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.8rem',
                      animation: 'pulse 1s infinite'
                    }}>🔊</div>
                  )}
                </div>
                
                <h4 style={{fontSize: '1.3rem', fontWeight: 'bold', margin: '0 0 0.5rem 0'}}>{currentTutor.name}</h4>
                <p style={{color: '#6B7280', margin: '0 0 0.5rem 0'}}>{currentTutor.language}</p>
                <p style={{color: '#6B7280', fontSize: '0.9rem', margin: '0 0 1rem 0'}}>
                  Target: {languageConfig[selectedTutor].accent}
                </p>
                
                <div style={{
                  background: currentTutor.accentColor,
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  marginBottom: '1rem'
                }}>
                  <span style={{fontSize: '0.9rem', fontWeight: 'bold', color: currentTutor.color}}>
                    {isSpeaking ? '🗣️ Speaking...' : '✅ Ready for voice chat!'}
                  </span>
                </div>

                {voiceSupported && (
                  <button
                    style={{
                      background: currentTutor.color,
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      marginBottom: '1rem',
                      width: '100%'
                    }}
                    onClick={() => speakText(currentTutor.greeting, selectedTutor)}
                  >
                    🔊 Test Voice
                  </button>
                )}
              </div>
            </div>

            {/* Voice Challenges */}
            <div style={styles.card}>
              <h3 style={{fontSize: '1.2rem', marginBottom: '1rem', color: '#1F2937'}}>🏆 Voice Challenges</h3>
              
              <div style={{textAlign: 'left', fontSize: '0.9rem'}}>
                <div style={{marginBottom: '0.75rem'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem'}}>
                    <span>🎯 Pronunciation Master</span>
                    <span style={{fontWeight: 'bold', color: voiceChallenges.pronunciationChallenge >= 90 ? '#10B981' : '#F59E0B'}}>
                      {voiceChallenges.pronunciationChallenge}%
                    </span>
                  </div>
                  <div style={{background: '#E5E7EB', borderRadius: '0.25rem', height: '0.5rem'}}>
                    <div style={{
                      background: voiceChallenges.pronunciationChallenge >= 90 ? '#10B981' : '#F59E0B',
                      width: `${voiceChallenges.pronunciationChallenge}%`,
                      height: '100%',
                      borderRadius: '0.25rem',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                  <p style={{fontSize: '0.8rem', color: '#6B7280', margin: '0.25rem 0 0 0'}}>Target: 90%+</p>
                </div>

                <div style={{marginBottom: '0.75rem'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem'}}>
                    <span>🌍 Multi-Language</span>
                    <span style={{fontWeight: 'bold', color: voiceChallenges.multiLanguageMaster >= 100 ? '#10B981' : '#F59E0B'}}>
                      {voiceChallenges.multiLanguageMaster}
                    </span>
                  </div>
                  <div style={{background: '#E5E7EB', borderRadius: '0.25rem', height: '0.5rem'}}>
                    <div style={{
                      background: voiceChallenges.multiLanguageMaster >= 100 ? '#10B981' : '#F59E0B',
                      width: `${Math.min(100, voiceChallenges.multiLanguageMaster)}%`,
                      height: '100%',
                      borderRadius: '0.25rem',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                  <p style={{fontSize: '0.8rem', color: '#6B7280', margin: '0.25rem 0 0 0'}}>Target: 100 points</p>
                </div>

                <div style={{marginBottom: '0.75rem'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem'}}>
                    <span>⭐ Fluency Expert</span>
                    <span style={{fontWeight: 'bold', color: voiceChallenges.voiceFluencyExpert >= 95 ? '#10B981' : '#F59E0B'}}>
                      {voiceChallenges.voiceFluencyExpert}%
                    </span>
                  </div>
                  <div style={{background: '#E5E7EB', borderRadius: '0.25rem', height: '0.5rem'}}>
                    <div style={{
                      background: voiceChallenges.voiceFluencyExpert >= 95 ? '#10B981' : '#F59E0B',
                      width: `${voiceChallenges.voiceFluencyExpert}%`,
                      height: '100%',
                      borderRadius: '0.25rem',
                      transition: 'width 0.3s ease'
                    }}></div>
                  </div>
                  <p style={{fontSize: '0.8rem', color: '#6B7280', margin: '0.25rem 0 0 0'}}>Target: 95%+</p>
                </div>
              </div>
            </div>

            {/* Session Stats */}
            <div style={styles.card}>
              <h3 style={{fontSize: '1.2rem', marginBottom: '1rem', color: '#1F2937'}}>📊 Session Stats</h3>
              
              <div style={{textAlign: 'left'}}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
                  <span>Messages:</span>
                  <span style={{fontWeight: 'bold'}}>{conversations.length}</span>
                </div>
                
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
                  <span>Voice Messages:</span>
                  <span style={{fontWeight: 'bold'}}>
                    {conversations.filter(msg => msg.isVoiceMessage).length}
                  </span>
                </div>
                
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
                  <span>Language:</span>
                  <span style={{fontWeight: 'bold'}}>{currentLanguage}</span>
                </div>

                {pronunciationScore > 0 && (
                  <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
                    <span>Last Score:</span>
                    <span style={{fontWeight: 'bold', color: pronunciationScore > 80 ? '#10B981' : '#F59E0B'}}>
                      {pronunciationScore}/100
                    </span>
                  </div>
                )}
              </div>

              <button
                onClick={() => {
                  setIsAuthenticated(false);
                  setCurrentPage('login');
                  setConversations([]);
                  setVoiceChallenges({ pronunciationChallenge: 0, multiLanguageMaster: 0, voiceFluencyExpert: 0 });
                }}
                style={{
                  width: '100%',
                  background: '#6B7280',
                  color: 'white',
                  border: 'none',
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  marginTop: '1rem'
                }}
              >
                🚪 End Session
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
