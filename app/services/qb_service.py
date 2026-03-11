from app.agent.qb_agent import run_agent

class QuestionBankService:

    async def execute_agent(self, type: str, topic: str, difficulty: str, count: str ):
        
        print(f"SERVICE: Executing agent for topic: {topic} with difficulty: {difficulty} and count: {count} and type: {type}")

        result = await run_agent(type, topic, difficulty, count)
        return {
            "message": "Agent execution complete at service level",
            "questions": result['questions'],
            "type": type,
            "topic": topic,
            "difficulty": difficulty,
            "count": count
        }
