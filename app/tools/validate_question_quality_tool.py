"""
Validate question quality
this tool will check the quality of the generated questions based on certain criteria 
such as relevance, clarity, difficulty level, and correctness.
it will take the generated questions as input and evaluate them against these criteria, 
providing feedback on how well the questions meet the desired standards and where they can be improved.
if the questions do not meet the quality standards, the tool itself will rewrite 
the questions to improve their quality and ensure they are suitable for use in the question bank."""


# Plan A: create this tool - program this to check the quality and rewrite the questions if they do not meet the quality standards.
# Plan B: create this tool - program this to check the quality and provide feedback for improvement, but do not rewrite the questions. 
# The agent will have to rewrite the questions itself based on the feedback provided by the tool. 
# This will be a more complex implementation but will allow us to test the agent's 
# ability to improve its own output based on feedback.


from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI
from ..agent.prompts import VALIDATE_QUESTION_QUALITY_PROMPT_TEMPLATE

import os
from dotenv import load_dotenv

load_dotenv()

class ValidationResult(BaseModel):
    is_valid: bool
    feedback: str
    original_questions: List[str]
    improved_questions: List[str] = []

def validate_question_quality(questions: List[str], type: str, topic: str, difficulty: str, count: int = 5) -> ValidationResult:
  """Validate the quality of the generated questions based on relevance, clarity, difficulty level, and correctness."""

  print(f"TOOL: Validating quality of {len(questions)} questions for topic: {topic} with difficulty: {difficulty} and type: {type}")
  max_tokens = int(os.getenv("MAX_TOKENS_FROM_TOOLS", 1500))
  llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=max_tokens, temperature=0.5)
  structured_llm = llm.with_structured_output(ValidationResult)

  result: ValidationResult = structured_llm.invoke(VALIDATE_QUESTION_QUALITY_PROMPT_TEMPLATE + "\n\n" + "\n".join(questions))
  return result.json()