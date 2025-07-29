import { NextRequest, NextResponse } from 'next/server';
import { MAIN_URL } from '@/lib/utils';

export async function POST(req: NextRequest) {
  try {
    // Parse the question from the request body (not used in mock)
    const { question } = await req.json();
    const response = await fetch(`${MAIN_URL}/form/${question}`, {
      method: 'GET',
    });
    if (!response.ok) {
      throw new Error(`Upstream error: ${response.status}`);
    }
    const data = await response.json();
    // Map the first 3 items from the response to chunks
    const documents = data.documents;
    const chunks = Array.isArray(documents) ? documents.slice(0, 3).map(item => ({ ...item })) : [];
    const embedding_type = data.embedding_type;
    return NextResponse.json({ chunks, embedding_type });
  } catch (error) {
    console.error('Error in get_chunks:', error);
    return NextResponse.json({ error: (error instanceof Error ? error.message : 'Unknown error'), chunks: [] }, { status: 500 });
  }
}
