// LLM generation functions

import OpenAI from 'openai';
import type { PineconeMatch } from './pinecone-client';
import type { RAGConfiguration } from './rag-config';

export interface GeneratedResponse {
  message: string;
  transcript_data: Array<{
    number: number;
    text: string;
    source: string;
    slug: string;
    start_time: string;
    end_time: string;
  }>;
  prompt_id: string;
  config: RAGConfiguration;
}

interface ParsedSource {
  text: string;
  start_time: string;
  end_time: string;
  slug: string;
}

/**
 * Parse the text field from Pinecone metadata
 * The text field contains a stringified JSON array of tuples: [[text, [start, end]], ...]
 */
function parseTextSources(match: PineconeMatch): ParsedSource[] {
  try {
    const textField = match.metadata?.text;
    const slug = match.metadata?.sanity_slug || match.metadata?.name_space || 'Unknown';
    
    if (!textField) {
      return [];
    }

    // Parse the stringified JSON array
    const tuples = JSON.parse(textField);
    
    if (!Array.isArray(tuples)) {
      return [];
    }

    // Extract each tuple as a separate source
    return tuples.map((tuple: any) => {
      if (Array.isArray(tuple) && tuple.length === 2) {
        const [text, timestamps] = tuple;
        const [start_time, end_time] = Array.isArray(timestamps) ? timestamps : ['', ''];
        
        return {
          text: String(text || ''),
          start_time: String(start_time || ''),
          end_time: String(end_time || ''),
          slug,
        };
      }
      return null;
    }).filter((source): source is ParsedSource => source !== null);
  } catch (error) {
    console.error('Error parsing text field from Pinecone:', error);
    return [];
  }
}

/**
 * Generate LLM response using retrieved context
 */
export async function generateLLMResponse(
  question: string,
  matches: PineconeMatch[],
  config: RAGConfiguration
): Promise<GeneratedResponse> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not set');
  }

  const openai = new OpenAI({ apiKey });

  // Parse all sources from all matches
  const allSources: ParsedSource[] = [];
  matches.forEach(match => {
    const sources = parseTextSources(match);
    allSources.push(...sources);
  });

  // Format the context with numbered sources
  const context = allSources
    .map((source, index) => {
      return `[${index + 1}] ${source.text}\nSource: ${source.slug} (${source.start_time} - ${source.end_time})`;
    })
    .join('\n\n');

  // Create the prompt with the user's specified format
  const systemPrompt = `You are a Rav Soloveitchik expert assistant. Your task is to output ONLY a valid JSON object that summarizes the main idea and lists which numbered sources from the context you used.

# Context

${context}

# User Question

${question}

# Context Format

The context above contains numbered sources [1], [2], [3], etc. Each source is a segment from a transcript with:

- A number in brackets: [N]

- The full text of that segment

- Source metadata (slug and timestamp)

# Output Requirements (CRITICAL)

1. Output ONLY a single valid JSON object. No prose, no Markdown, no extra text before or after.

2. JSON schema (exact keys):

{
  "main_text": string,  
  "source_numbers": [number]
}

3. MAIN TEXT:

   - Provide a comprehensive response (3-5 sentences) that directly answers the user's question

   - Synthesize and explain the relevant ideas from the numbered sources

   - Write naturally and clearly for the user

4. SOURCE NUMBERS:

   - List ONLY the numbers (as integers) of the sources you referenced in your main_text

   - Be selective - only include sources that are truly relevant to answering the question

   - The numbers should correspond to the [N] markers in the context above

   - Example: if you used sources [1], [3], and [5], return: "source_numbers": [1, 3, 5]

5. STRICT REQUIREMENTS:

   - Use ONLY information from the provided numbered sources

   - Do NOT invent or add information not present in the context

   - Reference source numbers EXACTLY as they appear in brackets

   - If no sources are relevant, return: {"main_text": "The provided context does not contain sufficient information to answer this question.", "source_numbers": []}

6. Ensure all strings use double quotes and the JSON is syntactically valid.

# Example Output Structure:

{
  "main_text": "Rav Soloveitchik emphasized that Jewish education must go beyond mere practice to encompass a lived experience of Judaism. This involves bringing imagination and vision into religious life, where we feel and experience the depths of our tradition. He taught that authentic transmission between generations requires more than knowledge—it demands empathy, prayer for others, and a genuine connection that transcends age barriers.",
  "source_numbers": [1, 3, 5, 8]
}

IMPORTANT NOTES:

- Your main_text should be a flowing, natural response—NOT a list of quotes

- The source_numbers array tells us which sources support your response

- We will return the exact original source texts to the user based on your source_numbers

- Focus on answering the question clearly and comprehensively`;

  // Generate response using GPT-5.2
  const completion = await openai.chat.completions.create({
    model: 'gpt-5.2-2025-12-11',
    messages: [
      { role: 'user', content: systemPrompt },
    ],
    temperature: 0.7,
    max_completion_tokens: 1000,
  });

  const rawResponse = completion.choices[0].message.content || '{}';

  // Parse the JSON response
  let parsedResponse: { main_text: string; source_numbers: number[] };
  try {
    parsedResponse = JSON.parse(rawResponse);
  } catch (error) {
    console.error('Error parsing LLM JSON response:', error);
    console.error('Raw response:', rawResponse);
    // Fallback response
    parsedResponse = {
      main_text: rawResponse,
      source_numbers: [],
    };
  }

  const message = parsedResponse.main_text;
  const sourceNumbers = parsedResponse.source_numbers || [];

  // Filter transcript_data to only include sources that were referenced
  const transcript_data = sourceNumbers
    .filter(num => num >= 1 && num <= allSources.length)
    .map(num => {
      const source = allSources[num - 1]; // Convert to 0-indexed
      return {
        number: num,
        text: source.text,
        source: `${source.slug} (${source.start_time} - ${source.end_time})`,
        slug: source.slug,
        start_time: source.start_time,
        end_time: source.end_time,
      };
    });

  // Create a prompt ID based on the configuration
  const prompt_id = `${config.embeddingModel}-${config.chunkingStrategy}`;

  return {
    message,
    transcript_data,
    prompt_id,
    config,
  };
}

