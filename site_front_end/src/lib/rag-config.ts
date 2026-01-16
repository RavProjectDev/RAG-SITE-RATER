// RAG Configuration Types and Constants

export type EmbeddingModel = 'openai' | 'cohere' | 'gemini';
export type ChunkingStrategy = 'fixed-size' | 'sliding-window';

export interface RAGConfiguration {
  embeddingModel: EmbeddingModel;
  chunkingStrategy: ChunkingStrategy;
  indexName: string;
  namespace: string;
}

// All 6 possible configurations (semantic chunking removed)
export const ALL_CONFIGURATIONS: RAGConfiguration[] = [
  // OpenAI configurations
  { embeddingModel: 'openai', chunkingStrategy: 'fixed-size', indexName: 'openai', namespace: 'fixed_size' },
  { embeddingModel: 'openai', chunkingStrategy: 'sliding-window', indexName: 'openai', namespace: 'divided' },
  
  // Cohere configurations
  { embeddingModel: 'cohere', chunkingStrategy: 'fixed-size', indexName: 'cohere', namespace: 'fixed_size' },
  { embeddingModel: 'cohere', chunkingStrategy: 'sliding-window', indexName: 'cohere', namespace: 'divided' },
  
  // Gemini configurations
  { embeddingModel: 'gemini', chunkingStrategy: 'fixed-size', indexName: 'gemini', namespace: 'fixed_size' },
  { embeddingModel: 'gemini', chunkingStrategy: 'sliding-window', indexName: 'gemini', namespace: 'divided' },
];

/**
 * Check if Gemini/Vertex AI credentials are available
 */
export function isGeminiAvailable(): boolean {
  const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
  const projectId = process.env.GOOGLE_CLOUD_PROJECT_ID;
  return !!(credentialsPath && projectId);
}

/**
 * Get available configurations (excluding Gemini if credentials not available)
 * 
 * Note: Gemini embeddings are automatically truncated to 784 dimensions to match your Pinecone index.
 */
export function getAvailableConfigurations(): RAGConfiguration[] {
  const geminiAvailable = isGeminiAvailable();
  
  if (!geminiAvailable) {
    // Filter out Gemini configurations if credentials not available
    return ALL_CONFIGURATIONS.filter(config => config.embeddingModel !== 'gemini');
  }
  
  return ALL_CONFIGURATIONS;
}

/**
 * Select 2 random configurations from available configurations
 * Automatically excludes Gemini if Vertex AI credentials are not set
 * Ensures the two configurations are different
 */
export function selectRandomConfigurations(): [RAGConfiguration, RAGConfiguration] {
  const available = getAvailableConfigurations();
  
  if (available.length < 2) {
    throw new Error(
      'Not enough available configurations. Need at least 2. ' +
      'Ensure OpenAI and/or Cohere API keys are set, or set up Vertex AI credentials for Gemini.'
    );
  }
  
  // Shuffle the array to randomize
  const shuffled = [...available].sort(() => Math.random() - 0.5);
  
  // Pick first configuration
  const config1 = shuffled[0];
  
  // Pick second configuration that's different from the first
  // Compare by embedding model and chunking strategy
  const config2 = shuffled.find((config, index) => 
    index > 0 && 
    (config.embeddingModel !== config1.embeddingModel || 
     config.chunkingStrategy !== config1.chunkingStrategy)
  );
  
  // Fallback: if somehow we can't find a different one, just use the second item
  // (this should never happen if we have at least 2 different configs)
  const finalConfig2 = config2 || shuffled[1];
  
  // Double-check they're actually different
  if (config1.embeddingModel === finalConfig2.embeddingModel && 
      config1.chunkingStrategy === finalConfig2.chunkingStrategy) {
    console.warn('Warning: Same configuration selected twice. This should not happen.');
  }
  
  return [config1, finalConfig2];
}

/**
 * Clean and trim the user question
 */
export function cleanQuestion(question: string): string {
  return question.trim().replace(/\s+/g, ' ');
}

