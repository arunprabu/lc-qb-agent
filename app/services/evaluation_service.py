from app.agent.evaluation_agent import run_evaluation_agent

class EvaluationService:
    """Service to handle evaluation requests using the evaluation agent"""

    async def execute_evaluation(self, evaluation_type: str, **kwargs):
        """
        Execute evaluation using the evaluation agent.
        
        Args:
            evaluation_type: Type of evaluation ("grammar", "reading", or "listening")
            **kwargs: Additional parameters specific to evaluation type
        
        Returns:
            dict: Evaluation results
        """
        print(f"EVALUATION_SERVICE: Executing evaluation for type: {evaluation_type}")

        result = await run_evaluation_agent(evaluation_type, **kwargs)

        return {
            "message": f"Evaluation completed successfully",
            "evaluation_type": evaluation_type,
            "status": "success",
            "data": result.get("evaluation")
        }
