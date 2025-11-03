import openai
import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from agents.tools import TOOLS_DEFINITIONS, AVAILABLE_FUNCTIONS
from agents.tools import record_students_lead, record_workshops_lead, record_feedback


# Load environment variables
load_dotenv()

class EduZenVanillaAgent:
    def __init__(self, personality="formal"):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.personality = personality
        self.business_summary = self._load_business_summary()
        self.instructions = self._load_instructions()
        self.personality_style = self._load_personality(personality)
        self.system_prompt = self._create_system_prompt()
        
    def _load_business_summary(self) -> str:
        try:
            file_path = os.path.join("..", "me", "business_summary.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "EduZen Agency - Educational services provider"
    
    def _load_instructions(self) -> str:
        try:
            file_path = os.path.join("..", "prompts", "instructions.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Provide helpful assistance with educational services."
    
    def _load_personality(self, personality: str) -> str:
        try:
            file_path = os.path.join("..", "prompts", "personalities", f"{personality}.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Be helpful and professional."

    def _create_system_prompt(self) -> str:
         return f" {self.business_summary} \n {self.instructions} \n {self.personality_style}"

    def chat(self, message: str, history: List[Dict[str, str]] = None) -> tuple[str, List[Dict[str, str]]]:
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
                        tool = AVAILABLE_FUNCTIONS[function_name]
                        function_response = tool.invoke(function_args)
                        
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

def create_agent(personality: str = "formal") -> EduZenVanillaAgent:
    return EduZenVanillaAgent(personality)