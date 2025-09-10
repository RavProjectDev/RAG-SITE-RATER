"use client";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
      <Card className="w-full lg:max-w-4xl p-8 flex flex-col gap-6 shadow-lg">
        <h1 className="text-3xl font-bold text-center">Welcome to The Rav RAG Project</h1>
        <p className="text-center text-base text-muted-foreground">Exploring the Teachings of Rabbi Joseph B. Soloveitchik Through AI</p>

        <div className="space-y-4">
          <p className="text-base leading-relaxed">
            This Retrieval-Augmented Generation (RAG) system is designed to help users explore and access the profound philosophical and halakhic teachings of Rabbi Joseph B. Soloveitchik, known as "The Rav." Our platform combines advanced AI technology with carefully curated texts to provide meaningful interactions with his scholarly works.
          </p>

          <div>
            <h2 className="text-xl font-semibold mb-2">About This Evaluation System</h2>
            <p className="text-base leading-relaxed">
              This interface serves a dual purpose: providing access to The Rav's teachings while simultaneously measuring and improving our AI model's performance. Your participation helps us evaluate:
            </p>
            <ul className="list-disc pl-6 text-base leading-relaxed">
              <li><strong>Model Accuracy</strong>: How well our system retrieves and presents relevant information</li>
              <li><strong>User Satisfaction</strong>: The quality and usefulness of responses from a user perspective</li>
              <li><strong>System Performance</strong>: Overall effectiveness of our RAG implementation</li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">Choose Your Evaluation Mode</h2>

            <div className="space-y-4">
              <div className="p-4 border rounded-md bg-muted/50">
                <h3 className="text-lg font-semibold">📄 Chunk Evaluation (<code>get_chunks</code>)</h3>
                <div className="text-sm text-muted-foreground">Purpose: Evaluate information retrieval accuracy</div>
                <ul className="list-disc pl-6 mt-2 text-base leading-relaxed">
                  <li>Submit a question drawn from our curated list</li>
                  <li>Receive up to 5 extracted text chunks relevant to your query</li>
                  <li>Score each chunk on a 0–100 scale for relevance and usefulness</li>
                  <li>Help us tune embeddings and retrieval quality</li>
                </ul>
                <div className="text-sm mt-2">Best for: Measuring search precision and document matching.</div>
                <div className="mt-3">
                  <Link href="/get_chunks">
                    <Button>Go to Chunk Evaluation</Button>
                  </Link>
                </div>
              </div>

              <div className="p-4 border rounded-md bg-muted/50">
                <h3 className="text-lg font-semibold">🔍 Full Response Evaluation (<code>get_full</code>)</h3>
                <div className="text-sm text-muted-foreground">Purpose: Evaluate complete AI-generated responses</div>
                <ul className="list-disc pl-6 mt-2 text-base leading-relaxed">
                  <li>Ask a question about The Rav’s teachings</li>
                  <li>Receive 3 complete responses at increasing LLM interference levels (1 = least → 3 = most)</li>
                  <li>Assign a unique rank: 1 = Best, 2 = Middle, 3 = Worst</li>
                  <li>Optionally add an overall comment about the responses</li>
                </ul>
                <div className="text-sm mt-2">Best for: Assessing end-to-end answer quality and user experience.</div>
                <div className="mt-3">
                  <Link href="/get_full_response">
                    <Button variant="outline">Go to Full Response Evaluation</Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">Your Role as an Evaluator</h2>
            <ul className="list-disc pl-6 text-base leading-relaxed">
              <li>Fine-tune our retrieval algorithms</li>
              <li>Improve response generation quality</li>
              <li>Ensure respectful and accurate representation of The Rav's teachings</li>
              <li>Enhance overall user satisfaction with the system</li>
            </ul>
            <p className="mt-2 text-base leading-relaxed">Ready to begin? Select your preferred evaluation mode and start exploring The Rav's profound contributions to Jewish thought and law.</p>
          </div>
        </div>
      </Card>
    </div>
  );
}


