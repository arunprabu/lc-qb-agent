#

# QB Agent 
# =====
#   model = gpt-4o-mini 
#   system_prompt = ""

#   tools 
#     1. Generate grammar MCQs
#     2. Generate comprehension passages
#     3. Validate question quality
#     4. Store in MongoDB

from dotenv import load_dotenv
import os
from langchain.agents import create_agent
from .prompts import SYSTEM_PROMPT
from ..tools.grammar_tool import generate_grammar_mcqs

load_dotenv()

def build_agent(topic: str, difficulty: str):
    print(f"AGENT: Building agent for topic: {topic} with difficulty: {difficulty}")
    
    question_bank_agent = create_agent(
        model="gpt-4o-mini",
        tools=[generate_grammar_mcqs],
        system_prompt=SYSTEM_PROMPT
    )

    return question_bank_agent

async def run_agent(topic: str, difficulty: str):
    print(f"AGENT: Running agent for topic: {topic} with difficulty: {difficulty}")
    agent = build_agent(topic, difficulty)
    print("AGENT: Agent built successfully, invoking now...")
    result = agent.invoke({
      "messages": [
        {
          "role": "user", 
          "content": "Generate questions for the topic: " + topic + " with difficulty: " + difficulty
        }
      ]
    })

    print(f"AGENT: Agent invocation complete. Result: {result['messages'][-1].content}")

    # let's return this result back to the service layer and then to the route and then to the client
    return {
        "message": "Agent execution complete at agent level",
        "agent_response": result['messages'][-1].content,
        "topic": topic,
        "difficulty": difficulty
    }
