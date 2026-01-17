import { useState } from "react";

function TextInput({ onGenerate }: { onGenerate: (text: string) => void }) {
  const [input, setInput] = useState("");

  return (
    <section
      style={{
        width: "100%",
        maxWidth: "600px",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
      }}
    >
      <textarea
        placeholder='Paste lecture slide text here...'
        value={input}
        onChange={e => setInput(e.target.value)}
        style={{
          height: "300px",
          padding: "1rem",
          borderRadius: "1rem",
          border: "1px solid var(--clr-neutral-300)",
          backgroundColor: "var(--clr-neutral-100)",
          outline: "none",
        }}
      />
      <button
        onClick={() => onGenerate(input)}
        disabled={!input.trim()}
        style={{
          backgroundColor: "var(--clr-accent-400)",
          color: "var(--clr-neutral-100)",
          padding: "1rem",
          border: "none",
          borderRadius: "1rem",
        }}
      >
        Generate video
      </button>
    </section>
  );
}

export default TextInput;
