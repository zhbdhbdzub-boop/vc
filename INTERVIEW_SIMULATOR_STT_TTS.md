# Interview Simulator - STT/TTS Integration

## What's Fixed

### 1. Real API Integration ✅
- **Before**: Mock responses (same answer every time)
- **After**: Connected to backend `/api/interviews/simulator/` endpoints
- **Result**: Each AI response is unique and contextual based on your answers

### 2. Speech-to-Text (STT) ✅
- **Feature**: Click "Record Answer" to speak your response
- **Technology**: Web Speech API (webkitSpeechRecognition)
- **Usage**:
  1. Click the 🎤 **Record Answer** button
  2. Speak your response (you'll see "● Listening..." indicator)
  3. Your speech is automatically converted to text in the input field
  4. Click "Send Response" to submit

### 3. Text-to-Speech (TTS) ✅
- **Feature**: AI interviewer speaks questions out loud
- **Technology**: Web Speech Synthesis API
- **Usage**:
  - **Auto-speak**: Questions are spoken automatically (default ON)
  - **Manual control**: Click 🔊 speaker icon on any message to replay it
  - **Toggle**: Use "Audio On/Off" button in header to enable/disable auto-speak
  - **Visual feedback**: "🔊 AI is speaking..." indicator while audio plays

## New UI Features

### Real-time Indicators
- **Loading states**: "Starting...", "AI is thinking...", "Sending..."
- **Recording indicator**: Red pulsing dot "● Listening..." when mic is active
- **Speaking indicator**: "🔊 AI is speaking..." in header
- **Confidence scores**: Shows your response confidence percentage

### Smart Controls
- **Audio On/Off**: Toggle auto-speak for AI responses
- **Speaker icon**: Replay any AI message manually
- **Disabled states**: Buttons disable during loading to prevent duplicate submissions
- **Auto-scroll**: Messages automatically scroll to show latest conversation

## How It Works

### Start Interview Flow
```
1. Enter job role (e.g., "Software Engineer") 
2. Optional: Enter company name (e.g., "Kpit")
3. Click "Start Interview"
4. Backend creates session, generates personalized opening
5. AI speaks opening question (if audio enabled)
```

### Conversation Flow
```
1. Type response OR click "Record Answer" to speak
2. Click "Send Response"
3. Your response is analyzed (sentiment, confidence, keywords)
4. AI generates contextual follow-up question (Llama 3.1 or GPT-4)
5. AI speaks the question (if audio enabled)
6. Repeat until ready to end
```

### End Interview
```
1. Click "End Interview"
2. Backend analyzes full conversation
3. Get comprehensive feedback with scores:
   - Overall Score
   - Technical Skills
   - Communication
   - Confidence
   - Problem Solving
```

## Browser Compatibility

### Speech Recognition (STT)
- ✅ Chrome/Edge (Desktop & Android)
- ✅ Safari (iOS 14.5+)
- ❌ Firefox (not supported yet)

### Speech Synthesis (TTS)
- ✅ All modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Works on mobile and desktop

## Technical Stack

### Frontend
- React + TypeScript
- Web Speech API (native browser APIs)
- Real-time state management with React hooks

### Backend
- Django REST Framework
- OpenAI GPT-4 (sentiment analysis)
- Ollama Llama 3.1 (conversation generation)
- PostgreSQL (conversation history)

## API Endpoints Used

```
POST /api/interviews/simulator/start/
POST /api/interviews/simulator/{id}/respond/
POST /api/interviews/simulator/{id}/end/
GET  /api/interviews/simulator/{id}/transcript/
GET  /api/interviews/simulator/{id}/messages/
```

## Testing Tips

1. **Test STT**: Use Chrome/Edge for best results
2. **Test TTS**: Ensure browser volume is not muted
3. **Test conversation**: Try different job roles to see unique questions
4. **Test scoring**: Complete full interview to see comprehensive feedback

## Pricing
- **24.99 TND per session**
- **1 FREE session included** for first-time users

## Next Steps (Optional Enhancements)

- [ ] Add video recording with facial expression analysis
- [ ] Add WebRTC for live audio streaming
- [ ] Add multilingual support (French, Arabic)
- [ ] Add interview templates (Technical, Behavioral, HR)
- [ ] Add practice mode vs. evaluation mode
- [ ] Add interview history dashboard with analytics
