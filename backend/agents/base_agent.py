"""
Base agent class with common functionality
"""
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from ..config import settings


class BaseAgent:
    """
    Base class for all Fiscal Pilot agents
    Provides LLM initialization and common utilities
    """
    
    def __init__(self, agent_name: str, model_name: str = "llama-3.1-70b-versatile"):
        """
        Initialize base agent
        
        Args:
            agent_name: Name of the agent (for logging/identification)
            model_name: Groq model to use
        """
        self.agent_name = agent_name
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=model_name,
            temperature=0.3,  # Lower temperature for more deterministic outputs
        )
        self.conversation_history: List[Dict[str, str]] = []
    
    def _build_prompt(self, system_prompt: str, user_message: str) -> List:
        """Build prompt for LLM"""
        return [
            ("system", system_prompt),
            ("user", user_message),
        ]
    
    def _call_llm(self, prompt: List, response_format: Optional[str] = None) -> str:
        """
        Call LLM with error handling
        
        Args:
            prompt: Formatted prompt
            response_format: Optional format constraint (e.g., "json")
            
        Returns:
            LLM response text
        """
        try:
            messages = [
                HumanMessage(content=msg[1]) if msg[0] == "user" 
                else AIMessage(content=msg[1]) if msg[0] == "assistant"
                else HumanMessage(content=msg[1])
                for msg in prompt
            ]
            # Insert system message
            system_content = next((msg[1] for msg in prompt if msg[0] == "system"), "")
            if system_content:
                messages.insert(0, HumanMessage(content=f"System: {system_content}"))
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            # Fallback: return safe error message
            return f"Error in {self.agent_name}: {str(e)}"
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Attempt to parse JSON from response"""
        import json
        import re
        
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        # If no JSON found, return as text
        return {"raw_response": response}
    
    def log_decision(self, decision_type: str, inputs: Dict, outputs: Dict, confidence: float = 0.8):
        """Log agent decision (will be stored by orchestrator)"""
        return {
            "agent": self.agent_name,
            "decision_type": decision_type,
            "inputs": inputs,
            "outputs": outputs,
            "confidence": confidence,
        }
