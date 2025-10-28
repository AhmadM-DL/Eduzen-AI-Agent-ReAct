import gradio as gr
from agent import create_agent
from typing import List, Tuple, Dict
import pandas as pd
from xlsx import get_student_leads, get_workshop_leads, get_feedback_data

# Initialize the agent
agent = create_agent()

def chat_interface(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    """
    Chat interface function for Gradio.
    
    Args:
        message: User's current message
        history: Chat history in Gradio format
        
    Returns:
        Tuple of (response, updated_history)
    """
    try:
        # Convert Gradio history format to our format
        formatted_history = []
        for exchange in history:
            if len(exchange) >= 2:
                formatted_history.append({
                    "user": exchange[0],
                    "assistant": exchange[1]
                })
        
        # Get response from agent (now returns tuple)
        response, updated_agent_history = agent.chat(message, formatted_history)
        
        # Update Gradio history format
        history.append([message, response])
        
        return "", history
        
    except Exception as e:
        error_response = f"I apologize, but I encountered an error: {str(e)}. Please try again."
        history.append([message, error_response])
        return "", history

def view_student_leads() -> str:
    """View all student leads in a formatted table."""
    try:
        df = get_student_leads()
        if df is not None and not df.empty:
            return df.to_html(index=False, escape=False, classes="table table-striped")
        else:
            return "<p>No student leads found.</p>"
    except Exception as e:
        return f"<p>Error loading student leads: {str(e)}</p>"

def view_workshop_leads() -> str:
    """View all workshop leads in a formatted table."""
    try:
        df = get_workshop_leads()
        if df is not None and not df.empty:
            return df.to_html(index=False, escape=False, classes="table table-striped")
        else:
            return "<p>No workshop leads found.</p>"
    except Exception as e:
        return f"<p>Error loading workshop leads: {str(e)}</p>"

def view_feedback() -> str:
    """View all feedback in a formatted table."""
    try:
        df = get_feedback_data()
        if df is not None and not df.empty:
            return df.to_html(index=False, escape=False, classes="table table-striped")
        else:
            return "<p>No feedback found.</p>"
    except Exception as e:
        return f"<p>Error loading feedback: {str(e)}</p>"

# Removed export_leads function - not needed in simplified interface

# Create the Gradio interface
def create_interface():
    """Create and configure the simple Gradio interface."""
    
    # Simple CSS styling
    custom_css = """
    .container { max-width: 1000px; margin: auto; }
    .header { text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 8px; margin-bottom: 1rem; }
    """
    
    with gr.Blocks(css=custom_css, title="EduZen Assistant") as interface:
        
        # Simple header
        gr.HTML("""
        <div class="header">
            <h1>🎓 EduZen Assistant</h1>
            <p>Chat with our AI assistant or view collected data</p>
        </div>
        """)
        
        with gr.Tabs():
            # Chat Tab
            with gr.TabItem("💬 Chat"):
                chatbot = gr.Chatbot(
                    height=400,
                    placeholder="Ask me about EduZen services..."
                )
                
                msg = gr.Textbox(
                    placeholder="Type your message here...",
                    label="Message",
                    lines=1
                )
                
                with gr.Row():
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                    clear_btn = gr.Button("Clear", variant="secondary", scale=1)
                
                # Event handlers
                send_btn.click(chat_interface, [msg, chatbot], [msg, chatbot])
                msg.submit(chat_interface, [msg, chatbot], [msg, chatbot])
                clear_btn.click(lambda: (None, []), outputs=[msg, chatbot])
            
            # Student Leads Tab
            with gr.TabItem("👨‍🎓 Student Leads"):
                student_display = gr.HTML()
                refresh_students = gr.Button("Refresh Data")
                refresh_students.click(view_student_leads, outputs=student_display)
                        
            # Workshop Leads Tab
            with gr.TabItem("🏫 Workshop Leads"):
                workshop_display = gr.HTML()
                refresh_workshops = gr.Button("Refresh Data")
                refresh_workshops.click(view_workshop_leads, outputs=workshop_display)
                        
            # Feedback Tab
            with gr.TabItem("💬 Feedback"):
                feedback_display = gr.HTML()
                refresh_feedback = gr.Button("Refresh Data")
                refresh_feedback.click(view_feedback, outputs=feedback_display)
    
    return interface

# Launch function
def launch_interface(share=False, debug=False):
    """Launch the simple Gradio interface."""
    interface = create_interface()
    interface.launch(
        share=share,
        debug=debug,
        server_name="0.0.0.0",
        server_port=7860
    )

if __name__ == "__main__":
    launch_interface(debug=True)