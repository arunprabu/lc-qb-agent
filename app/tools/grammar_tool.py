from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI
from ..agent.prompts import GRAMMAR_MCQS_TOOL_PROMPT_TEMPLATE
import os 
from dotenv import load_dotenv

load_dotenv()

class GrammarMCQ(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str
    topic: str

class GrammarMCQListOutput(BaseModel):
    questions: List[GrammarMCQ]

def generate_grammar_mcqs(topic: str, difficulty: str, count: int = 5) -> str:
    """
    Generate grammar MCQs based on the given topic and difficulty level. 
    You should give 4 options for each question and also specify the correct answer. 
    
    Args:
        topic (str): The grammar topic for which to generate questions.
        difficulty (str): The difficulty level of the questions (e.g., "beginner", "intermediate", "advanced").
        count (int): The number of questions to generate. Default is 5.
    """
    print(f"TOOL: Generating {count} {difficulty} MCQs for topic: {topic}")

    # let's connect to LLM and generate questions based on the topic and difficulty
    max_tokens = int(os.getenv("MAX_TOKENS_FROM_TOOLS", 1500))
    llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=max_tokens, temperature=0.5)
    # telling llm to produce output in a structured format that matches our GrammarMCQListOuput model
    structured_llm = llm.with_structured_output(GrammarMCQListOutput)

    # Let's invoke with a prompt
    result:GrammarMCQListOuput = structured_llm.invoke(GRAMMAR_MCQS_TOOL_PROMPT_TEMPLATE)

    # print(f"TOOL: Generated questions: {result}")
    return result.json()