import os
import json
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from agents.tools import record_students_lead, record_workshops_lead, record_feedback

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[Any], "The messages in the conversation"]
    reasoning: str
    next_action: str
    is_final: bool

class EduZenReActAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.business_summary = open("../me/business_summary.txt", "r", encoding="utf-8").read()
        self.tools = [record_students_lead, record_workshops_lead, record_feedback]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self._build_graph()
        

  
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt with ReAct methodology."""
        return f"""You are EduZen Assistant, a helpful AI agent representing EduZen Agency. You use the ReAct (Reasoning and Acting) methodology to help users.

BUSINESS CONTEXT:
{self.business_summary}

YOUR ROLE:
- Provide information about EduZen's services
- Help students register for teacher matching
- Assist educational program providers with advertising inquiries
- Answer questions about pricing, processes, and services
- Collect leads for appropriate services
- Record feedback for questions you cannot answer

REACT METHODOLOGY:
You must follow this pattern for each interaction:

1. THOUGHT: Analyze what the user is asking and what you need to do
2. ACTION: Decide if you need to use a tool or can respond directly
3. OBSERVATION: If you used a tool, observe the result
4. FINAL RESPONSE: Provide your final answer to the user

COMMUNICATION STYLE:
- Be friendly, professional, and helpful
- Use clear, simple language
- Always mention the unique value proposition (pay only when successful)
- Emphasize the community-driven aspect
- Be enthusiastic about educational opportunities

AVAILABLE ACTIONS:
- record_student_lead: When a student wants to be matched with a teacher
- record_workshop_lead: When an organization wants to advertise educational programs
- record_user_feedback: When you cannot answer a question or need human follow-up
- Direct response: When you can answer without using tools

Always think step by step and explain your reasoning before taking action!"""

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        def reasoning_node(state: MessagesState):
            """Node for reasoning about the user's request."""
            messages = state["messages"]
            
            # Create a reasoning prompt
            reasoning_prompt = ChatPromptTemplate.from_messages([
                ("system", self._create_system_prompt()),
                ("human", "Think step by step about this request. What is the user asking for? What action should I take?\n\nUser message: {input}"),
            ])
            
            # Get the latest user message
            latest_message = messages[-1].content if messages else ""
            
            # Generate reasoning
            reasoning_chain = reasoning_prompt | self.llm
            reasoning_response = reasoning_chain.invoke({"input": latest_message})
            
            # Add reasoning as a system message
            return {
                "messages": messages + [AIMessage(content=f"THINKING: {reasoning_response.content}")],
            }
        
        def agent_node(state: MessagesState):
            """Main agent node that processes the request and potentially calls tools."""
            messages = state["messages"]
            
            # Prepare messages for the LLM, including system prompt
            formatted_messages = [
                SystemMessage(content=self._create_system_prompt())
            ] + messages
            
            response = self.llm_with_tools.invoke(formatted_messages)
            return {"messages": messages + [response]}
        
        def should_continue(state: MessagesState):
            """Determine if we should continue with tool calls or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If there are tool calls, continue to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            # Otherwise, we're done
            return END
        
        # Create the graph
        workflow = StateGraph(MessagesState)
        
        # Add nodes
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("reasoning")
        
        # Add edges
        workflow.add_edge("reasoning", "agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")
        
        # Compile the graph
        return workflow.compile(checkpointer=MemorySaver())
    
    def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Process a chat message using the ReAct methodology.
        
        Args:
            message: User's message
            thread_id: Thread ID for conversation state
            
        Returns:
            str: Agent's response
        """
        try:
            # Prepare the input
            input_data = {
                "messages": [HumanMessage(content=message)]
            }
            
            # Run the graph
            config = {"configurable": {"thread_id": thread_id}}
            result = self.graph.invoke(input_data, config)
            
            # Get the final response
            final_message = result["messages"][-1]
            
            # If it's an AI message, return its content
            if isinstance(final_message, AIMessage):
                # Filter out thinking/reasoning from the final response
                content = final_message.content
                if content.startswith("THINKING:"):
                    # If there are tool calls, the actual response will be after tool execution
                    # Get all messages and find the last substantive AI response
                    for msg in reversed(result["messages"]):
                        if isinstance(msg, AIMessage) and not msg.content.startswith("THINKING:"):
                            content = msg.content
                            break
                return content
            else:
                return "I apologize, but I encountered an issue processing your request. Please try again."
                
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or contact our support team."
    
    def chat_with_history(self, message: str, history: List[Dict[str, str]] = None, thread_id: str = "default") -> tuple[str, List[Dict[str, str]]]:
        """
        Process a chat message and return both response and updated history.
        
        Args:
            message: User's message
            history: Previous conversation history (for compatibility)
            thread_id: Thread ID for conversation state
            
        Returns:
            tuple: (response_message, updated_history)
        """
        if history is None:
            history = []
        
        # Get response using the graph
        response = self.chat(message, thread_id)
        
        # Update history
        updated_history = history.copy()
        updated_history.append({
            "user": message,
            "assistant": response
        })
        
        return response, updated_history
    
    def get_graph_state(self, thread_id: str = "default") -> Dict:
        """Get the current state of the conversation graph."""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            return self.graph.get_state(config)
        except Exception as e:
            return {"error": str(e)}
    
    def clear_history(self, thread_id: str = "default") -> bool:
        """Clear conversation history for a specific thread."""
        try:
            # Note: MemorySaver doesn't have a direct clear method
            # This would need to be implemented based on the checkpoint system
            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False

def create_agent() -> EduZenReActAgent:
    """Create and return a new EduZen ReAct agent instance."""
    return EduZenReActAgent()
