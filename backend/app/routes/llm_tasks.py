from openai import OpenAI
from pydantic import BaseModel
import os

class MethodDetails(BaseModel):
    description: str
    time_complexity: str
    space_complexity: str

class LLMAnalysisResponse(BaseModel):
    file_description: str
    methods: dict[str, MethodDetails]


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_code_with_llm(code: str, methods: list[str], file_extension: str) -> LLMAnalysisResponse:
    """
    Uses OpenAI's LLM to analyze code, generating a file-level description and method-level details.
    """
    prompt = (
        f"""
        You are an expert software engineer. Analyze the following {file_extension} code and provide:
        1. A high-level description of what the file does.
        2. For each function/method, provide a brief description, estimated time complexity, and space complexity.

        Code:
        {code}

        Output format:
        {{
            "file_description": "...",
            "methods": {{
                "method_name": {{
                    "description": "...",
                    "time_complexity": "...",
                    "space_complexity": "..."
                }}
            }}
        }}
        """
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant specialized in code analysis."},
            {"role": "user", "content": prompt}
        ]
    )
    
    result = response.choices[0].message.content
    cleaned_result = result.strip().strip("```json").strip("```")
    return LLMAnalysisResponse.parse_raw(cleaned_result)


def generate_suggestion_with_llm(method_name: str, method_details: dict[str, str], code: str) -> str:
    """
    Uses OpenAI's LLM to generate suggestions for improving a specific method.
    """
    prompt = (
        f"""
        You are a Principle software engineer. Provide improvement suggestions for the method "{method_name}".

        Method details:
        Description: {method_details.description}
        Time Complexity: {method_details.time_complexity}
        Space Complexity: {method_details.space_complexity}

        Code:
        {code}

        Output format:
        "Suggestion: ..."
        """
    )
    
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant specialized in code optimization."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
