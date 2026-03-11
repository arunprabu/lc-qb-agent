from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from langchain.agents import create_agent
from .prompts import SYSTEM_PROMPT
from ..tools.grammar_tool import generate_grammar_mcqs
from ..tools.comprehension_tool import generate_comprehension_passages
from ..tools.validate_question_quality_tool import validate_question_quality

load_dotenv()

class QuestionOutput(BaseModel):
    question: str
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    # topic and difficulty are injected from run_agent params, not from LLM
    topic: Optional[str] = None
    difficulty: Optional[str] = None

class QuestionBankOutput(BaseModel):
    questions: List[QuestionOutput]

def build_agent():
    return create_agent(
        model="gpt-4o-mini",
        tools=[generate_grammar_mcqs, generate_comprehension_passages, validate_question_quality],
        system_prompt=SYSTEM_PROMPT,
        response_format=QuestionBankOutput
    )

async def run_agent(type: str, topic: str, difficulty: str, count: str):
    print(f"AGENT: Running agent for topic: {topic} with difficulty: {difficulty} and count: {count} and type: {type}")
    agent = build_agent()
    print("AGENT: Agent built successfully, invoking now...")
    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"Generate {count} {type} questions for the topic: {topic} with difficulty: {difficulty}"
            }
        ]
    })

    structured: QuestionBankOutput = result["structured_response"]
    print(f"AGENT: Structured output received: {structured}")

    # inject topic + difficulty (known from input) into each question for DB storage
    questions = [
        {**q.model_dump(), "topic": topic, "difficulty": difficulty}
        for q in structured.questions
    ]

    return {
        "message": "Agent execution complete at agent level",
        "questions": questions,
        "type": type,
        "topic": topic,
        "difficulty": difficulty,
        "count": count
    }