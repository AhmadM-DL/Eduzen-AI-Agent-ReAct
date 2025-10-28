import openai
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from tools import TOOLS_DEFINITIONS, AVAILABLE_FUNCTIONS

# Load environment variables
load_dotenv()

class EduZenAgent:
    def __init__(self):
        """Initialize the EduZen AI agent with OpenAI client and business context."""
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.business_summary = self._load_business_summary()
        self.system_prompt = self._create_system_prompt()
        
    def _load_business_summary(self) -> str:
        """Load business summary from the me/business_summary.txt file."""
        try:
            with open("me/business_summary.txt", "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return "EduZen is an educational services agency focused on connecting students with teachers and educational opportunities."
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt with business context."""
        return f"""You are EduZen Assistant, a helpful AI agent representing EduZen Agency. You help users with educational services and information.

BUSINESS CONTEXT:
{self.business_summary}

YOUR ROLE:
- Provide information about EduZen's services
- Help students register for teacher matching
- Assist educational program providers with advertising inquiries
- Answer questions about pricing, processes, and services
- Collect leads for appropriate services
- Record feedback for questions you cannot answer

COMMUNICATION STYLE:
- Be friendly, professional, and helpful
- Use clear, simple language
- Always mention the unique value proposition (pay only when successful)
- Emphasize the community-driven aspect
- Be enthusiastic about educational opportunities

Always be helpful and guide users toward the appropriate service!"""

    def chat(self, message: str, history: List[Dict[str, str]] = None) -> tuple[str, List[Dict[str, str]]]:
        """
        Process a chat message and return both response and updated history.
        
        Args:
            message: User's message
            history: Previous conversation history
            
        Returns:
            tuple: (response_message, updated_history)
        """
        if history is None:
            history = []
        
        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        for exchange in history:
            messages.append({"role": "user", "content": exchange.get("user", "")})
            messages.append({"role": "assistant", "content": exchange.get("assistant", "")})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            # First API call to get response and potential tool calls
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=TOOLS_DEFINITIONS,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000
            )
            
            response_message = response.choices[0].message
            agent_response = ""
            
            # Check if the model wants to call a function
            if response_message.tool_calls:
                # Add the assistant's response to messages
                messages.append(response_message)
                
                # Process each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Call the function
                    if function_name in AVAILABLE_FUNCTIONS:
                        function_response = AVAILABLE_FUNCTIONS[function_name](**function_args)
                        
                        # Add function response to messages
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": function_response
                        })
                
                # Get final response from the model
                final_response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                agent_response = final_response.choices[0].message.content
            
            else:
                # No tool calls, return the response directly
                agent_response = response_message.content
            
            # Update history with the new exchange
            updated_history = history.copy()
            updated_history.append({
                "user": message,
                "assistant": agent_response
            })
            
            return agent_response, updated_history
                
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}. Please try again or contact our support team."
            # Still update history even with errors
            updated_history = history.copy()
            updated_history.append({
                "user": message,
                "assistant": error_message
            })
            return error_message, updated_history

    def chat_simple(self, message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Process a chat message and return only the response (legacy method).
        
        Args:
            message: User's message
            history: Previous conversation history
            
        Returns:
            str: Agent's response
        """
        response, _ = self.chat(message, history)
        return response

    def get_response(self, message: str, history: List[Dict[str, str]] = None) -> str:
        """
        Simplified interface for getting a response (legacy method).
        
        Args:
            message: User's message
            history: Previous conversation history
            
        Returns:
            str: Agent's response
        """
        return self.chat_simple(message, history)

def create_agent() -> EduZenAgent:
    """Create and return a new EduZen agent instance."""
    return EduZenAgent()

# Test function
def test_agent():
    """Test the agent with sample interactions."""
    agent = create_agent()
    
    print("EduZen Agent Test")
    print("================")
    
    test_messages = [
        "Hi! What services does EduZen offer?",
        "I'm a grade 10 student looking for help with math and physics. Can you help me find a teacher?",
        "We have a programming bootcamp we'd like to advertise. How does that work?"
    ]
    
    for msg in test_messages:
        print(f"\nUser: {msg}")
        response, history = agent.chat(msg, history)
        print(f"Agent: {response}")

if __name__ == "__main__":
    test_agent()