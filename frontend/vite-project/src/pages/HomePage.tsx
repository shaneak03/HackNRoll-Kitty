import { useState } from "react";

function TextInput({ 
  onGenerate 
}: { 
  onGenerate: (text: string, file?: File) => void;
}) {
  const [input, setInput] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const extension = file.name.split('.').pop()?.toLowerCase();
      
      if (!['pdf', 'pptx', 'ppt'].includes(extension || '')) {
        alert('Please upload a PDF or PowerPoint file');
        return;
      }
      
      setSelectedFile(file);
      setInput(""); // Clear text input when file is selected
    }
  };

  const handleSubmit = () => {
    if (selectedFile) {
      onGenerate("", selectedFile);
    } else if (input.trim()) {
      onGenerate(input);
    }
  };

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
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <textarea
          placeholder='Paste lecture slide text here...'
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={!!selectedFile}
          style={{
            height: "300px",
            minHeight: "200px",
            padding: "1rem",
            borderRadius: "1rem",
            border: "1px solid var(--clr-neutral-300)",
            backgroundColor: selectedFile ? "var(--clr-neutral-200)" : "var(--clr-neutral-100)",
            outline: "none",
            opacity: selectedFile ? 0.5 : 1,
            resize: "vertical",
          }}
        />
        
        <div style={{ 
          textAlign: "center", 
          color: "var(--clr-neutral-600)",
          fontSize: "0.9rem",
          fontWeight: 500
        }}>
          OR
        </div>
        
        <label style={{
          padding: "1.5rem",
          borderRadius: "1rem",
          border: "2px dashed var(--clr-neutral-300)",
          cursor: "pointer",
          textAlign: "center",
          backgroundColor: selectedFile ? "var(--clr-accent-100)" : "transparent",
          transition: "all 0.2s",
          fontWeight: 500,
        }}>
          <input
            type="file"
            accept=".pdf,.pptx,.ppt"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
          {selectedFile ? (
            <span style={{ color: "var(--clr-accent-600)" }}>📄 {selectedFile.name}</span>
          ) : (
            <span style={{ color: "var(--clr-neutral-600)" }}>📎 Upload PDF or PowerPoint</span>
          )}
        </label>
        
        {selectedFile && (
          <button
            onClick={() => {
              setSelectedFile(null);
              setInput("");
            }}
            style={{
              padding: "0.5rem",
              backgroundColor: "transparent",
              border: "1px solid var(--clr-neutral-300)",
              borderRadius: "0.5rem",
              cursor: "pointer",
              color: "var(--clr-neutral-600)",
            }}
          >
            ✕ Clear file
          </button>
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={!input.trim() && !selectedFile}
        style={{
          backgroundColor: "var(--clr-accent-400)",
          color: "var(--clr-neutral-100)",
          padding: "1rem",
          border: "none",
          borderRadius: "1rem",
          cursor: (!input.trim() && !selectedFile) ? "not-allowed" : "pointer",
          opacity: (!input.trim() && !selectedFile) ? 0.5 : 1,
        }}
      >
        Generate video
      </button>
    </section>
  );
}

export default TextInput;
