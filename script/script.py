import anthropic

client = anthropic.Anthropic()

prompt = """
    Give me a 30-second script for a Kitty Explains video on binary search. The
    script should do the following things:
    1. Summarise the content decently
    2. Be humorous 
    3. Refer to kitty as "Kitty"
    
    Some example sentences are: "Kitty wants to find his car in a crowded parking lot.
    Kitty knows that the licence plates are sorted."

    Give me the pure script, no headers, introduction, comments, nothing.
    """

def generateScript(prompt):
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    if len(message.content) == 0:
        return ""

    return message.content[0].text