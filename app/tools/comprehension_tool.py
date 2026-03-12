from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI
from ..agent.prompts import COMPREHENSION_PASSAGE_TOOL_PROMPT_TEMPLATE
import os
from dotenv import load_dotenv

load_dotenv()

# pydantic models to define the structure of the comprehension passage and questions
class ComprehensionQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str

class ComprehensionPassage(BaseModel):
    passage: str
    questions: List[ComprehensionQuestion]


def generate_comprehension_passages(topic: str, difficulty: str, count: int = 1) -> str:
    """
    Generate comprehension passages based on the given topic and difficulty level. 
    Each passage should be followed by 3-5 questions that test the reader's understanding of the passage.
    
    Args:
        topic (str): The topic for which to generate comprehension passages.
        difficulty (str): The difficulty level of the passages (e.g., "beginner", "intermediate", "advanced").
        count (int): The number of passages to generate. Default is 1.
    """

    print(f"TOOL: Generating {count} {difficulty} comprehension passages for topic: {topic}")

    # let's connect to LLM and generate questions based on the topic and difficulty
    max_tokens = int(os.getenv("MAX_TOKENS_FROM_TOOLS", 1500))
    llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=max_tokens, temperature=0.5)
    # telling llm to produce output in a structured format that matches our Passage model
    structured_llm = llm.with_structured_output(ComprehensionPassage)

    # Let's invoke with a prompt
    result:ComprehensionPassage = structured_llm.invoke(COMPREHENSION_PASSAGE_TOOL_PROMPT_TEMPLATE)

    return result.json()