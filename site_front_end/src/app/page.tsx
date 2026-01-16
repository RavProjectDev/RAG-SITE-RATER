"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Lightbulb, CheckCircle } from "lucide-react";
import { getNextExampleQuestion } from "@/data/example-questions";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [exampleQuestion, setExampleQuestion] = useState("");
  const router = useRouter();
  const searchParams = useSearchParams();

  // Initialize example question on mount
  useEffect(() => {
    setExampleQuestion(getNextExampleQuestion());
  }, []);

  // Check if user just submitted a rating
  useEffect(() => {
    if (searchParams.get("submitted") === "true") {
      setShowSuccess(true);
      // Clear the query parameter
      router.replace("/", { scroll: false });
      // Hide success message after 5 seconds
      const timer = setTimeout(() => setShowSuccess(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [searchParams, router]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setIsSubmitting(true);
    // Navigate to comparison page with question as query parameter
    const encodedQuestion = encodeURIComponent(question.trim());
    router.push(`/comparison?question=${encodedQuestion}`);
  };

  const handleUseExample = () => {
    // Get next question in round-robin and update state
    const nextQuestion = getNextExampleQuestion();
    setQuestion(nextQuestion);
    setExampleQuestion(nextQuestion);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <main className="mx-auto max-w-3xl px-4 py-12 md:py-20">
        {/* Title */}
        <section className="text-center mb-8 md:mb-12">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-gray-100 dark:to-gray-400 bg-clip-text text-transparent mb-3">
            RAG Response Evaluator
          </h1>
          <p className="text-base text-gray-600 dark:text-gray-400">
            Compare AI responses and help improve model quality
          </p>
        </section>

        {/* Success Message */}
        {showSuccess && (
          <section className="mb-6">
            <Card className="shadow-lg border-2 border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/30">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="font-semibold text-green-900 dark:text-green-100">
                      Rating submitted successfully!
                    </p>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      You can ask another question below to continue.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
        )}

        {/* Question Input Section */}
        <section id="question-form">
          <Card className="shadow-xl border-2">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-center">
                Ask a Question
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="question" className="text-base font-semibold">
                    Your Question
                  </Label>
                  <Textarea
                    id="question"
                    placeholder="Type your question here..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="min-h-32 text-base"
                    required
                  />
                </div>
                
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button
                    type="submit"
                    size="lg"
                    className="flex-1 h-12 text-base font-semibold shadow-lg hover:shadow-xl transition-all"
                    disabled={!question.trim() || isSubmitting}
                  >
                    {isSubmitting ? "Loading..." : "Compare Responses →"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="lg"
                    onClick={handleUseExample}
                    className="h-12 text-base font-semibold"
                  >
                    <Lightbulb className="mr-2 h-4 w-4" />
                    Use Example
                  </Button>
                </div>
              </form>

              {/* Example Question Display */}
              {exampleQuestion && (
                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950/30 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start gap-3">
                    <Lightbulb className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                        Example Question (click "Use Example" to cycle):
                      </p>
                      <p className="text-sm text-blue-700 dark:text-blue-300 italic">
                        "{exampleQuestion}"
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}
