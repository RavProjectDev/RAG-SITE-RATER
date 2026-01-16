// Pinecone client and query functions

import { Pinecone } from '@pinecone-database/pinecone';
import type { RAGConfiguration } from './rag-config';

export interface PineconeMatch {
  id: string;
  score: number;
  metadata?: {
    text?: string;
    content?: string;
    source?: string;
    name_space?: string;
    [key: string]: any;
  };
}

/**
 * Initialize Pinecone client
 */
export function getPineconeClient(): Pinecone {
  const apiKey = process.env.PINECONE_API_KEY;
  if (!apiKey) {
    throw new Error('PINECONE_API_KEY is not set');
  }

  return new Pinecone({ apiKey });
}

/**
 * Query Pinecone for related documents
 */
export async function queryPinecone(
  embedding: number[],
  config: RAGConfiguration,
  topK: number = 3
): Promise<PineconeMatch[]> {
  const pinecone = getPineconeClient();
  
  const index = pinecone.index(config.indexName);
  
  try {
    const queryResponse = await index.namespace(config.namespace).query({
      vector: embedding,
      topK,
      includeMetadata: true,
    });

    return queryResponse.matches.map(match => ({
      id: match.id,
      score: match.score ?? 0,
      metadata: match.metadata as any,
    }));
  } catch (error: any) {
    // Provide helpful error message for dimension mismatches
    if (error?.message?.includes('dimension') || error?.message?.includes('Dimension')) {
      const embeddingDim = embedding.length;
      const expectedDims: Record<string, number> = {
        'openai': 3072,  // text-embedding-3-large
        'cohere': 1024,  // embed-multilingual-v3.0
        'gemini': 784,   // gemini-embedding-001 with outputDimensionality=784
      };
      const expectedDim = expectedDims[config.indexName];
      
      throw new Error(
        `Dimension mismatch for ${config.indexName} index:\n` +
        `  - Embedding dimension: ${embeddingDim}\n` +
        `  - Expected dimension: ${expectedDim || 'unknown'}\n` +
        `  - Index dimension: Check your Pinecone dashboard\n\n` +
        `Fix: Recreate the "${config.indexName}" index in Pinecone with ${embeddingDim} dimensions, ` +
        `or use an embedding model that matches your current index dimension.\n\n` +
        `For Gemini: The embedding will be truncated/padded to match your index dimension of 784.`
      );
    }
    throw error;
  }
}

