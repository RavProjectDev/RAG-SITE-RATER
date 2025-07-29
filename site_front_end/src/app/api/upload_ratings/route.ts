import { NextRequest, NextResponse } from 'next/server';
import { MAIN_URL } from '@/lib/utils';

export async function POST(req: NextRequest) {
  const { user_question, document, embedding_type } = await req.json();
  // Forward to FastAPI
  const response = await fetch(`${MAIN_URL}/form/upload_ratings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      "user_question": user_question,
      "data": document,
      "embedding_type": embedding_type,
    }),
  });

  const data = await response.json();
  return NextResponse.json(data);
} 