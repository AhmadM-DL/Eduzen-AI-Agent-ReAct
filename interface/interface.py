import gradio as gr
from agents.vanilla_agent import create_agent as create_vanilla_agent
from agents.react_lg_agent import create_agent as create_react_agent
from typing import List, Tuple, Dict
import pandas as pd
from utils.xlsx import get_student_leads, get_workshop_leads, get_feedback_data

# Global variables for agent management
current_agent = None
current_agent_type = None
current_personality = None

def initialize_agent(agent_type: str, personality: str = "formal"):
    """Initialize the agent based on type and personality."""
    global current_agent, current_agent_type, current_personality
    
    if agent_type == "vanilla":
        current_agent = create_vanilla_agent()
        current_agent_type = "vanilla"
        current_personality = None
    elif agent_type == "react":
        current_agent = create_react_agent(personality)
        current_agent_type = "react"
        current_personality = personality
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return f"✅ Initialized {agent_type} agent" + (f" with {personality} personality" if personality else "")

def chat_interface(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    """
    Chat interface function for Gradio.
    
    Args:
        message: User's current message
        history: Chat history in Gradio format
        
    Returns:
        Tuple of (response, updated_history)
    """
    global current_agent
    
    if current_agent is None:
        error_response = "❌ No agent initialized. Please select an agent type first."
        history.append([message, error_response])
        return "", history
    
    try:
        # Convert Gradio history format to our format
        formatted_history = []
        for exchange in history:
            if len(exchange) >= 2:
                formatted_history.append({
                    "user": exchange[0],
                    "assistant": exchange[1]
                })
        
        # Get response from agent based on type
        if current_agent_type == "vanilla":
            response, updated_agent_history = current_agent.chat(message, formatted_history)
        elif current_agent_type == "react":
            (final_answer, reasoning_steps), updated_agent_history = current_agent.chat_with_history(message, formatted_history)
            # Format the response to show both reasoning and final answer
            if reasoning_steps:
                response = f"**Reasoning:**\n"
                for i, step in enumerate(reasoning_steps, 1):
                    response += f"{i}. {step}\n"
                response += f"\n**Response:**\n{final_answer}"
            else:
                response = final_answer
        else:
            raise ValueError(f"Unknown agent type: {current_agent_type}")
        
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
    .agent-config { background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }
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
                # Agent Configuration Section
                with gr.Group():
                    gr.HTML('<div class="agent-config"><h3>🤖 Agent Configuration</h3></div>')
                    
                    with gr.Row():
                        agent_type = gr.Radio(
                            choices=["vanilla", "react"],
                            label="Agent Type",
                            value="vanilla",
                            info="Vanilla: Simple conversation agent | React: Advanced reasoning agent"
                        )
                        
                        personality = gr.Radio(
                            choices=["formal", "casual", "supportive"],
                            label="Personality (React only)",
                            value="formal",
                            visible=False,
                            info="Choose the agent's communication style"
                        )
                    
                    with gr.Row():
                        init_btn = gr.Button("Initialize Agent", variant="primary")
                        status_msg = gr.Textbox(
                            label="Status", 
                            value="No agent initialized", 
                            interactive=False,
                            scale=2
                        )
                
                # Chat Interface
                chatbot = gr.Chatbot(
                    height=400,
                    placeholder="Initialize an agent first, then start chatting..."
                )
                
                msg = gr.Textbox(
                    placeholder="Type your message here...",
                    label="Message",
                    lines=1
                )
                
                with gr.Row():
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                    clear_btn = gr.Button("Clear", variant="secondary", scale=1)
                
                # Show/hide personality based on agent type
                def update_personality_visibility(agent_type_value):
                    return gr.update(visible=(agent_type_value == "react"))
                
                agent_type.change(
                    update_personality_visibility,
                    inputs=[agent_type],
                    outputs=[personality]
                )
                
                # Initialize agent
                init_btn.click(
                    initialize_agent,
                    inputs=[agent_type, personality],
                    outputs=[status_msg]
                )
                
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
def launch_interface(agent_type="vanilla", personality="formal", share=False, debug=False):
    """
    Launch the Gradio interface with specified agent configuration.
    
    Args:
        agent_type: Type of agent ("vanilla" or "react")
        personality: Personality for react agent ("formal", "casual", "supportive")
        share: Whether to create a public link
        debug: Whether to run in debug mode
    """
    # Initialize the agent if parameters are provided
    if agent_type:
        try:
            initialize_agent(agent_type, personality)
            print(f"✅ Pre-initialized {agent_type} agent" + (f" with {personality} personality" if agent_type == "react" else ""))
        except Exception as e:
            print(f"❌ Failed to pre-initialize agent: {e}")
    
    interface = create_interface()
    interface.launch(
        share=share,
        debug=debug,
        server_name="0.0.0.0",
        server_port=7860
    )

if __name__ == "__main__":
    # Example usage:
    # launch_interface(agent_type="vanilla", debug=True)
    # launch_interface(agent_type="react", personality="casual", debug=True)
    launch_interface(agent_type="vanilla", debug=True)