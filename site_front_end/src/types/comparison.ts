export type VoteOption = "A" | "B" | "tie" | "both_bad";

export type HallucinationFlag = 
  | "factually_incorrect" 
  | "ignored_instructions" 
  | "hallucination";

export interface Citation {
  id: string;
  number: number;
  text: string;
  source: string;
}

export interface ModelResponse {
  id: string;
  text: string;
  modelName: string; // Hidden until after vote
  citations: Citation[];
}

export interface ComparisonData {
  query: string;
  modelA: ModelResponse;
  modelB: ModelResponse;
}

export interface ComparisonResult {
  vote: VoteOption;
  timestamp: number;
  hallucination_flags: {
    modelA: HallucinationFlag[];
    modelB: HallucinationFlag[];
  };
  model_a_id: string;
  model_b_id: string;
  model_a_response: string;
  model_b_response: string;
  query: string;
}

