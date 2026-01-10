"""
Compliance Guard Agent
Ensures output is educational, not advisory
"""
from typing import Dict, Any
from .base_agent import BaseAgent


class ComplianceGuardAgent(BaseAgent):
    """
    Agent responsible for:
    - Checking all outputs for compliance
    - Blocking unsafe responses
    - Ensuring educational (not advisory) tone
    - Verifying no guarantees or promises
    """
    
    def __init__(self):
        super().__init__("ComplianceGuardAgent")
        self.system_prompt = """You are a Compliance Guard Agent for Fiscal Pilot.
Your CRITICAL role is to ensure all outputs are compliant and safe.

YOU MUST BLOCK OR FLAG:
1. Any guarantees of returns or profits
2. Specific investment recommendations ("Buy X", "Sell Y")
3. Promises about future performance
4. Claims that sound like financial advice
5. Statements that could be misconstrued as advisory
6. Predictions about market movements
7. Specific return percentages or numbers

YOU MUST ENSURE:
1. Language is educational, not advisory
2. Disclaimers are present
3. Risk warnings are clear
4. No guarantees are made
5. User is reminded to consult professionals
6. Tone is informational, not directive

Return JSON with compliance check results."""

    def check_compliance(self, agent_output: Dict[str, Any], agent_name: str, 
                        output_text: str = None) -> Dict[str, Any]:
        """
        Check agent output for compliance
        
        Args:
            agent_output: Output dictionary from agent
            agent_name: Name of agent that produced output
            output_text: Optional raw text output to check
            
        Returns:
            Compliance check result
        """
        # Convert output to text for analysis
        if output_text is None:
            import json
            output_text = json.dumps(agent_output, indent=2)
        
        user_message = f"""Check this output from {agent_name} for compliance:

OUTPUT TEXT:
{output_text[:2000]}  # Limit to avoid token limits

Check for:
1. Guarantees or promises
2. Specific investment recommendations
3. Return predictions
4. Advisory language
5. Missing disclaimers
6. Risk warnings adequacy

Return JSON:
{{
    "compliant": <true|false>,
    "issues_found": [
        {{
            "severity": "<critical|warning|minor>",
            "issue": "<description>",
            "location": "<where in output>",
            "suggestion": "<how to fix>"
        }}
    ],
    "block_output": <true|false>,  // true if critical issues
    "suggested_fixes": {{
        "<key>": "<fixed value or note>"
    }},
    "compliance_notes": "<overall compliance assessment>"
}}"""
        
        prompt = self._build_prompt(self.system_prompt, user_message)
        response = self._call_llm(prompt)
        result = self._parse_json_response(response)
        
        # Default to compliant if parsing fails
        compliant = result.get("compliant", True)
        if not isinstance(compliant, bool):
            # Try to infer from issues
            issues = result.get("issues_found", [])
            critical_issues = [i for i in issues if i.get("severity") == "critical"]
            compliant = len(critical_issues) == 0
        
        return {
            "compliant": compliant,
            "issues_found": result.get("issues_found", []),
            "block_output": result.get("block_output", False),
            "suggested_fixes": result.get("suggested_fixes", {}),
            "compliance_notes": result.get("compliance_notes", "Output appears compliant"),
            "checked_agent": agent_name,
        }
