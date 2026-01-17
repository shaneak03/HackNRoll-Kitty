function ResultView({ onReset }: { videoUrl: string; onReset: () => void; }) {
  return (
    <section
      style={{
        textAlign: "center",
        display: "flex",
        flexDirection: "column",
        gap: "1.5rem",
      }}
    >
      <div
        style={{
          padding: "2rem",
          border: "2px solid var(--clr-accent-400)",
          borderRadius: "12px",
        }}
      >
        <h2 style={{ color: "var(--clr-accent-400)" }}>Video Ready!</h2>
      </div>

      <div style={{ display: "flex", gap: "1rem" }}>
        <button
          style={{
            backgroundColor: "var(--clr-neutral-800)",
            color: "var(--clr-neutral-100)",
            padding: "1rem 2rem",
            borderRadius: "8px",
            textDecoration: "none",
          }}
          onClick={() => {
            // Fetch the video from backend
            fetch("http://localhost:2025/video")
              .then(res => res.blob())
              .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "kitty_explains.mp4";
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
              });
          }}
        >
          Download Video
        </button>

        <button
          onClick={onReset}
          style={{
            backgroundColor: "transparent",
            border: "1px solid var(--clr-neutral-700)",
            padding: "1rem 2rem",
            borderRadius: "8px",
          }}
        >
          Generate Again
        </button>
      </div>
    </section>
  );
}

export default ResultView;
