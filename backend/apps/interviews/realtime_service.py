"""
Real-time Interview Simulation Service
Handles video-based AI interview with conversation
"""
import logging
import json
import requests
from typing import Dict, List, Any
from django.conf import settings
from django.utils import timezone
from django.db import models
from openai import OpenAI
from .models import InterviewSession, ConversationMessage

logger = logging.getLogger(__name__)

# Initialize clients
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY) if hasattr(settings, 'OPENAI_API_KEY') else None
OLLAMA_API_URL = getattr(settings, 'OLLAMA_API_URL', 'http://ollama:11434')


class RealTimeInterviewService:
    """Service for managing real-time interview simulations"""
    
    def __init__(self, session: InterviewSession):
        self.session = session
        self.conversation_history = []
        
    def start_session(self) -> Dict[str, Any]:
        """
        Start a new interview session
        
        Returns:
            Initial session data with first question
        """
        self.session.status = 'in_progress'
        self.session.started_at = timezone.now()
        self.session.save()
        
        # Generate opening message
        opening_message = self._generate_opening_message()
        
        # Save to conversation
        ConversationMessage.objects.create(
            session=self.session,
            role='interviewer',
            content=opening_message,
            timestamp_seconds=0
        )
        
        return {
            'session_id': str(self.session.id),
            'message': opening_message,
            'status': 'started'
        }
    
    def _generate_opening_message(self) -> str:
        """Generate personalized opening message"""
        job_role = self.session.job_role or "this position"
        company = self.session.company_name or "our company"
        
        return f"""Hello! Welcome to your interview simulation for the {job_role} role at {company}. 

I'm your AI interviewer, and I'll be asking you a series of questions to assess your skills and fit for this position. This is a safe environment to practice, so feel free to take your time with your answers.

Let's begin. Can you start by telling me a bit about yourself and why you're interested in this {job_role} position?"""
    
    def process_candidate_response(
        self,
        response_text: str,
        audio_url: str = None,
        timestamp: float = 0
    ) -> Dict[str, Any]:
        """
        Process candidate's response and generate next question
        
        Args:
            response_text: Transcribed text of candidate's answer
            audio_url: URL to audio recording (optional)
            timestamp: Time in seconds from session start
            
        Returns:
            AI interviewer's next question/response
        """
        # Save candidate response
        candidate_msg = ConversationMessage.objects.create(
            session=self.session,
            role='candidate',
            content=response_text,
            audio_url=audio_url or '',
            timestamp_seconds=timestamp
        )
        
        # Analyze response sentiment and quality
        analysis = self._analyze_response(response_text)
        candidate_msg.sentiment = analysis.get('sentiment', 'neutral')
        candidate_msg.confidence_score = analysis.get('confidence', 50)
        candidate_msg.keywords_detected = analysis.get('keywords', [])
        candidate_msg.save()
        
        # Generate follow-up question
        next_question = self._generate_next_question(response_text)
        
        # Save interviewer response
        interviewer_msg = ConversationMessage.objects.create(
            session=self.session,
            role='interviewer',
            content=next_question,
            timestamp_seconds=timestamp + 5  # Small delay
        )
        
        return {
            'question': next_question,
            'analysis': analysis,
            'message_id': str(interviewer_msg.id)
        }
    
    def _analyze_response(self, response_text: str) -> Dict[str, Any]:
        """
        Analyze candidate's response using AI
        
        Returns:
            sentiment, confidence score, keywords
        """
        if not openai_client:
            return {
                'sentiment': 'neutral',
                'confidence': 50,
                'keywords': []
            }
        
        try:
            prompt = f"""Analyze this interview response and provide:
1. sentiment: positive, neutral, or negative
2. confidence: 0-100 (how confident the answer sounds)
3. keywords: 3-5 key technical terms or skills mentioned

Response: "{response_text}"

Format as JSON."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an interview analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing response: {e}")
            return {'sentiment': 'neutral', 'confidence': 50, 'keywords': []}
    
    def _generate_next_question(self, previous_response: str) -> str:
        """
        Generate contextual follow-up question using AI
        
        Args:
            previous_response: Candidate's last answer
            
        Returns:
            Next interview question
        """
        # Get conversation context
        messages = ConversationMessage.objects.filter(
            session=self.session
        ).order_by('timestamp_seconds')
        
        conversation_context = "\n".join([
            f"{msg.role}: {msg.content}" for msg in messages
        ])
        
        job_role = self.session.job_role or "the position"
        
        # Try Llama via Ollama first (faster, free)
        try:
            ollama_response = requests.post(
                f"{OLLAMA_API_URL}/api/generate",
                json={
                    "model": "llama3.1",
                    "prompt": f"""You are conducting a job interview for a {job_role} position.

Previous conversation:
{conversation_context}

Generate the next natural interview question based on the candidate's last response. Keep it professional, relevant, and conversational. If they mentioned something interesting, ask a follow-up. Otherwise, move to a new topic.

Just provide the question, nothing else.""",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": 200
                    }
                },
                timeout=30
            )
            
            if ollama_response.status_code == 200:
                result = ollama_response.json()
                question = result.get('response', '').strip()
                if question:
                    logger.info("Generated question using Llama 3.1")
                    return question
                    
        except Exception as e:
            logger.warning(f"Ollama unavailable, falling back to GPT-4: {e}")
        
        # Fallback to GPT-4
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"You are an interviewer for a {job_role} position. Ask relevant follow-up questions based on the conversation."},
                        {"role": "user", "content": f"Previous conversation:\n{conversation_context}\n\nGenerate the next question:"}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
                
                question = response.choices[0].message.content.strip()
                logger.info("Generated question using GPT-4")
                return question
                
            except Exception as e:
                logger.error(f"Error generating question with GPT-4: {e}")
        
        # Final fallback to generic questions
        return self._get_fallback_question()
    
    def _get_fallback_question(self) -> str:
        """Generic fallback questions when AI is unavailable"""
        fallback_questions = [
            "Can you describe a challenging project you worked on and how you approached it?",
            "What are your strongest technical skills, and how have you applied them?",
            "Tell me about a time you had to learn something new quickly. How did you handle it?",
            "How do you prioritize tasks when working on multiple projects?",
            "What interests you most about this role and our company?",
            "Where do you see yourself professionally in the next few years?",
        ]
        
        # Get count of questions asked
        question_count = ConversationMessage.objects.filter(
            session=self.session,
            role='interviewer'
        ).count()
        
        if question_count < len(fallback_questions):
            return fallback_questions[question_count]
        else:
            return "Thank you for your responses. Do you have any questions for me about the role or company?"
    
    def end_session(self) -> Dict[str, Any]:
        """
        End the interview session and generate final feedback
        
        Returns:
            Session summary and scores
        """
        self.session.status = 'completed'
        self.session.completed_at = timezone.now()
        
        # Calculate duration
        if self.session.started_at:
            duration = (self.session.completed_at - self.session.started_at).total_seconds()
            self.session.duration_seconds = int(duration)
        
        # Generate comprehensive feedback
        feedback = self._generate_session_feedback()
        
        self.session.overall_score = feedback['overall_score']
        self.session.technical_score = feedback['technical_score']
        self.session.communication_score = feedback['communication_score']
        self.session.confidence_score = feedback['confidence_score']
        self.session.overall_feedback = feedback['summary']
        self.session.strengths = feedback['strengths']
        self.session.areas_for_improvement = feedback['weaknesses']
        self.session.recommendations = feedback['recommendations']
        
        self.session.save()
        
        return {
            'session_id': str(self.session.id),
            'status': 'completed',
            'duration_seconds': self.session.duration_seconds,
            'scores': {
                'overall': self.session.overall_score,
                'technical': self.session.technical_score,
                'communication': self.session.communication_score,
                'confidence': self.session.confidence_score,
            },
            'feedback': feedback
        }
    
    def _generate_session_feedback(self) -> Dict[str, Any]:
        """Generate comprehensive feedback for the entire session"""
        # Get all conversation messages
        messages = ConversationMessage.objects.filter(
            session=self.session,
            role='candidate'
        )
        
        if not messages.exists():
            return {
                'overall_score': 0,
                'technical_score': 0,
                'communication_score': 0,
                'confidence_score': 0,
                'summary': 'No responses provided',
                'strengths': [],
                'weaknesses': ['Did not complete interview'],
                'recommendations': ['Try completing a full practice session']
            }
        
        # Collect responses
        responses = [msg.content for msg in messages]
        full_transcript = "\n\n".join([
            f"Q: {self.session.conversation_messages.filter(role='interviewer')[i].content}\nA: {resp}"
            for i, resp in enumerate(responses) if i < self.session.conversation_messages.filter(role='interviewer').count()
        ])
        
        # Calculate average confidence
        avg_confidence = messages.aggregate(models.Avg('confidence_score'))['confidence_score__avg'] or 50
        
        if not openai_client:
            # Basic scoring without AI
            return {
                'overall_score': int(avg_confidence),
                'technical_score': int(avg_confidence * 0.9),
                'communication_score': int(avg_confidence * 1.1),
                'confidence_score': int(avg_confidence),
                'summary': f'Completed {messages.count()} responses with good engagement.',
                'strengths': ['Completed the interview', 'Provided responses'],
                'weaknesses': ['Consider more detailed answers'],
                'recommendations': ['Practice more technical questions']
            }
        
        try:
            prompt = f"""Analyze this complete interview transcript and provide detailed feedback:

{full_transcript}

Provide a JSON response with:
1. overall_score: 0-100
2. technical_score: 0-100 (technical knowledge and skills)
3. communication_score: 0-100 (clarity, articulation)
4. confidence_score: 0-100 (confidence and presence)
5. problem_solving_score: 0-100
6. summary: 2-3 sentences overall assessment
7. strengths: Array of 3-5 specific strengths
8. weaknesses: Array of 3-4 areas to improve
9. recommendations: Array of 3-5 actionable next steps"""
            
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interview coach providing constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            feedback = json.loads(response.choices[0].message.content)
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating session feedback: {e}")
            return {
                'overall_score': int(avg_confidence),
                'technical_score': int(avg_confidence),
                'communication_score': int(avg_confidence),
                'confidence_score': int(avg_confidence),
                'problem_solving_score': int(avg_confidence),
                'summary': 'Feedback generation temporarily unavailable',
                'strengths': ['Completed interview'],
                'weaknesses': ['Try again for detailed feedback'],
                'recommendations': ['Practice more interviews']
            }
    
    def get_transcript(self) -> List[Dict[str, Any]]:
        """Get full conversation transcript"""
        messages = ConversationMessage.objects.filter(
            session=self.session
        ).order_by('timestamp_seconds')
        
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp_seconds,
                'sentiment': msg.sentiment,
                'confidence': msg.confidence_score
            }
            for msg in messages
        ]
