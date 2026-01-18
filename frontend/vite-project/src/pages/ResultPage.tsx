function ResultView({ onReset }: { videoUrl: string; onReset: () => void; }) {
  const VIDEO_PATH = "http://localhost:2025/video";

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
          display: "flex",
          justifyContent: "center", // horizontal centering
          width: "100%",
        }}
      >
        <video
          src={VIDEO_PATH}
          controls
          muted
          playsInline
          style={{
            width: "320px",
            borderRadius: "12px",
            boxShadow: "0 8px 30px rgba(0,0,0,0.25)",
          }}
        />
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
            fetch(VIDEO_PATH)
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
