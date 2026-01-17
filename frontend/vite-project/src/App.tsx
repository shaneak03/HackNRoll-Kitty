import { useState } from "react";
import TextInput from "./pages/HomePage";
import LoadingState from "./pages/LoadingPage";
import ResultView from "./pages/ResultPage";
import { Client } from "@langchain/langgraph-sdk";

// Define the possible UI states
type AppState = "INPUT" | "LOADING" | "RESULT";

export default function App() {
  const [step, setStep] = useState<AppState>("RESULT");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const client = new Client({ apiUrl: "http://localhost:2024" });

  async function generateKittyVideo(notes: string) {
    const thread = await client.threads.create();

    const stream = client.runs.stream(thread.thread_id, "kitty_educator", {
      input: { notes },
      streamMode: "updates",
    });

    for await (const event of stream) {
      console.log(Object.keys(event.data)?.[0], event.id, event.event);
    }

    const finalState = await client.threads.getState(thread.thread_id);
    return finalState.values;
  }

  const onGenerate = async (notes: string) => {
    try {
      setStep("LOADING");
      const res = await generateKittyVideo(notes);
      console.log(res);
      setStep("RESULT");
    } catch (error) {
      console.error("Generation failed:", error);
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
          <h1 style={{ color: "var(--clr-accent-400)", marginBottom: "1rem" }}>
            Kitty explains
          </h1>
        </header>
      )}

      {step === "INPUT" && <TextInput onGenerate={onGenerate} />}
      {step === "LOADING" && <LoadingState />}
      {step === "RESULT" && (
        <ResultView videoUrl={videoUrl ?? ""} onReset={resetApp} />
      )}
    </main>
  );
}
