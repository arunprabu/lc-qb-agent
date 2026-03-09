def generate_grammar_mcqs(topic: str, difficulty: str, count: int = 5) -> str:
    """
    Generate grammar MCQs based on the given topic and difficulty level. 
    You should give 4 options for each question and also specify the correct answer. 
    
    Args:
        topic (str): The grammar topic for which to generate questions.
        difficulty (str): The difficulty level of the questions (e.g., "beginner", "intermediate", "advanced").
        count (int): The number of questions to generate. Default is 5.
    
    Returns:
        str: A string containing the generated MCQs in a structured format.
    """
    print(f"TOOL: Generating {count} {difficulty} MCQs for topic: {topic}")
    # For demonstration purposes, we'll return a static string.
    # In a real implementation, this function would use an LLM to generate questions dynamically.
    return f"10"