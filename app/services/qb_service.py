from app.agent.qb_agent import run_agent
from app.db.database import SessionLocal
from app.db.repository import create_grammar_questions, create_comprehension_questions

class QuestionBankService:

    async def execute_agent(self, type: str, topic: str, difficulty: str, count: str ):
        
        print(f"SERVICE: Executing agent for topic: {topic} with difficulty: {difficulty} and count: {count} and type: {type}")

        result = await run_agent(type, topic, difficulty, count)

        # lets connect to the db and save the questions to the database
        db = SessionLocal()
        
        try:
            if(type == "grammar"):
                status = create_grammar_questions(db, result['questions'])
            elif(type == "comprehension"):
                status = create_comprehension_questions(db, result['questions'])
            else:   
                print('unknown type - unable to save')
        except Exception as e:
            print("Error saving questions to the database: ", e)
        finally:
            db.close()

        return {
            "message": count + " " + status['message'],
            "type": type,
            "topic": topic,
            "difficulty": difficulty,
            "count": count
        }
