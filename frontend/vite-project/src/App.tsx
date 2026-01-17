import { useState } from "react";
import TextInput from "./pages/HomePage";
import LoadingState from "./pages/LoadingPage";
import ResultView from "./pages/ResultPage";

// Define the possible UI states
type AppState = "INPUT" | "LOADING" | "RESULT";

export default function App() {
  const [step, setStep] = useState<AppState>("INPUT");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const handleGenerate = async (text: string) => {
    setStep("LOADING");

    try {
      // Logic to send text to your backend
      // const response = await fetch('your-api-endpoint', { method: 'POST', body: JSON.stringify({ text }) });
      // const data = await response.json();

      // Simulating backend delay for now
      setTimeout(() => {
        setVideoUrl("https://www.w3schools.com/html/mov_bbb.mp4"); // Mock URL
        setStep("RESULT");
      }, 3000);
    } catch (error) {
      console.error("Generation failed", error);
      setStep("INPUT");
    }
  };

  const resetApp = () => {
    setVideoUrl(null);
    setStep("INPUT");
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
      }}
    >
      {step !== "LOADING" && (
        <header>
          <h1 style={{ color: "var(--clr-accent-400)", marginBottom: "2rem" }}>
            Kitty explains
          </h1>
        </header>
      )}

      {/* Conditional Rendering Logic */}
      {step === "INPUT" && <TextInput onGenerate={handleGenerate} />}
      {step === "LOADING" && <LoadingState />}
      {step === "RESULT" && videoUrl && (
        <ResultView videoUrl={videoUrl} onReset={resetApp} />
      )}
    </main>
  );
}
