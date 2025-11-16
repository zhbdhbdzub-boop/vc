"""
Interview simulation services with OpenAI integration
"""
import logging
import json
from typing import Dict, List, Any
from django.conf import settings
from django.utils import timezone
from openai import OpenAI
from .models import (
    InterviewTemplate, InterviewSession, Question, SessionQuestion,
    InterviewFeedback, PracticeArea
)

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY) if hasattr(settings, 'OPENAI_API_KEY') else None


class QuestionGenerator:
    """Generate interview questions using OpenAI"""
    
    @staticmethod
    def generate_questions(
        template: InterviewTemplate,
        count: int = 10
    ) -> List[Question]:
        """
        Generate interview questions based on template
        
        Args:
            template: InterviewTemplate instance
            count: Number of questions to generate
        
        Returns:
            List of Question instances
        """
        if not client:
            logger.warning("OpenAI not configured, using fallback questions")
            return QuestionGenerator._get_fallback_questions(template, count)
        
        try:
            prompt = f"""Generate {count} {template.interview_type} interview questions for a {template.job_role} position at {template.difficulty} difficulty level.

For each question, provide:
1. question_text: The actual question
2. question_type: one of [multiple_choice, open_ended, coding, behavioral, system_design]
3. difficulty: {template.difficulty}
4. context: Any necessary background (optional)
5. ideal_answer: Expected answer or key points
6. evaluation_criteria: List of criteria to evaluate the answer

Format as JSON array of objects.
"""
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            questions_data = json.loads(response.choices[0].message.content)
            questions = []
            
            for i, q_data in enumerate(questions_data.get('questions', [])[:count]):
                question = Question.objects.create(
                    template=template,
                    question_type=q_data.get('question_type', 'open_ended'),
                    difficulty=q_data.get('difficulty', template.difficulty),
                    question_text=q_data.get('question_text', ''),
                    context=q_data.get('context', ''),
                    ideal_answer=q_data.get('ideal_answer', ''),
                    evaluation_criteria=q_data.get('evaluation_criteria', []),
                    time_limit_seconds=template.duration_minutes * 60 // count
                )
                questions.append(question)
            
            logger.info(f"Generated {len(questions)} questions for template {template.id}")
            return questions
        
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return QuestionGenerator._get_fallback_questions(template, count)
    
    @staticmethod
    def _get_fallback_questions(template: InterviewTemplate, count: int) -> List[Question]:
        """Fallback questions when OpenAI is unavailable"""
        fallback_questions = [
            {
                'question_text': 'Tell me about yourself and your experience.',
                'question_type': 'behavioral',
                'ideal_answer': 'Should include background, relevant experience, and career goals.',
            },
            {
                'question_text': 'What are your greatest strengths?',
                'question_type': 'behavioral',
                'ideal_answer': 'Should provide specific examples demonstrating strengths.',
            },
            {
                'question_text': 'Describe a challenging problem you solved recently.',
                'question_type': 'behavioral',
                'ideal_answer': 'Should follow STAR method: Situation, Task, Action, Result.',
            },
        ]
        
        questions = []
        for i, q_data in enumerate(fallback_questions[:count]):
            question = Question.objects.create(
                template=template,
                question_type=q_data['question_type'],
                difficulty=template.difficulty,
                question_text=q_data['question_text'],
                ideal_answer=q_data['ideal_answer'],
                time_limit_seconds=300
            )
            questions.append(question)
        
        return questions


class AnswerEvaluator:
    """Evaluate interview answers using OpenAI"""
    
    @staticmethod
    def evaluate_answer(
        session_question: SessionQuestion
    ) -> Dict[str, Any]:
        """
        Evaluate user's answer to a question
        
        Args:
            session_question: SessionQuestion instance
        
        Returns:
            Dict with score, feedback, and analysis
        """
        question = session_question.question
        user_answer = session_question.user_answer
        
        if not client or not user_answer:
            return {
                'score': 0,
                'is_correct': False,
                'feedback': 'No answer provided',
                'sentiment': 'neutral',
                'confidence_level': 0
            }
        
        try:
            prompt = f"""Evaluate this interview answer:

Question: {question.question_text}
Question Type: {question.question_type}
Difficulty: {question.difficulty}

Ideal Answer: {question.ideal_answer}
Evaluation Criteria: {json.dumps(question.evaluation_criteria)}

User's Answer: {user_answer}

Provide:
1. score: 0-100
2. is_correct: true/false
3. feedback: Detailed feedback (2-3 sentences)
4. strengths: What was good about the answer
5. areas_for_improvement: What could be better
6. sentiment: positive, neutral, or negative
7. confidence_level: 0-100 (how confident the candidate seems)

Format as JSON.
"""
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert interview evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            
            # Update session question
            session_question.score = evaluation.get('score', 0)
            session_question.is_correct = evaluation.get('is_correct', False)
            session_question.ai_evaluation = evaluation.get('feedback', '')
            session_question.sentiment = evaluation.get('sentiment', 'neutral')
            session_question.confidence_level = evaluation.get('confidence_level', 50)
            session_question.save()
            
            return evaluation
        
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            return {
                'score': 50,
                'is_correct': False,
                'feedback': 'Unable to evaluate answer automatically',
                'sentiment': 'neutral',
                'confidence_level': 50
            }


class SessionManager:
    """Manage interview sessions"""
    
    @staticmethod
    def start_session(
        user,
        tenant,
        template: InterviewTemplate
    ) -> InterviewSession:
        """
        Create and start a new interview session
        
        Args:
            user: User instance
            tenant: Tenant instance
            template: InterviewTemplate instance
        
        Returns:
            InterviewSession instance
        """
        # Create session
        session = InterviewSession.objects.create(
            tenant=tenant,
            user=user,
            template=template,
            title=f"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Get or generate questions
        questions = list(template.questions.all()[:template.question_count])
        
        if len(questions) < template.question_count:
            # Generate additional questions if needed
            new_questions = QuestionGenerator.generate_questions(
                template,
                template.question_count - len(questions)
            )
            questions.extend(new_questions)
        
        # Create session questions
        for i, question in enumerate(questions):
            SessionQuestion.objects.create(
                session=session,
                question=question,
                order=i + 1
            )
        
        # Update template usage
        template.usage_count += 1
        template.save()
        
        logger.info(f"Started session {session.id} with {len(questions)} questions")
        return session
    
    @staticmethod
    def complete_session(session: InterviewSession):
        """
        Complete a session and generate feedback
        
        Args:
            session: InterviewSession instance
        """
        session.status = 'completed'
        session.completed_at = timezone.now()
        
        if session.started_at:
            duration = (session.completed_at - session.started_at).total_seconds()
            session.duration_seconds = int(duration)
        
        # Calculate scores
        session_questions = session.session_questions.all()
        if session_questions:
            # Overall score
            total_score = sum(sq.score for sq in session_questions)
            session.overall_score = int(total_score / len(session_questions))
            
            # Calculate component scores
            technical_qs = [sq for sq in session_questions if sq.question.question_type in ['coding', 'technical', 'system_design']]
            if technical_qs:
                session.technical_score = int(sum(sq.score for sq in technical_qs) / len(technical_qs))
            
            # Communication score (based on open-ended and behavioral)
            comm_qs = [sq for sq in session_questions if sq.question.question_type in ['open_ended', 'behavioral']]
            if comm_qs:
                session.communication_score = int(sum(sq.score for sq in comm_qs) / len(comm_qs))
            
            # Confidence score (average of confidence levels)
            confidence_levels = [sq.confidence_level for sq in session_questions if sq.confidence_level > 0]
            if confidence_levels:
                session.confidence_score = int(sum(confidence_levels) / len(confidence_levels))
        
        session.save()
        
        # Generate detailed feedback
        FeedbackGenerator.generate_feedback(session)
        
        # Update practice areas
        SessionManager._update_practice_areas(session)
        
        logger.info(f"Completed session {session.id} with score {session.overall_score}")
    
    @staticmethod
    def _update_practice_areas(session: InterviewSession):
        """Update user's practice area statistics"""
        user = session.user
        tenant = session.tenant
        
        session_questions = session.session_questions.all()
        
        for sq in session_questions:
            # Determine area from question tags or type
            area_name = sq.question.tags[0] if sq.question.tags else sq.question.question_type
            
            practice_area, created = PracticeArea.objects.get_or_create(
                user=user,
                tenant=tenant,
                area_name=area_name,
                defaults={'category': session.template.interview_type if session.template else 'General'}
            )
            
            # Update stats
            practice_area.questions_attempted += 1
            if sq.is_correct:
                practice_area.questions_correct += 1
            
            practice_area.total_practice_time_minutes += sq.time_taken_seconds // 60
            
            # Update scores
            accuracy = (practice_area.questions_correct / practice_area.questions_attempted * 100)
            practice_area.current_score = int(accuracy)
            practice_area.best_score = max(practice_area.best_score, sq.score)
            
            # Calculate average
            all_scores = [sq.score for sq in SessionQuestion.objects.filter(
                session__user=user,
                question__tags__contains=[area_name]
            )]
            if all_scores:
                practice_area.average_score = int(sum(all_scores) / len(all_scores))
            
            practice_area.last_practiced_at = timezone.now()
            practice_area.save()


class FeedbackGenerator:
    """Generate detailed feedback using OpenAI"""
    
    @staticmethod
    def generate_feedback(session: InterviewSession) -> InterviewFeedback:
        """
        Generate comprehensive feedback for a session
        
        Args:
            session: InterviewSession instance
        
        Returns:
            InterviewFeedback instance
        """
        if not client:
            return FeedbackGenerator._generate_basic_feedback(session)
        
        try:
            # Prepare session data
            session_questions = session.session_questions.all()
            questions_summary = []
            
            for sq in session_questions:
                questions_summary.append({
                    'question': sq.question.question_text[:100],
                    'type': sq.question.question_type,
                    'score': sq.score,
                    'answer_quality': sq.ai_evaluation[:200] if sq.ai_evaluation else 'Not evaluated'
                })
            
            prompt = f"""Analyze this interview performance and provide detailed feedback:

Interview Type: {session.template.interview_type if session.template else 'General'}
Overall Score: {session.overall_score}/100
Questions Answered: {len(session_questions)}

Questions Summary:
{json.dumps(questions_summary, indent=2)}

Provide comprehensive feedback in JSON format with:
1. technical_analysis: Overall technical performance
2. communication_analysis: Communication skills assessment
3. problem_solving_analysis: Problem-solving approach
4. strong_areas: List of 3-5 strengths
5. weak_areas: List of 3-5 areas to improve
6. study_topics: List of 5 specific topics to study
7. recommendations: List of 3 actionable recommendations
8. percentile_rank: Estimated percentile (0-100)
9. ready_for_real_interview: true/false
10. recommended_difficulty: easy, medium, or hard for next practice
"""
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert career coach and interview trainer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            feedback_data = json.loads(response.choices[0].message.content)
            
            # Create feedback
            feedback = InterviewFeedback.objects.create(
                session=session,
                technical_analysis=feedback_data.get('technical_analysis', ''),
                communication_analysis=feedback_data.get('communication_analysis', ''),
                problem_solving_analysis=feedback_data.get('problem_solving_analysis', ''),
                strong_areas=feedback_data.get('strong_areas', []),
                weak_areas=feedback_data.get('weak_areas', []),
                study_topics=feedback_data.get('study_topics', []),
                resource_links=[],  # Can be populated with relevant links
                percentile_rank=feedback_data.get('percentile_rank', 50),
                ready_for_real_interview=feedback_data.get('ready_for_real_interview', False),
                recommended_difficulty=feedback_data.get('recommended_difficulty', 'medium')
            )
            
            # Update session with summary feedback
            session.overall_feedback = feedback.technical_analysis[:500]
            session.strengths = feedback.strong_areas[:3]
            session.areas_for_improvement = feedback.weak_areas[:3]
            session.recommendations = feedback_data.get('recommendations', [])
            session.save()
            
            return feedback
        
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return FeedbackGenerator._generate_basic_feedback(session)
    
    @staticmethod
    def _generate_basic_feedback(session: InterviewSession) -> InterviewFeedback:
        """Generate basic feedback without OpenAI"""
        feedback = InterviewFeedback.objects.create(
            session=session,
            technical_analysis=f"Completed {session.session_questions.count()} questions with {session.overall_score}% overall score.",
            strong_areas=['Completed the interview'],
            weak_areas=['Consider practicing more'],
            study_topics=['Review interview basics'],
            percentile_rank=session.overall_score,
            ready_for_real_interview=session.overall_score >= 70,
            recommended_difficulty='medium'
        )
        return feedback
