# insert logic only 
# for other actions such as get all questions, get question by id, update question, delete question -- you have to implement the logic without agent

from sqlalchemy.orm import Session
from ..models.qb_grammar import GrammarQuestion
from ..models.qb_comprehension import ComprehensionQuestion

# let's save the grammar questions to the database
def create_grammar_questions(db: Session, questions: list[dict]):
    print("IN REPOSITY: Before Saving the Grammar Questions =======")
    for q in questions:
        question = GrammarQuestion(
            topic=q.get("topic"),
            difficulty=q.get("difficulty"),
            question=q.get("question"),
            options=q.get("options"),
            correct_answer=q.get("correct_answer"),
            explanation=q.get("explanation")
        )
        db.add(question)

    print("IN REPOSITY: About to Save the Grammar Questions =======")
    # commit the transaction to save the questions to the database
    db.commit()

    # refresh all instances to get the generated ids and return them
    return {
        "message": "Grammar questions saved successfully"
    }


def create_comprehension_questions(db: Session, questions: list[dict]):
    print("IN REPOSITORY: Before Saving the Comprehension Questions =======")
    for q in questions:
        question = ComprehensionQuestion(
            topic=q.get("topic"),
            difficulty=q.get("difficulty"),
            passage=q.get("passage"),
            question=q.get("question"),
            options=q.get("options"),
            correct_answer=q.get("correct_answer"),
            explanation=q.get("explanation"),
        )
        db.add(question)

    print("IN REPOSITORY: About to Save the Comprehension Questions =======")
    db.commit()

    return {
        "message": "Comprehension questions saved successfully"
    }

