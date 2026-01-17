import { useState } from "react";
import TextInput from "./pages/HomePage";
import LoadingState from "./pages/LoadingPage";
import ResultView from "./pages/ResultPage";
import { Client } from "@langchain/langgraph-sdk";

// Define the possible UI states
type AppState = "INPUT" | "LOADING" | "RESULT";

export default function App() {
  const [step, setStep] = useState<AppState>("INPUT");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const client = new Client({ apiUrl: "http://localhost:2024" });

  // Convert file to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = (reader.result as string).split(',')[1]; // Remove data:*/*;base64, prefix
        resolve(base64);
      };
      reader.onerror = reject;
    });
  };

  // Unified generation method
  async function generateKittyVideo(notes: string, file?: File) {
    const thread = await client.threads.create();

    let input: any = { 
      notes: notes || "",
      file_data: "",
      file_type: "text"
    };

    // If file is provided, convert to base64
    if (file) {
      const fileExtension = file.name.split('.').pop()?.toLowerCase() || "";
      const base64Data = await fileToBase64(file);
      
      input = {
        notes: "",
        file_data: base64Data,
        file_type: fileExtension
      };
    }

    const stream = client.runs.stream(thread.thread_id, "kitty_educator", {
      input,
      streamMode: "updates",
    });

    for await (const event of stream) {
      console.log(Object.keys(event.data)?.[0], event.id, event.event);
    }

    const finalState = await client.threads.getState(thread.thread_id);
    return finalState.values;
  }

  const onGenerate = async (notes: string, file?: File) => {
    try {
      setStep("LOADING");
      const res = await generateKittyVideo(notes, file);
      console.log(res);
      setVideoUrl(res.video_path || null);
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
