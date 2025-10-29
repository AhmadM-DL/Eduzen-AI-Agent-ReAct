import json
from typing import Dict, Any, List
from langchain_core.tools import tool
from utils.xlsx import save_student_lead, save_workshop_lead, save_feedback

@tool
def record_students_lead(
    name: str,
    email: str,
    language: str,
    subjects: str,
    grade: str,
    location: str,
    contact_info: str = ""
) -> str:
    """
    Record a student lead for teacher matching services.
    
    Args:
        name: Student's full name
        email: Student's email address
        language: Preferred language for instruction
        subjects: Subjects student needs help with (comma-separated)
        grade: Student's grade level (1-12 or university level)
        location: Student's location/area
        contact_info: Additional contact information (optional)
    
    Returns:
        str: Success or error message
    """
    try:
        data = {
            'name': name,
            'email': email,
            'language': language,
            'subjects': subjects,
            'grade': grade,
            'location': location,
            'contact_info': contact_info
        }
        
        success = save_student_lead(data)
        
        if success:
            if "university" in grade.lower() or any(term in grade.lower() for term in ["bachelor", "master", "phd", "undergraduate", "graduate"]):
                whatsapp_group = "taleb w istez"
            else:
                whatsapp_group = "telmiz w istez"
                
            return f"✅ Student lead recorded successfully! Your information has been saved and you'll be matched with qualified teachers through our '{whatsapp_group}' WhatsApp group. Remember, this service is completely free for students - teachers only pay when they get their first paycheck. You'll be contacted soon with potential matches!"
        else:
            return "❌ Sorry, there was an error recording your information. Please try again or contact our support team."
            
    except Exception as e:
        return f"❌ Error: {str(e)}. Please check your information and try again."

@tool
def record_workshops_lead(
    organization_name: str,
    contact_person: str,
    email: str,
    phone: str,
    program_type: str,
    program_name: str,
    description: str,
    target_audience: str,
    duration: str,
    location: str,
    expected_participants: str
) -> str:
    """
    Record a workshop/educational program lead for advertising services.
    
    Args:
        organization_name: Name of the organization offering the program
        contact_person: Main contact person's name
        email: Contact email address
        phone: Contact phone number
        program_type: Type of program (workshop, bootcamp, course, etc.)
        program_name: Name of the specific program
        description: Detailed description of the program
        target_audience: Who the program is designed for
        duration: How long the program runs
        location: Where the program takes place
        expected_participants: Expected number of participants
    
    Returns:
        str: Success or error message
    """
    try:
        data = {
            'organization_name': organization_name,
            'contact_person': contact_person,
            'email': email,
            'phone': phone,
            'program_type': program_type,
            'program_name': program_name,
            'description': description,
            'target_audience': target_audience,
            'duration': duration,
            'location': location,
            'expected_participants': expected_participants
        }
        
        success = save_workshop_lead(data)
        
        if success:
            return f"✅ Workshop/program lead recorded successfully! Your '{program_name}' will be advertised through our 'motadareb w khabeer' WhatsApp group. Our commission is 10% per registered attendee. Our team will contact you within 24 hours to discuss the advertising strategy and timeline."
        else:
            return "❌ Sorry, there was an error recording your program information. Please try again or contact our support team."
            
    except Exception as e:
        return f"❌ Error: {str(e)}. Please check your information and try again."

@tool
def record_feedback(
    user_question: str,
    category: str = "general",
    urgency: str = "medium",
    contact_info: str = ""
) -> str:
    """
    Record user feedback for questions that the bot cannot answer.
    
    Args:
        user_question: The question or issue the user has
        category: Category of the question (general, technical, service-specific, etc.)
        urgency: Urgency level (low, medium, high)
        contact_info: User's contact information for follow-up
    
    Returns:
        str: Success message
    """
    try:
        data = {
            'user_question': user_question,
            'category': category,
            'urgency': urgency,
            'contact_info': contact_info
        }
        
        success = save_feedback(data)
        
        if success:
            return "✅ Thank you for your feedback! Your question has been recorded and our team will review it. If you provided contact information, we'll get back to you as soon as possible. In the meantime, feel free to ask other questions about our services!"
        else:
            return "❌ Sorry, there was an error recording your feedback. Please try again or contact our support team directly."
            
    except Exception as e:
        return f"❌ Error recording feedback: {str(e)}"

# Function definitions for OpenAI API tools
TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "record_students_lead",
            "description": "Record a student's information for teacher matching services. Use this when a student wants to be matched with a teacher for K-12 or university subjects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Student's full name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Student's email address"
                    },
                    "language": {
                        "type": "string",
                        "description": "Preferred language for instruction (e.g., English, Arabic, French, etc.)"
                    },
                    "subjects": {
                        "type": "string",
                        "description": "Subjects student needs help with, separated by commas"
                    },
                    "grade": {
                        "type": "string",
                        "description": "Student's grade level (1-12) or university level (e.g., 'Grade 10', 'University - Bachelor's in Engineering')"
                    },
                    "location": {
                        "type": "string",
                        "description": "Student's location or area"
                    },
                    "contact_info": {
                        "type": "string",
                        "description": "Additional contact information like WhatsApp number or phone (optional)"
                    }
                },
                "required": ["name", "email", "language", "subjects", "grade", "location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_workshops_lead",
            "description": "Record information about educational programs, workshops, or bootcamps that want to be advertised through EduZen's platform.",
            "parameters": {
                "type": "object",
                "properties": {
                    "organization_name": {
                        "type": "string",
                        "description": "Name of the organization offering the program"
                    },
                    "contact_person": {
                        "type": "string",
                        "description": "Main contact person's name"
                    },
                    "email": {
                        "type": "string",
                        "description": "Contact email address"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Contact phone number"
                    },
                    "program_type": {
                        "type": "string",
                        "description": "Type of program (workshop, bootcamp, course, seminar, etc.)"
                    },
                    "program_name": {
                        "type": "string",
                        "description": "Name of the specific program"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the program content and objectives"
                    },
                    "target_audience": {
                        "type": "string",
                        "description": "Who the program is designed for (students, professionals, beginners, etc.)"
                    },
                    "duration": {
                        "type": "string",
                        "description": "How long the program runs (e.g., '3 days', '2 weeks', '1 month')"
                    },
                    "location": {
                        "type": "string",
                        "description": "Where the program takes place (online, specific city, etc.)"
                    },
                    "expected_participants": {
                        "type": "string",
                        "description": "Expected number of participants"
                    }
                },
                "required": ["organization_name", "contact_person", "email", "phone", "program_type", "program_name", "description", "target_audience", "duration", "location", "expected_participants"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_feedback",
            "description": "Record user feedback when the bot cannot answer a question or when users have specific inquiries that need human attention.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_question": {
                        "type": "string",
                        "description": "The question or issue the user has"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category of the question",
                        "enum": ["general", "technical", "service-specific", "billing", "partnership", "other"]
                    },
                    "urgency": {
                        "type": "string",
                        "description": "Urgency level of the question",
                        "enum": ["low", "medium", "high"]
                    },
                    "contact_info": {
                        "type": "string",
                        "description": "User's contact information for follow-up (optional)"
                    }
                },
                "required": ["user_question"]
            }
        }
    }
]

# Available functions mapping
AVAILABLE_FUNCTIONS = {
    "record_students_lead": record_students_lead,
    "record_workshops_lead": record_workshops_lead,
    "record_feedback": record_feedback
}