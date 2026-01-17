import anthropic

client = anthropic.Anthropic()

prompt = "binary search"

def generateScript(prompt):
    # system_prompt = (
    #     "You are a humorous and concise script writer for short educational videos. "
    #     "Your scripts feature a cat named 'Kitty' who explains concepts clearly and humorously. "
    #     "Always produce only the script text, without headers, introductions, or comments."
    #     "Don't insult the audience, be nice."
    # )

    user_prompt = (
        f"""
        Write a 30-second script for a 'Kitty Explains' video on the following topic: {prompt}. 
        The script should:
        1. Summarize the content decently.
        2. Be humorous.
        3. Refer to the cat as "Kitty".

        Example sentences for style: 
        "Kitty wants to find his car in a crowded parking lot. Kitty knows that the license plates are sorted."

        Produce only the script, nothing else.
        """
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            # system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
    except Exception as e:
        print("Error:", e)
        return ""

    return "".join(block.text.strip() for block in message.content if block.type == "text")

def main():
    script = generateScript(prompt)
    print(script)

if __name__ == "__main__":
    main()