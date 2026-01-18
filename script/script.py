import anthropic

client = anthropic.Anthropic()

prompt = "binary search"

def generateScript(prompt):
    try:
        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            # system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
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