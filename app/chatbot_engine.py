"""
Chatbot engine for answering queries based on database data.
This module processes natural language questions and retrieves relevant information
from the database to provide answers.
"""

import re
from datetime import datetime
from app.models import User, StudentProfile, Job, Opportunity, Application


class ChatbotEngine:
    """
    Main chatbot engine that processes queries and retrieves relevant data from the database.
    """

    def __init__(self, session=None):
        """Initialize the chatbot engine with a database session."""
        self.session = session
        self.knowledge_base = self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build a knowledge base of available topics and their keywords."""
        return {
            'opportunities': {
                'keywords': ['opportunity', 'opportunities', 'openings', 'job', 'internship', 'hackathon', 'bootcamp', 'seminar', 'session'],
                'handler': self._answer_opportunities
            },
            'jobs': {
                'keywords': ['job', 'jobs', 'placement', 'hiring', 'recruitment', 'ctc', 'company'],
                'handler': self._answer_jobs
            },
            'applications': {
                'keywords': ['application', 'applications', 'applied', 'apply', 'status', 'shortlist'],
                'handler': self._answer_applications
            },
            'student_profile': {
                'keywords': ['profile', 'cgpa', 'gpa', 'branch', 'skill', 'skills', 'resume', 'percentage'],
                'handler': self._answer_profile
            },
            'deadlines': {
                'keywords': ['deadline', 'deadlines', 'closing', 'expire', 'expiring', 'when'],
                'handler': self._answer_deadlines
            },
            'requirements': {
                'keywords': ['require', 'requirement', 'requirement', 'eligible', 'eligibility', 'minimum', 'min'],
                'handler': self._answer_requirements
            },
            'help': {
                'keywords': ['help', 'support', 'how', 'what', 'who', 'where', 'guide', 'instruction'],
                'handler': self._answer_help
            }
        }

    def process_query(self, question: str, user_id: int = None) -> dict:
        """
        Process a user question and return a relevant answer.
        
        Args:
            question: The user's question
            user_id: Optional user ID for personalized answers
            
        Returns:
            Dictionary with 'answer' and 'success' keys
        """
        if not question or not isinstance(question, str):
            return {
                'answer': 'Please ask a valid question.',
                'success': False,
                'context': 'invalid_input'
            }

        question_lower = question.lower().strip()
        
        # Check for greeting
        greeting_response = self._check_greeting(question_lower)
        if greeting_response:
            return greeting_response

        # Identify the topic from keywords
        topic = self._identify_topic(question_lower)
        
        # Get the handler for this topic
        if topic in self.knowledge_base:
            handler = self.knowledge_base[topic]['handler']
            answer = handler(question_lower, user_id)
        else:
            answer = self._fallback_answer(question_lower, user_id)

        return {
            'answer': answer,
            'success': True,
            'context': topic if topic else 'general'
        }

    def _identify_topic(self, question_lower: str) -> str:
        """Identify the topic of the question based on keywords."""
        for topic, data in self.knowledge_base.items():
            for keyword in data['keywords']:
                if keyword in question_lower:
                    return topic
        return None

    def _check_greeting(self, question: str) -> dict:
        """Check if the question is a greeting."""
        greetings = {
            'hello': 'Hello! I am your Training & Placement Assistant. I can help you with information about opportunities, jobs, applications, and more. What would you like to know?',
            'hi': 'Hi there! How can I assist you today?',
            'hey': 'Hey! Feel free to ask me about opportunities, jobs, or your applications.',
            'thanks': 'You\'re welcome! Feel free to ask if you need anything else.',
            'thank you': 'You\'re welcome! Is there anything else I can help you with?',
            'bye': 'Goodbye! Good luck with your placements!',
            'goodbye': 'Goodbye! Feel free to come back anytime.',
        }

        for greeting, response in greetings.items():
            if greeting in question:
                return {
                    'answer': response,
                    'success': True,
                    'context': 'greeting'
                }
        
        return None

    def _answer_opportunities(self, question: str, user_id: int = None) -> str:
        """Answer questions about opportunities."""
        try:
            opportunities = Opportunity.query.all()

            if not opportunities:
                return 'Sorry, there are no opportunities available at the moment. Please check back later!'

            if any(word in question for word in ['how many', 'count', 'total']):
                return f'There are currently {len(opportunities)} opportunities available.'

            if any(word in question for word in ['what', 'list', 'show', 'available']):
                response = 'Here are the available opportunities:\n\n'
                for opp in opportunities[:5]:  # Show first 5
                    response += f'• **{opp.title}** ({opp.type})\n'
                    if opp.company_name:
                        response += f'  Company: {opp.company_name}\n'
                    if opp.deadline:
                        response += f'  Deadline: {opp.deadline.strftime("%d-%m-%Y")}\n'
                    response += '\n'
                
                if len(opportunities) > 5:
                    response += f'...and {len(opportunities) - 5} more opportunities.'
                
                return response

            if any(word in question for word in ['type', 'category']):
                types = set(opp.type for opp in opportunities)
                return f'Available opportunity types: {", ".join(types)}'

            return f'Found {len(opportunities)} opportunities. You can search by type, company, or deadline. What specific information would you like?'

        except Exception as e:
            return f'Error retrieving opportunities: {str(e)}'

    def _answer_jobs(self, question: str, user_id: int = None) -> str:
        """Answer questions about jobs."""
        try:
            jobs = Job.query.all()

            if not jobs:
                return 'No job openings available at the moment.'

            if any(word in question for word in ['how many', 'count', 'total']):
                return f'There are {len(jobs)} job openings currently.'

            if any(word in question for word in ['what', 'list', 'show', 'available']):
                response = 'Active job openings:\n\n'
                for job in jobs[:5]:
                    response += f'• **{job.company_name}** - {job.ctc}\n'
                    response += f'  Min CGPA: {job.min_cgpa}\n'
                    response += f'  Deadline: {job.deadline.strftime("%d-%m-%Y") if job.deadline else "TBD"}\n\n'
                
                if len(jobs) > 5:
                    response += f'And {len(jobs) - 5} more positions.'
                
                return response

            if any(word in question for word in ['ctc', 'salary', 'pay', 'package']):
                ctc_list = [job.ctc for job in jobs]
                response = 'Job packages offered:\n'
                for ctc in set(ctc_list):
                    response += f'• {ctc}\n'
                return response

            return f'Found {len(jobs)} job openings. Ask about specific companies, packages, or requirements.'

        except Exception as e:
            return f'Error retrieving jobs: {str(e)}'

    def _answer_applications(self, question: str, user_id: int = None) -> str:
        """Answer questions about applications (personalized for logged-in users)."""
        if not user_id:
            return 'Please log in to view your application status and history.'

        try:
            applications = Application.query.filter_by(student_id=user_id).all()

            if not applications:
                return 'You haven\'t applied to any opportunities yet. Check the opportunities section to find interesting positions!'

            if any(word in question for word in ['how many', 'count', 'total']):
                return f'You have applied to {len(applications)} opportunities.'

            if any(word in question for word in ['status', 'where', 'check']):
                response = 'Your application statuses:\n\n'
                status_summary = {}
                
                for app in applications:
                    status = app.status
                    status_summary[status] = status_summary.get(status, 0) + 1
                    
                    if app.job:
                        response += f'• **{app.job.company_name}** - {status}\n'
                    elif app.opportunity:
                        response += f'• **{app.opportunity.title}** - {status}\n'
                
                response += '\n**Summary:**\n'
                for status, count in status_summary.items():
                    response += f'• {status}: {count}\n'
                
                return response

            if any(word in question for word in ['selected', 'selected', 'shortlist', 'shortlisted']):
                selected = [app for app in applications if app.status == 'Selected']
                if selected:
                    response = 'Congratulations! You have been selected for:\n'
                    for app in selected:
                        if app.job:
                            response += f'• {app.job.company_name}\n'
                        elif app.opportunity:
                            response += f'• {app.opportunity.title}\n'
                    return response
                else:
                    return 'You haven\'t been selected yet. Keep trying and improve your profile!'

            return f'You have {len(applications)} applications. Ask about your status, selected positions, or shortlists.'

        except Exception as e:
            return f'Error retrieving applications: {str(e)}'

    def _answer_profile(self, question: str, user_id: int = None) -> str:
        """Answer questions about student profiles and eligibility."""
        if not user_id:
            return 'Please log in to view your profile information.'

        try:
            student_profile = StudentProfile.query.filter_by(user_id=user_id).first()

            if not student_profile:
                return 'Please complete your profile first to get personalized recommendations.'

            if any(word in question for word in ['cgpa', 'gpa']):
                return f'Your current CGPA is {student_profile.cgpa}.'

            if any(word in question for word in ['branch', 'stream']):
                return f'Your branch is {student_profile.branch}.'

            if any(word in question for word in ['skill', 'skills']):
                skills = student_profile.skills or 'Not updated'
                return f'Your skills: {skills}'

            if any(word in question for word in ['eligible', 'eligibility', 'qualify', 'can apply']):
                eligible_jobs = []
                for job in Job.query.all():
                    if student_profile.cgpa >= job.min_cgpa:
                        if student_profile.branch in job.allowed_branches:
                            eligible_jobs.append(job.company_name)
                
                if eligible_jobs:
                    return f'You are eligible for {len(eligible_jobs)} positions. Check the opportunities section to apply!'
                else:
                    return f'Your current profile (CGPA {student_profile.cgpa}) may not meet the minimum requirements. Keep improving!'

            return f'Your profile shows CGPA: {student_profile.cgpa}, Branch: {student_profile.branch}. What would you like to know?'

        except Exception as e:
            return f'Error retrieving profile: {str(e)}'

    def _answer_deadlines(self, question: str, user_id: int = None) -> str:
        """Answer questions about upcoming deadlines."""
        try:
            now = datetime.utcnow()
            
            # Get upcoming opportunities
            upcoming = Opportunity.query.filter(
                Opportunity.deadline >= now
            ).order_by(Opportunity.deadline).all()

            # Get upcoming jobs
            future_jobs = Job.query.filter(
                Job.deadline >= now
            ).order_by(Job.deadline).all()

            if not upcoming and not future_jobs:
                return 'No upcoming deadlines at the moment.'

            if any(word in question for word in ['upcoming', 'coming', 'next', 'soon']):
                response = 'Upcoming deadlines:\n\n'
                
                all_deadlines = []
                for opp in upcoming[:5]:
                    all_deadlines.append((opp.deadline, f'• **{opp.title}** - {opp.deadline.strftime("%d-%m-%Y")}'))
                
                for job in future_jobs[:5]:
                    all_deadlines.append((job.deadline, f'• **{job.company_name}** - {job.deadline.strftime("%d-%m-%Y")}'))
                
                all_deadlines.sort(key=lambda x: x[0])
                
                for _, text in all_deadlines[:5]:
                    response += f'{text}\n'
                
                return response

            return f'There are {len(upcoming) + len(future_jobs)} active opportunities with upcoming deadlines.'

        except Exception as e:
            return f'Error retrieving deadlines: {str(e)}'

    def _answer_requirements(self, question: str, user_id: int = None) -> str:
        """Answer questions about requirements and eligibility criteria."""
        try:
            if any(word in question for word in ['job', 'position']):
                jobs = Job.query.all()
                if jobs:
                    response = 'General job requirements:\n\n'
                    for job in jobs[:3]:
                        response += f'**{job.company_name}:**\n'
                        response += f'• Min CGPA: {job.min_cgpa}\n'
                        response += f'• Allowed Branches: {job.allowed_branches}\n\n'
                    return response

            if any(word in question for word in ['opportunity', 'opportunities']):
                opportunities = Opportunity.query.filter(
                    Opportunity.requirements.isnot(None)
                ).all()
                
                if opportunities:
                    response = 'Opportunity requirements:\n\n'
                    for opp in opportunities[:3]:
                        response += f'**{opp.title}:**\n'
                        reqs = opp.get_requirements_list()
                        for req in reqs[:3]:
                            response += f'• {req}\n'
                        response += '\n'
                    return response

            return 'Tell me which job or opportunity you\'re interested in, and I\'ll share the requirements!'

        except Exception as e:
            return f'Error retrieving requirements: {str(e)}'

    def _answer_help(self, question: str, user_id: int = None) -> str:
        """Provide help and guidance."""
        help_text = '''I'm your Training & Placement Assistant! Here's what I can help you with:

**About Opportunities:**
• "Show me available opportunities"
• "How many opportunities are there?"
• "What types of opportunities exist?"

**About Jobs:**
• "What job openings are available?"
• "What are the salary packages?"
• "Which companies are hiring?"

**About Your Applications:**
• "What's my application status?"
• "How many positions have I applied to?"
• "Which positions am I selected for?"

**About Your Profile:**
• "What's my CGPA?"
• "Which positions am I eligible for?"
• "What skills have I listed?"

**About Deadlines:**
• "What are the upcoming deadlines?"
• "When does this opportunity close?"

**About Requirements:**
• "What are the job requirements?"
• "Am I eligible for this position?"

Feel free to ask me questions naturally - I'll do my best to help! 😊'''
        
        return help_text

    def _fallback_answer(self, question: str, user_id: int = None) -> str:
        """Provide a fallback answer when topic is not identified."""
        return '''I didn't quite understand your question. Here are some things I can help with:
        
• Information about job opportunities and openings
• Application status and history
• Your profile and eligibility
• Upcoming deadlines
• Job requirements and skills needed

Try asking something like:
- "Show me available opportunities"
- "What's my application status?"
- "Am I eligible for this job?"
- "What are the upcoming deadlines?"

Type "help" if you need more guidance!'''
