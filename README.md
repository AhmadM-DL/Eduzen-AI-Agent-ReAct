# 🎓 EduZen Assistant - AI Chatbot

A smart AI chatbot for EduZen Agency that helps connect students with teachers and advertises educational programs.

## What does it do?

The EduZen Assistant helps with:
- **Student-Teacher Matching** (K-12 & University) - Free for students
- **Educational Program Advertisement** - Workshops, bootcamps, courses  
- **Language Learning Services** - English, Arabic, German, French, Spanish
- **International University Applications** - Pay only upon acceptance
- **General Questions** - About EduZen services

## Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
```

### 2. Install Dependencies
```bash
pip install openai gradio pandas openpyxl python-dotenv
```

### 3. Set Up OpenAI API Key
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Edit the `.env` file and replace `your_openai_api_key_here` with your actual key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 4. Run the Application
```bash
jupyter notebook Business_agent.ipynb
```
Or run the last cell to launch the web interface directly.

## How to Use

1. **Chat Interface**: Ask questions or provide information to register students/workshops
2. **View Data**: Check the tabs to see collected student leads, workshop leads, and feedback
3. **Excel Files**: All data is automatically saved to Excel files in the project folder

## Example Conversations

**Student Registration:**
> "I'm Ahmed, a Grade 10 student in Cairo. I need help with math and physics. My email is ahmed@email.com"

**Workshop Advertisement:**
> "We want to advertise our Python programming bootcamp for university students"

**General Questions:**
> "What services does EduZen offer?"

## Files Created

- `students_leads.xlsx` - Student registration data
- `workshops_leads.xlsx` - Workshop advertisement data  
- `feedback.xlsx` - User feedback and questions

That's it! The bot will automatically handle registrations and save data to Excel files.
