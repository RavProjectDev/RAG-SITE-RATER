"use client";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

// Rating component for 0–100 using a number input (clicker)
function Rating({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex items-center gap-2 justify-center">
      <button
        type="button"
        className="w-8 h-8 rounded border border-gray-300 bg-white text-lg font-bold hover:bg-gray-100 disabled:opacity-50"
        onClick={() => onChange(Math.max(0, value - 1))}
        disabled={value <= 0}
        aria-label="Decrease rating"
      >
        -
      </button>
      <input
        type="number"
        min={0}
        max={100}
        value={value}
        onChange={e => {
          let v = Number(e.target.value);
          if (isNaN(v)) v = 0;
          v = Math.max(0, Math.min(100, v));
          onChange(v);
        }}
        className="w-16 text-center border border-gray-300 rounded h-8 text-base font-semibold bg-white focus:outline-none focus:ring-2 focus:ring-primary"
        aria-label="Rating value"
      />
      <button
        type="button"
        className="w-8 h-8 rounded border border-gray-300 bg-white text-lg font-bold hover:bg-gray-100 disabled:opacity-50"
        onClick={() => onChange(Math.min(100, value + 1))}
        disabled={value >= 100}
        aria-label="Increase rating"
      >
        +
      </button>
    </div>
  );
}

export default function Home() {
  // App state
  const [question, setQuestion] = useState("");
  const [chunks, setChunks] = useState<{ id: string; content: string }[]>([]);
  const [ratings, setRatings] = useState<{ [id: string]: number }>({});
  const [step, setStep] = useState<"ask" | "rate" | "done">("ask");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle question submit
  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/get_chunks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setChunks(data.chunks);
      setRatings({});
      setStep("rate");
    } catch (err) {
      setError("Failed to fetch chunks.");
    } finally {
      setLoading(false);
    }
  }

  // Handle ratings submit
  async function handleRatings(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      // Optimistic UI: go to done immediately
      setStep("done");
      await fetch("/api/upload_ratings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question, // include the question
          ratings: chunks.map((chunk) => ({
            chunkId: chunk.id,
            rating: ratings[chunk.id] ?? 0,
          })),
        }),
      });
    } catch (err) {
      setError("Failed to upload ratings.");
      setStep("rate"); // Rollback
    } finally {
      setLoading(false);
    }
  }

  // UI
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
      <Card className="w-full lg:max-w-4xl p-6 flex flex-col gap-10 shadow-lg">
        <h1 className="text-2xl font-bold mb-2 text-center">Chunk Rater</h1>
        {/* About Section */}
        {step === "ask" && (
          <div className="mb-4 p-4 bg-muted/80 border rounded text-sm text-muted-foreground">
            <h2 className="font-semibold mb-2 text-lg">About</h2>
            <p>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque euismod, urna eu tincidunt consectetur, nisi nisl aliquam nunc, eget aliquam massa nisl quis neque. Etiam vitae turpis euismod, ultricies quam in, eleifend massa. Integer non dictum erat. Suspendisse potenti.
            </p>
          </div>
        )}
        {step === "ask" && (
          <form onSubmit={handleAsk} className="flex flex-col gap-4">
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your question..."
              className="resize-none min-h-[80px]"
              required
            />
            <Button type="submit" disabled={loading || !question.trim()}>
              {loading ? "Loading..." : "Get Chunks"}
            </Button>
          </form>
        )}
        {step === "rate" && (
          <form onSubmit={handleRatings} className="flex flex-col gap-6">
            <div className="text-lg font-semibold text-center text-primary mb-2">
              Question: <span className="font-normal text-foreground">{question}</span>
            </div>
            <div className="flex flex-col gap-4">
              {chunks.map((chunk) => (
                <div
                  key={chunk.id}
                  className="flex flex-col gap-2 border rounded-lg bg-muted/60 shadow-inner w-full"
                  style={{ minHeight: 220, maxHeight: 400 }}
                >
                  <div className="p-6 rounded-t-lg whitespace-pre-line leading-relaxed break-words text-base font-medium flex-1"
                    style={{ maxHeight: 320, overflowY: 'auto' }}
                  >
                    {chunk.content}
                  </div>
                  <div className="p-6 pt-4 border-t border-gray-200 rounded-b-lg bg-background flex items-center justify-center">
                    <Rating
                      value={ratings[chunk.id] ?? 50}
                      onChange={(v) => setRatings((r) => ({ ...r, [chunk.id]: v }))}
                    />
                  </div>
                </div>
              ))}
            </div>
            <Button
              type="submit"
              disabled={loading || chunks.some((c) => ratings[c.id] === undefined)}
              className="w-full"
            >
              {loading ? "Submitting..." : "Submit Ratings"}
            </Button>
          </form>
        )}
        {step === "done" && (
          <div className="text-center flex flex-col gap-4 items-center">
            <div className="text-green-600 font-semibold text-lg">Thank you for your feedback!</div>
            <div className="text-muted-foreground text-base">Your question: <b>{question}</b></div>
            <Button onClick={() => { setStep("ask"); setQuestion(""); setChunks([]); setRatings({}); }}>
              Rate another question
            </Button>
          </div>
        )}
        {error && <div className="text-red-500 text-center">{error}</div>}
      </Card>
      <footer className="mt-8 text-xs text-muted-foreground text-center opacity-80">
        &copy; {new Date().getFullYear()} Chunk Rater Demo
      </footer>
    </div>
  );
}
