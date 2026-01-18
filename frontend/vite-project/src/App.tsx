import { useState } from "react";
import TextInput from "./pages/HomePage";
import LoadingState from "./pages/LoadingPage";
import ResultView from "./pages/ResultPage";
import { Client } from "@langchain/langgraph-sdk";

// Define the possible UI states
type AppState = "INPUT" | "LOADING" | "RESULT";
type DurationOption = "30s" | "60s" | "90s";

export default function App() {
  const [step, setStep] = useState<AppState>("INPUT");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const client = new Client({ apiUrl: "http://localhost:2024" });
  const [pipelineCount, setPipelineCount] = useState(0);

  // Convert file to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = (reader.result as string).split(",")[1]; // Remove data:*/*;base64, prefix
        resolve(base64);
      };
      reader.onerror = reject;
    });
  };

  // Unified generation method
  async function generateKittyVideo(notes: string, duration: DurationOption, file?: File) {
    const thread = await client.threads.create();

    let input: any = {
      notes: notes || "",
      file_data: "",
      file_type: "text",
      duration,
    };

    // If file is provided, convert to base64
    if (file) {
      const fileExtension = file.name.split(".").pop()?.toLowerCase() || "";
      const base64Data = await fileToBase64(file);

      input = {
        notes: "",
        file_data: base64Data,
        file_type: fileExtension,
        duration,
      };
    }

    const stream = client.runs.stream(thread.thread_id, "kitty_educator", {
      input,
      streamMode: "updates",
    });

    for await (const event of stream) {
      console.log(Object.keys(event.data)?.[0]);
      setPipelineCount(count => count + 1);
    }

    const finalState = await client.threads.getState(thread.thread_id);
    return finalState.values;
  }

  const onGenerate = async (notes: string, duration: DurationOption, file?: File) => {
    try {
      setStep("LOADING");
      const res = await generateKittyVideo(notes, duration, file);
      console.log(res);
      setStep("RESULT");
      setPipelineCount(0);
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
      {step === "LOADING" && <LoadingState pipelineCount={pipelineCount} />}
      {step === "RESULT" && (
        <ResultView videoUrl={videoUrl ?? ""} onReset={resetApp} />
      )}
    </main>
  );
}
