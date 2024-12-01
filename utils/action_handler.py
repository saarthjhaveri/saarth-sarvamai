from typing import Dict, Any, Optional, List
from openai import OpenAI
import json
from pydantic import BaseModel

class ActionInput(BaseModel):
    section: Optional[str] = None
    topic: Optional[str] = None
    difficulty_level: Optional[str] = None
    num_questions: Optional[int] = None
    format_type: Optional[str] = None
    search_term: Optional[str] = None

class ActionHandler:
    def __init__(self, pdf_processor=None):
        self.client = OpenAI()
        self.pdf_processor = pdf_processor
        
        # Define available functions/tools
        self.available_functions = {
            "generate_study_material": self.generate_study_material,
            "search_content": self.search_content,
            "create_quiz": self.create_quiz,
            "analyze_content": self.analyze_content
        }
        
        # Define function schemas for OpenAI
        self.function_descriptions = [
            {
                "name": "generate_study_material",
                "description": "Generate study materials like summaries, flashcards, or mind maps",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "section": {
                            "type": "string",
                            "description": "The specific section or topic to generate material for"
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["summary", "flashcards", "mind_map", "notes"],
                            "description": "The format of study material to generate"
                        }
                    },
                    "required": ["format_type"]
                }
            },
            {
                "name": "create_quiz",
                "description": "Generate practice questions or quizzes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to create questions about"
                        },
                        "difficulty_level": {
                            "type": "string",
                            "enum": ["easy", "medium", "hard"],
                            "description": "The difficulty level of questions"
                        },
                        "num_questions": {
                            "type": "integer",
                            "description": "Number of questions to generate",
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["num_questions", "difficulty_level"]
                }
            },
            {
                "name": "search_content",
                "description": "Search for specific information or patterns in the document",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "The term or pattern to search for"
                        }
                    },
                    "required": ["search_term"]
                }
            },
            {
                "name": "analyze_content",
                "description": "Analyze content for patterns, relationships, or specific aspects",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "section": {
                            "type": "string",
                            "description": "The section to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["key_concepts", "numerical_data", "relationships", "examples"],
                            "description": "Type of analysis to perform"
                        }
                    },
                    "required": ["analysis_type"]
                }
            }
        ]

    async def determine_action(self, query: str) -> Dict[str, Any]:
        """Use OpenAI's function calling to determine the appropriate action"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "You are an intelligent study assistant that helps students learn from PDF documents. Determine the most appropriate action based on the user's query."},
                    {"role": "user", "content": query}
                ],
                functions=self.function_descriptions,
                function_call="auto"
            )

            if response.choices[0].message.function_call:
                function_name = response.choices[0].message.function_call.name
                function_args = json.loads(response.choices[0].message.function_call.arguments)
                return {
                    "action": function_name,
                    "parameters": function_args
                }
            return None

        except Exception as e:
            print(f"Error in determine_action: {str(e)}")
            return None

    async def execute_action(self, action: str, parameters: Dict[str, Any], context: str = None) -> Dict[str, Any]:
        """Execute the specified action with given parameters"""
        if action not in self.available_functions:
            raise ValueError(f"Unknown action: {action}")
            
        result = await self.available_functions[action](parameters, context)
        return {
            "action": action,
            "parameters": parameters,
            "result": result,
            "context_used": context is not None
        }

    async def generate_study_material(self, params: Dict[str, Any], context: str = None) -> str:
        format_type = params.get("format_type")
        section = params.get("section", "")
        
        prompt = f"""Generate {format_type} for the following content.
        Make it engaging and easy to understand.
        
        Content: {context}
        Section focus: {section}
        
        Format as a structured {format_type}:"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert study material creator."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def create_quiz(self, params: Dict[str, Any], context: str = None) -> str:
        difficulty = params.get("difficulty_level", "medium")
        num_questions = params.get("num_questions", 3)
        topic = params.get("topic", "")
        
        prompt = f"""Create {num_questions} {difficulty}-level questions about {topic}.
        Base the questions on this content: {context}
        
        Include:
        - Multiple choice options
        - Correct answer
        - Brief explanation
        
        Format as JSON with 'questions' array."""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert question creator."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def search_content(self, params: Dict[str, Any], context: str = None) -> str:
        search_term = params.get("search_term", "")
        
        # Use the PDF processor's collection to search
        if self.pdf_processor and self.pdf_processor.collection:
            results, is_relevant = query_similar_chunks(search_term, self.pdf_processor.collection)
            return json.dumps({
                "search_term": search_term,
                "results": results['documents'][0] if results['documents'] else [],
                "is_relevant": is_relevant
            })
        return "PDF processor not initialized"

    async def analyze_content(self, params: Dict[str, Any], context: str = None) -> str:
        analysis_type = params.get("analysis_type")
        section = params.get("section", "")
        
        prompt = f"""Analyze the following content for {analysis_type}.
        Section focus: {section}
        
        Content: {context}
        
        Provide a detailed analysis focusing on {analysis_type}:"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert content analyzer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content