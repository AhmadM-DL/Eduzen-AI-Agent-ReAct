import pandas as pd
import os
from datetime import datetime
from typing import Dict, Any, Optional

def save_student_lead(data: Dict[str, Any], filename: str = "students_leads.xlsx") -> bool:
    """
    Save student lead data to Excel file.
    
    Args:
        data: Dictionary containing student information
        filename: Name of the Excel file to save to
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create DataFrame from the new data
        new_df = pd.DataFrame([data])
        
        # Check if file exists
        if os.path.exists(filename):
            # Read existing data
            existing_df = pd.read_excel(filename)
            # Append new data
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            # Create new file with headers
            updated_df = new_df
        
        # Save to Excel
        updated_df.to_excel(filename, index=False)
        return True
        
    except Exception as e:
        print(f"Error saving student lead: {e}")
        return False

def save_workshop_lead(data: Dict[str, Any], filename: str = "workshops_leads.xlsx") -> bool:
    """
    Save workshop/program lead data to Excel file.
    
    Args:
        data: Dictionary containing workshop/program information
        filename: Name of the Excel file to save to
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create DataFrame from the new data
        new_df = pd.DataFrame([data])
        
        # Check if file exists
        if os.path.exists(filename):
            # Read existing data
            existing_df = pd.read_excel(filename)
            # Append new data
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            # Create new file with headers
            updated_df = new_df
        
        # Save to Excel
        updated_df.to_excel(filename, index=False)
        return True
        
    except Exception as e:
        print(f"Error saving workshop lead: {e}")
        return False

def save_feedback(data: Dict[str, Any], filename: str = "feedback.xlsx") -> bool:
    """
    Save feedback data to Excel file.
    
    Args:
        data: Dictionary containing feedback information
        filename: Name of the Excel file to save to
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Add timestamp
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create DataFrame from the new data
        new_df = pd.DataFrame([data])
        
        # Check if file exists
        if os.path.exists(filename):
            # Read existing data
            existing_df = pd.read_excel(filename)
            # Append new data
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            # Create new file with headers
            updated_df = new_df
        
        # Save to Excel
        updated_df.to_excel(filename, index=False)
        return True
        
    except Exception as e:
        print(f"Error saving feedback: {e}")
        return False

def get_student_leads(filename: str = "students_leads.xlsx") -> Optional[pd.DataFrame]:
    """
    Retrieve all student leads from Excel file.
    
    Args:
        filename: Name of the Excel file to read from
        
    Returns:
        pandas.DataFrame or None: DataFrame containing all student leads
    """
    try:
        if os.path.exists(filename):
            return pd.read_excel(filename)
        else:
            print(f"File {filename} does not exist")
            return None
    except Exception as e:
        print(f"Error reading student leads: {e}")
        return None

def get_workshop_leads(filename: str = "workshops_leads.xlsx") -> Optional[pd.DataFrame]:
    """
    Retrieve all workshop leads from Excel file.
    
    Args:
        filename: Name of the Excel file to read from
        
    Returns:
        pandas.DataFrame or None: DataFrame containing all workshop leads
    """
    try:
        if os.path.exists(filename):
            return pd.read_excel(filename)
        else:
            print(f"File {filename} does not exist")
            return None
    except Exception as e:
        print(f"Error reading workshop leads: {e}")
        return None

def get_feedback_data(filename: str = "feedback.xlsx") -> Optional[pd.DataFrame]:
    """
    Retrieve all feedback data from Excel file.
    
    Args:
        filename: Name of the Excel file to read from
        
    Returns:
        pandas.DataFrame or None: DataFrame containing all feedback
    """
    try:
        if os.path.exists(filename):
            return pd.read_excel(filename)
        else:
            print(f"File {filename} does not exist")
            return None
    except Exception as e:
        print(f"Error reading feedback data: {e}")
        return None

def initialize_excel_files():
    """
    Initialize Excel files with appropriate headers if they don't exist.
    """
    # Student leads headers
    student_headers = {
        'name': [],
        'email': [],
        'language': [],
        'subjects': [],
        'grade': [],
        'location': [],
        'contact_info': [],
        'timestamp': []
    }
    
    # Workshop leads headers
    workshop_headers = {
        'organization_name': [],
        'contact_person': [],
        'email': [],
        'phone': [],
        'program_type': [],
        'program_name': [],
        'description': [],
        'target_audience': [],
        'duration': [],
        'location': [],
        'expected_participants': [],
        'timestamp': []
    }
    
    # Feedback headers
    feedback_headers = {
        'user_question': [],
        'category': [],
        'urgency': [],
        'contact_info': [],
        'timestamp': []
    }
    
    # Create files if they don't exist
    if not os.path.exists("students_leads.xlsx"):
        pd.DataFrame(student_headers).to_excel("students_leads.xlsx", index=False)
    
    if not os.path.exists("workshops_leads.xlsx"):
        pd.DataFrame(workshop_headers).to_excel("workshops_leads.xlsx", index=False)
    
    if not os.path.exists("feedback.xlsx"):
        pd.DataFrame(feedback_headers).to_excel("feedback.xlsx", index=False)

if __name__ == "__main__":
    # Initialize the Excel files
    initialize_excel_files()
    print("Excel files initialized successfully!")