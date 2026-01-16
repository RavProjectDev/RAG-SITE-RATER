// Embedding functions for different providers

import OpenAI from 'openai';
import { CohereClient } from 'cohere-ai';
import { PredictionServiceClient, helpers } from '@google-cloud/aiplatform';
import type { EmbeddingModel } from './rag-config';

/**
 * Generate embeddings for a given text using the specified embedding model
 */
export async function generateEmbedding(
  text: string,
  model: EmbeddingModel
): Promise<number[]> {
  switch (model) {
    case 'openai':
      return await generateOpenAIEmbedding(text);
    case 'cohere':
      return await generateCohereEmbedding(text);
    case 'gemini':
      return await generateGeminiEmbedding(text);
    default:
      throw new Error(`Unknown embedding model: ${model}`);
  }
}

/**
 * Generate OpenAI embeddings using text-embedding-3-large (3072 dimensions)
 */
async function generateOpenAIEmbedding(text: string): Promise<number[]> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not set');
  }

  const openai = new OpenAI({ apiKey });
  
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-large',
    input: text,
    dimensions: 3072, // Explicitly set to match Pinecone index
  });

  return response.data[0].embedding;
}

/**
 * Generate Cohere embeddings using embed-multilingual-v3.0 (1024 dimensions)
 */
async function generateCohereEmbedding(text: string): Promise<number[]> {
  const apiKey = process.env.COHERE_API_KEY;
  if (!apiKey) {
    throw new Error('COHERE_API_KEY is not set');
  }

  const cohere = new CohereClient({ token: apiKey });
  
  const response = await cohere.embed({
    texts: [text],
    model: 'embed-multilingual-v3.0',
    inputType: 'search_query',
  });

  return response.embeddings[0];
}

/**
 * Generate Gemini embeddings using gemini-embedding-001 via Vertex AI
 * Note: This requires Google Cloud service account authentication
 * 
 * Configured to output 3072 dimensions to match your Pinecone index.
 * Uses RETRIEVAL_QUERY task type for optimizing search queries.
 */
async function generateGeminiEmbedding(text: string): Promise<number[]> {
  // Check for service account credentials
  const credentialsPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
  const projectId = process.env.GOOGLE_CLOUD_PROJECT_ID;
  const location = process.env.GOOGLE_CLOUD_LOCATION || 'us-central1';

  if (!credentialsPath || !projectId) {
    throw new Error(
      'GOOGLE_APPLICATION_CREDENTIALS and GOOGLE_CLOUD_PROJECT_ID must be set for Vertex AI embeddings.\n' +
      'Set GOOGLE_APPLICATION_CREDENTIALS to the path of your service account JSON file.\n' +
      'Example: GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json'
    );
  }

  try {
    // Initialize Vertex AI PredictionServiceClient
    // The client will automatically use GOOGLE_APPLICATION_CREDENTIALS env var
    const client = new PredictionServiceClient({
      apiEndpoint: `${location}-aiplatform.googleapis.com`,
    });

    // Vertex AI endpoint for gemini-embedding-001
    const endpoint = `projects/${projectId}/locations/${location}/publishers/google/models/gemini-embedding-001`;

    // Prepare the instance using helpers.toValue
    // For gemini-embedding-001, we pass the text as content
    const instance = helpers.toValue({
      content: text,
    });

    // Specify parameters to control output dimensionality and task type
    // Explicitly set to 3072 to match your Pinecone index
    // Use RETRIEVAL_QUERY for embedding search queries
    const parameters = helpers.toValue({
      outputDimensionality: 3072,
      taskType: 'RETRIEVAL_DOCUMENT',
    });

    const request = {
      endpoint,
      instances: [instance],
      parameters,
    };

    // Call the prediction API
    const [response] = await client.predict(request);

    if (!response.predictions || response.predictions.length === 0) {
      throw new Error('No predictions returned from Vertex AI');
    }

    const prediction = response.predictions[0] as any;

    // Extract embeddings from the protobuf response structure
    // Vertex AI returns data in protobuf format with nested structValue/fields
    // Structure: prediction.structValue.fields.embeddings.structValue.fields.values.listValue.values[].numberValue
    function extractEmbeddingFromProtobuf(pred: any): number[] | null {
      // Try direct access first (if already converted)
      if (pred.embeddings?.values && Array.isArray(pred.embeddings.values)) {
        return pred.embeddings.values;
      }

      // Handle protobuf structValue format - exact path from Vertex AI response
      // pred.structValue.fields.embeddings.structValue.fields.values.listValue.values
      try {
        // Check if pred itself is a structValue (root level)
        const rootStruct = pred.structValue || pred;
        
        if (rootStruct?.fields?.embeddings?.structValue?.fields?.values?.listValue?.values) {
          const values = rootStruct.fields.embeddings.structValue.fields.values.listValue.values;
          if (Array.isArray(values) && values.length > 0) {
            return values.map((v: any) => {
              // Extract numberValue from protobuf format
              if (v && typeof v === 'object' && 'numberValue' in v) {
                return v.numberValue;
              }
              // Fallback for other formats
              return typeof v === 'number' ? v : 0;
            });
          }
        }
      } catch (e) {
        console.error('Error extracting embeddings from protobuf:', e);
      }

      // Try alternative nested paths
      try {
        if (pred?.embeddings?.structValue?.fields?.values?.listValue?.values) {
          const values = pred.embeddings.structValue.fields.values.listValue.values;
          if (Array.isArray(values) && values.length > 0) {
            return values.map((v: any) => {
              if (v && typeof v === 'object' && 'numberValue' in v) {
                return v.numberValue;
              }
              return typeof v === 'number' ? v : 0;
            });
          }
        }
      } catch (e) {
        console.error('Error extracting embeddings from alternative path:', e);
      }

      return null;
    }

    const embedding = extractEmbeddingFromProtobuf(prediction);

    if (embedding && embedding.length > 0) {
      console.log(`Generated embedding with ${embedding.length} dimensions using gemini-embedding-001 (configured for 3072 dimensions)`);
      return embedding;
    }

    // Debug: log the structure to help diagnose
    console.error('Failed to extract embeddings. Prediction structure:', JSON.stringify(prediction).substring(0, 1000));
    
    // Fallback: try to extract as plain array
    if (Array.isArray(prediction)) {
      return prediction;
    }

    throw new Error(`Unexpected response format from Vertex AI. Could not extract embeddings from: ${JSON.stringify(prediction).substring(0, 500)}`);
  } catch (error) {
    console.error('Error generating Gemini embedding via Vertex AI:', error);
    throw error;
  }
}

