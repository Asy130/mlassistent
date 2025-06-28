def format_initial_user_prompt(user_prompt: str, user_form: str) -> str:
    """
    Formats the initial user query with their form data
    
    Args:
        user_prompt: User's question
        user_form: User's form data
        
    Returns:
        str: Formatted query string
    """
    return (
        "User form data:\n"
        f"{user_form}\n\n"
        "User question:\n"
        f"{user_prompt}\n\n"
        "Please provide a detailed response considering the user's profile."
    )
