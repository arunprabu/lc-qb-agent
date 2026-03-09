from app.agent.qb_agent import run_agent

class QuestionBankService:

    async def execute_agent(self, topic: str, difficulty: str):
        print(f"SERVICE: Executing agent for topic: {topic} with difficulty: {difficulty}")

        result = await run_agent(topic, difficulty)
        return {
            "message": "Agent execution complete at service level",
            "agent_response": result['agent_response'],
            "topic": topic,
            "difficulty": difficulty
        }