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
    def __init__(self, personality):
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.personality = personality
        self.business_summary = self._load_business_summary()
        self.instructions = self._load_instructions()
        self.personality_style = self._load_personality(personality)

        self.tools = [record_students_lead, record_workshops_lead, record_feedback]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.graph = self._build_graph()
    
    def _load_business_summary(self) -> str:
        try:
            with open("../me/business_summary.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "EduZen Agency - Educational services provider"
    
    def _load_instructions(self) -> str:
        try:
            with open("../prompts/instructions.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "Provide helpful assistance with educational services."
    
    def _load_personality(self, personality: str) -> str:
        try:
            with open(f"../prompts/personalities/{personality}.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
           return "Be helpful and professional."
    
    def _create_system_prompt(self) -> str:
        return f" {self.business_summary} \n {self.instructions} \n {self.personality_style}"

    def _build_graph(self) -> StateGraph:
        
        def reasoning_node(state: MessagesState):
            messages = state["messages"]
            reasoning_prompt = ChatPromptTemplate.from_messages([
                ("system", self._create_system_prompt()),
                ("human", "Think step by step about this request. What is the user asking for? What action should I take?\n\nUser message: {input}"),
            ])
            latest_message = messages[-1].content if messages else ""
            reasoning_chain = reasoning_prompt | self.llm # Langchain pipe operator
            reasoning_response = reasoning_chain.invoke({"input": latest_message})
            response = AIMessage(content=f"THINKING: {reasoning_response.content}")
            return {
                "messages": messages + [response],
            }
        
        def agent_node(state: MessagesState):
            messages = state["messages"]
            formatted_messages = [
                SystemMessage(content=self._create_system_prompt())
            ] + messages
            response = self.llm_with_tools.invoke(formatted_messages)
            return {"messages": messages + [response]}
        
        def should_continue(state: MessagesState):
            """Determine if we should continue with tool calls or end."""
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END
        
        workflow = StateGraph(MessagesState)
        
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        workflow.set_entry_point("reasoning")
        
        workflow.add_edge("reasoning", "agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def chat(self, message: str, thread_id: str = "default") -> tuple[str, List[str]]:
        try:
            input_data = { "messages": [HumanMessage(content=message)]}
            config = {"configurable": {"thread_id": thread_id}}
            result = self.graph.invoke(input_data, config)
            
            # Collect all reasoning steps and final response
            reasoning_steps = []
            final_response = ""
            
            # Extract all AI messages from the result
            for msg in result["messages"]:
                if isinstance(msg, AIMessage):
                    if msg.content.startswith("THINKING:"):
                        # Extract reasoning step
                        reasoning_steps.append(msg.content.replace("THINKING:", "").strip())
                    else:
                        # This is the final response
                        final_response = msg.content
            
            # Return final answer and reasoning steps as separate values
            if not final_response:
                final_response = "I apologize, but I encountered an issue processing your request. Please try again."
            
            return final_response, reasoning_steps
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}. Please try again or contact our support team."
            return error_msg, []
    
    def chat_with_history(self, message: str, history: List[Dict[str, str]] = None, thread_id: str = "default") -> tuple[tuple[str, List[str]], List[Dict[str, str]]]:
        if history is None: history = []
        final_answer, reasoning_steps = self.chat(message, thread_id)
        updated_history = history.copy()
        updated_history.append({
            "user": message,
            "assistant": final_answer,
            "reasoning": reasoning_steps
        })
        return (final_answer, reasoning_steps), updated_history
    
    def get_graph_state(self, thread_id: str = "default") -> Dict:
        try:
            config = {"configurable": {"thread_id": thread_id}}
            return self.graph.get_state(config)
        except Exception as e:
            return {"error": str(e)}
    
    def clear_history(self, thread_id: str = "default") -> bool:
        """Clear conversation history for a specific thread."""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            current_state = self.graph.get_state(config)
            
            if current_state is None or not hasattr(current_state, 'values'):
                # Thread doesn't exist or is already empty
                return True
            
            empty_state = {"messages": []}
            self.graph.update_state(config, empty_state)
            return True
            
        except Exception as e:
            print(f"Error clearing history for thread '{thread_id}': {e}")
            return False

def create_agent(personality):
    return EduZenReActAgent(personality)