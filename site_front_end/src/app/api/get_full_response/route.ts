import { NextRequest, NextResponse } from 'next/server';
import { GENERIC_ERROR_MESSAGE } from '@/lib/utils';
import { selectRandomConfigurations, cleanQuestion } from '@/lib/rag-config';
import { generateEmbedding } from '@/lib/embeddings';
import { queryPinecone } from '@/lib/pinecone-client';
import { generateLLMResponse } from '@/lib/llm-generator';

// Generate full RAG responses for a given question
export async function POST(req: NextRequest) {
  try {
    const { question } = await req.json();
    if (!question || typeof question !== 'string') {
      return NextResponse.json({ error: 'Question is required' }, { status: 400 });
    }

    // Step 1: Clean the question
    const cleanedQuestion = cleanQuestion(question);
    console.log('Processing question:', cleanedQuestion);

    // Step 2: Select 2 random configurations
    const [config1, config2] = selectRandomConfigurations();
    console.log('Selected configurations:', config1, config2);
    
    // Log if Gemini is excluded
    if (config1.embeddingModel !== 'gemini' && config2.embeddingModel !== 'gemini') {
      const geminiAvailable = process.env.GOOGLE_APPLICATION_CREDENTIALS && process.env.GOOGLE_CLOUD_PROJECT_ID;
      if (!geminiAvailable) {
        console.log('Note: Gemini configurations excluded (Vertex AI credentials not set)');
      }
    }

    // Step 3: Generate responses for both configurations in parallel
    const [response1, response2] = await Promise.all([
      generateResponseForConfig(cleanedQuestion, config1),
      generateResponseForConfig(cleanedQuestion, config2),
    ]);

    // Step 4: Format responses
    const responses = [
      {
        message: response1.message,
        transcript_data: response1.transcript_data,
        prompt_id: response1.prompt_id,
      },
      {
        message: response2.message,
        transcript_data: response2.transcript_data,
        prompt_id: response2.prompt_id,
      },
    ];

    return NextResponse.json({ responses });
  } catch (error) {
    console.error('Error in get_full_response:', error);
    const errorMessage = error instanceof Error ? error.message : GENERIC_ERROR_MESSAGE;
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}

/**
 * Generate a response for a specific RAG configuration
 */
async function generateResponseForConfig(question: string, config: any) {
  try {
    // Step 1: Generate embedding for the question
    console.log(`Generating ${config.embeddingModel} embedding...`);
    const embedding = await generateEmbedding(question, config.embeddingModel);

    // Step 2: Query Pinecone for related documents
    console.log(`Querying Pinecone index: ${config.indexName}, namespace: ${config.namespace}...`);
    const matches = await queryPinecone(embedding, config, 3);
    console.log(`Found ${matches.length} matches`);

    // Step 3: Generate LLM response
    console.log('Generating LLM response...');
    const response = await generateLLMResponse(question, matches, config);

    return response;
  } catch (error) {
    console.error(`Error generating response for config ${config.embeddingModel}-${config.chunkingStrategy}:`, error);
    throw error;
  }
}

