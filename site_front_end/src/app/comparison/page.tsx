"use client";

import { useState, useMemo, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CitationDisplay } from "@/components/CitationDisplay";
import { HallucinationFlagModal } from "@/components/HallucinationFlagModal";
import { ChevronDown, ChevronUp, CheckCircle, Loader2, AlertCircle } from "lucide-react";
import type {
  ComparisonData,
  VoteOption,
  HallucinationFlag,
  ComparisonResult,
  Citation,
} from "@/types/comparison";

// Force dynamic rendering to support useSearchParams
export const dynamic = 'force-dynamic';

// Helper function to transform backend response to ComparisonData
function transformBackendResponse(
  question: string,
  responses: Array<{
    message: string;
    transcript_data: unknown[];
    prompt_id?: string;
  }>
): ComparisonData | null {
  if (responses.length < 2) {
    return null; // Need at least 2 responses for comparison
  }

  // Take first two responses
  const responseA = responses[0];
  const responseB = responses[1];

  // Transform transcript_data to citations
  const transformCitations = (
    transcriptData: unknown[],
    modelPrefix: string
  ): Citation[] => {
    if (!Array.isArray(transcriptData)) return [];
    
    return transcriptData
      .map((item, index) => {
        if (typeof item !== "object" || item === null) return null;
        const obj = item as Record<string, unknown>;
        
        // Try to extract citation data - adapt based on your backend structure
        const number = typeof obj.number === "number" ? obj.number : index + 1;
        const text = typeof obj.text === "string" ? obj.text : 
                    typeof obj.content === "string" ? obj.content :
                    typeof obj.snippet === "string" ? obj.snippet : "";
        const source = typeof obj.source === "string" ? obj.source :
                      typeof obj.url === "string" ? obj.url :
                      typeof obj.metadata?.source === "string" ? obj.metadata.source : "Unknown source";
        
        if (!text) return null;
        
        return {
          id: `${modelPrefix}-citation-${number}`,
          number,
          text,
          source,
        };
      })
      .filter((c): c is Citation => c !== null);
  };

  return {
    query: question,
    modelA: {
      id: responseA.prompt_id || "model-a-1",
      text: responseA.message,
      modelName: "Model A", // Will be revealed after vote
      citations: transformCitations(responseA.transcript_data, "a"),
    },
    modelB: {
      id: responseB.prompt_id || "model-b-1",
      text: responseB.message,
      modelName: "Model B", // Will be revealed after vote
      citations: transformCitations(responseB.transcript_data, "b"),
    },
  };
}

export default function ComparisonPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const question = searchParams.get("question");

  const [data, setData] = useState<ComparisonData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [vote, setVote] = useState<VoteOption | null>(null);
  const [hallucinationFlags, setHallucinationFlags] = useState<{
    modelA: HallucinationFlag[];
    modelB: HallucinationFlag[];
  }>({ modelA: [], modelB: [] });
  const [showSources, setShowSources] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch comparison data when question is available
  useEffect(() => {
    if (!question) {
      setError("No question provided. Please enter a question on the home page.");
      setIsLoading(false);
      return;
    }

    const fetchComparisonData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await fetch("/api/get_full_response", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        });

        if (!response.ok) {
          // Try to get error message from response
          let errorMessage = "Failed to fetch model responses";
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
          } catch {
            // If response isn't JSON, use status text
            errorMessage = `${errorMessage} (${response.status}: ${response.statusText})`;
          }
          throw new Error(errorMessage);
        }

        const result = await response.json();
        
        // Check if there's an error in the response
        if (result.error) {
          throw new Error(result.error);
        }
        
        const transformed = transformBackendResponse(question, result.responses || []);

        if (!transformed) {
          throw new Error("Insufficient responses. Need at least 2 model responses for comparison.");
        }

        setData(transformed);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "An error occurred while fetching responses";
        setError(errorMessage);
        console.error("Error fetching comparison data:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchComparisonData();
  }, [question]);

  const hasVoted = vote !== null;

  const handleVote = (voteOption: VoteOption) => {
    setVote(voteOption);
  };

  const handleFlagsSubmit = (model: "A" | "B", flags: HallucinationFlag[]) => {
    setHallucinationFlags((prev) => ({
      ...prev,
      [`model${model}`]: flags,
    }));
  };

  const handleSubmit = async () => {
    if (!data) return;
    
    setIsSubmitting(true);
    
    const result: ComparisonResult = {
      vote: vote!,
      timestamp: Date.now(),
      hallucination_flags: hallucinationFlags,
      model_a_id: data.modelA.id,
      model_b_id: data.modelB.id,
      model_a_response: data.modelA.text,
      model_b_response: data.modelB.text,
      query: data.query,
    };

    try {
      const response = await fetch("/api/submit_comparison", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(result),
      });

      if (response.ok) {
        // Show success and redirect to home to ask another question
        router.push("/?submitted=true");
      } else {
        console.error("Failed to submit comparison");
        setError("Failed to submit comparison. Please try again.");
      }
    } catch (error) {
      console.error("Error submitting comparison:", error);
      setError("An error occurred while submitting. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderResponseWithCitations = (
    text: string,
    citations: Citation[],
    modelKey: "modelA" | "modelB"
  ) => {
    const parts: (string | JSX.Element)[] = [];
    let lastIndex = 0;
    const citationRegex = /\[(\d+)\]/g;
    let match;

    while ((match = citationRegex.exec(text)) !== null) {
      // Add text before citation
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }

      // Find the citation
      const citationNumber = parseInt(match[1]);
      const citation = citations.find((c) => c.number === citationNumber);

      if (citation) {
        parts.push(
          <CitationDisplay
            key={`${modelKey}-${citation.id}-${match.index}`}
            citation={citation}
          />
        );
      } else {
        parts.push(match[0]);
      }

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return <div className="leading-relaxed">{parts}</div>;
  };

  const allCitations = useMemo(() => {
    if (!data) return [];
    return [...data.modelA.citations, ...data.modelB.citations].sort(
      (a, b) => a.number - b.number
    );
  }, [data]);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 pb-6">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400" />
              <p className="text-center text-gray-600 dark:text-gray-400">
                Loading model responses...
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Error state
  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertCircle className="h-5 w-5" />
              Error
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-700 dark:text-gray-300">
              {error || "Failed to load comparison data"}
            </p>
            <Link href="/">
              <Button className="w-full">Return to Home</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* User Query */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-lg md:text-xl">User Query</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 dark:text-gray-300 text-base md:text-lg">
              {data.query}
            </p>
          </CardContent>
        </Card>

        {/* Two-Column Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
          {/* Model A */}
          <Card className="shadow-lg border-2 border-transparent hover:border-blue-200 dark:hover:border-blue-800 transition-colors">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  Model A
                  {hasVoted && (
                    <span className="ml-2 text-sm font-normal text-gray-600 dark:text-gray-400">
                      ({data.modelA.modelName})
                    </span>
                  )}
                </CardTitle>
                <HallucinationFlagModal
                  modelLabel="A"
                  currentFlags={hallucinationFlags.modelA}
                  onSubmit={(flags) => handleFlagsSubmit("A", flags)}
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-gray-700 dark:text-gray-300 text-sm md:text-base">
                {renderResponseWithCitations(data.modelA.text, data.modelA.citations, "modelA")}
              </div>
            </CardContent>
          </Card>

          {/* Model B */}
          <Card className="shadow-lg border-2 border-transparent hover:border-purple-200 dark:hover:border-purple-800 transition-colors">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">
                  Model B
                  {hasVoted && (
                    <span className="ml-2 text-sm font-normal text-gray-600 dark:text-gray-400">
                      ({data.modelB.modelName})
                    </span>
                  )}
                </CardTitle>
                <HallucinationFlagModal
                  modelLabel="B"
                  currentFlags={hallucinationFlags.modelB}
                  onSubmit={(flags) => handleFlagsSubmit("B", flags)}
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-gray-700 dark:text-gray-300 text-sm md:text-base">
                {renderResponseWithCitations(data.modelB.text, data.modelB.citations, "modelB")}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Collapsible Sources Section */}
        <Card className="shadow-lg">
          <CardHeader
            className="cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            onClick={() => setShowSources(!showSources)}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                📚 View Sources / Citations
              </CardTitle>
              {showSources ? (
                <ChevronUp className="h-5 w-5" />
              ) : (
                <ChevronDown className="h-5 w-5" />
              )}
            </div>
          </CardHeader>
          {showSources && (
            <CardContent className="space-y-4 pt-4">
              {allCitations.map((citation) => (
                <div
                  key={citation.id}
                  className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 flex items-center justify-center font-semibold text-sm">
                      {citation.number}
                    </div>
                    <div className="flex-1 space-y-2">
                      <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">
                        {citation.text}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 italic break-words">
                        Source: {citation.source}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          )}
        </Card>

        {/* Voting Bar */}
        <Card className="shadow-lg sticky bottom-4 bg-white/95 dark:bg-gray-900/95 backdrop-blur">
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Button
                  size="lg"
                  variant={vote === "A" ? "default" : "outline"}
                  className="h-12 md:h-14 font-semibold"
                  onClick={() => handleVote("A")}
                  disabled={hasVoted}
                >
                  {vote === "A" && <CheckCircle className="mr-2 h-5 w-5" />}
                  A is better
                </Button>
                <Button
                  size="lg"
                  variant={vote === "B" ? "default" : "outline"}
                  className="h-12 md:h-14 font-semibold"
                  onClick={() => handleVote("B")}
                  disabled={hasVoted}
                >
                  {vote === "B" && <CheckCircle className="mr-2 h-5 w-5" />}
                  B is better
                </Button>
                <Button
                  size="lg"
                  variant={vote === "tie" ? "default" : "outline"}
                  className="h-12 md:h-14 font-semibold"
                  onClick={() => handleVote("tie")}
                  disabled={hasVoted}
                >
                  {vote === "tie" && <CheckCircle className="mr-2 h-5 w-5" />}
                  Tie
                </Button>
                <Button
                  size="lg"
                  variant={vote === "both_bad" ? "destructive" : "outline"}
                  className="h-12 md:h-14 font-semibold"
                  onClick={() => handleVote("both_bad")}
                  disabled={hasVoted}
                >
                  {vote === "both_bad" && <CheckCircle className="mr-2 h-5 w-5" />}
                  Both bad
                </Button>
              </div>

              {hasVoted && (
                <div className="flex justify-center pt-2">
                  <Button
                    size="lg"
                    className="w-full md:w-auto px-12 h-12 md:h-14 font-semibold bg-green-600 hover:bg-green-700"
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? "Submitting..." : "Submit Rating →"}
                  </Button>
                </div>
              )}

              {!hasVoted && (
                <p className="text-center text-sm text-gray-500 dark:text-gray-400">
                  Please vote to submit your rating
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

