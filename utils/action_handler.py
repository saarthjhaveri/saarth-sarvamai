from typing import Dict, Any, Optional
from openai import OpenAI
import json
from pydantic import BaseModel

class ActionHandler:
    def __init__(self, pdf_processor=None):
        self.client = OpenAI()
        self.pdf_processor = pdf_processor
        
        # Define tool schemas for analysis
        self.tool_schemas = {
            "flashcards": {
                "name": "create_flashcards",
                "description": "Create flashcards for key concepts and terms",
                "parameters": {
                    "concept": "string",
                    "num_cards": "integer (optional)"
                }
            },
            "practice_problems": {
                "name": "generate_practice",
                "description": "Generate practice problems with step-by-step solutions",
                "parameters": {
                    "topic": "string",
                    "difficulty": "string (basic/intermediate/advanced)"
                }
            },
            "concept_map": {
                "name": "create_concept_map",
                "description": "Create a visual map showing relationships between concepts",
                "parameters": {
                    "central_concept": "string",
                    "depth": "integer (optional)"
                }
            },
            "summary": {
                "name": "generate_summary",
                "description": "Create a structured summary with key points and examples",
                "parameters": {
                    "topic": "string",
                    "format": "string (brief/detailed)"
                }
            }
        }

    async def analyze_query_for_tools(self, query: str) -> Dict[str, Any]:
        """Analyze if the query would benefit from using a learning tool"""
        try:
            prompt = f"""Analyze this query to determine if a learning tool would be helpful.It is not neccessary that every query needs learning tool hence respond accordingly.
            Query: {query}
            
            Available tools:
            {json.dumps(self.tool_schemas, indent=2)}
            
            Respond in JSON format with:
            - should_use_tool (boolean)
            - tool (string, name of tool if should_use_tool is true)
            - parameters (object with required parameters if should_use_tool is true)
            - confidence (float between 0 and 1)
            - reasoning (string explaining the decision)
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a learning assistant that analyzes queries for potential tool usage."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error in analyze_query_for_tools: {str(e)}")
            return {
                "should_use_tool": False,
                "confidence": 0.0,
                "reasoning": f"Error during analysis: {str(e)}"
            }

    async def execute_action(self, tool: str, parameters: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Execute the specified tool action"""
        tool_functions = {
            "create_flashcards": self._create_flashcards,
            "generate_practice": self._generate_practice_problems,
            "create_concept_map": self._create_concept_map,
            "generate_summary": self._generate_summary
        }
        
        if tool not in tool_functions:
            raise ValueError(f"Unknown tool: {tool}")
            
        result = await tool_functions[tool](parameters, context)
        print("result from tool functions is ", result )
        return result

    async def generate_tool_response(self, query: str, tool_result: Dict[str, Any], tool: str) -> str:
        """Generate a natural language response incorporating the tool result"""
        prompt = f"""Generate a helpful response to the user's query that incorporates the tool results.
        Query: {query}
        Tool Used: {tool}
        Tool Results: {json.dumps(tool_result, indent=2)}
        
        Provide a natural, conversational response that:
        1. Acknowledges the user's question
        2. Explains what was created/generated
        3. Guides them on how to use the results
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful learning assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    async def _create_flashcards(self, parameters: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Create flashcards from the content"""
        prompt = f"""Create flashcards for learning about {parameters.get('concept')}.
        Use this content as reference: {context}
        
        Generate {parameters.get('num_cards', 5)} flashcards in this JSON format:
        {{
            "flashcards": [
                {{"front": "question/term", "back": "answer/definition"}}
            ]
        }}
        
        Make the cards clear, concise, and focused on key concepts."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at creating educational flashcards."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return json.loads(response.choices[0].message.content)

    async def _generate_practice_problems(self, parameters: Dict[str, Any], context: str) -> Dict[str, Any]:
       
        """Generate practice problems with solutions"""
        try:
            prompt = f"""Create practice problems about {parameters.get('topic')} at {parameters.get('difficulty')} level.
            Use this content as reference: {context}
            
            Generate problems in this JSON format:
            {{
                "problems": [
                    {{
                        "question": "problem statement",
                        "solution": "step-by-step solution",
                        "final_answer": "the answer",
                        "explanation": "explanation of concepts used"
                    }}
                ]
            }}"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at creating educational practice problems."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            print("practice problems result is ", response)
            return json.loads(response.choices[0].message.content)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return {"error": "Failed to parse response", "details": str(e)}
        except Exception as e:
            print(f"Error generating practice problems: {str(e)}")
            return {"error": "Failed to generate practice problems", "details": str(e)}
        
    async def _create_concept_map(self, parameters: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Create a concept map showing relationships"""
        prompt = f"""Create a concept map centered on {parameters.get('central_concept')}.
        Use this content as reference: {context}
        
        Generate the concept map in this JSON format:
        {{
            "central_concept": "main topic",
            "connections": [
                {{
                    "concept": "related concept",
                    "relationship": "how it relates",
                    "sub_concepts": ["more specific ideas"]
                }}
            ]
        }}"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at creating concept maps."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return json.loads(response.choices[0].message.content)

    async def _generate_summary(self, parameters: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Generate a structured summary"""
        prompt = f"""Create a {parameters.get('format', 'detailed')} summary about {parameters.get('topic')}.
        Use this content as reference: {context}
        
        Generate the summary in this JSON format:
        {{
            "main_points": ["key ideas"],
            "details": {{
                "concept": "explanation"
            }},
            "examples": ["relevant examples"],
            "additional_notes": "any important considerations"
        }}"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at creating educational summaries."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return json.loads(response.choices[0].message.content)