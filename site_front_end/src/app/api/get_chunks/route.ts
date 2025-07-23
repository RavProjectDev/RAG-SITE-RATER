import { NextRequest, NextResponse } from 'next/server';
import { MAIN_URL } from '@/lib/utils';

export async function POST(req: NextRequest) {
  // Parse the question from the request body (not used in mock)
  const { question } = await req.json();
  const response = await fetch(`${MAIN_URL}/form/${question}`, {
    method: 'GET',
  });
  const data = await response.json();
  // Map the first 3 items from the response to chunks
  const chunks = Array.isArray(data) ? data.slice(0, 3).map(item => ({ ...item })) : [];

  return NextResponse.json({ chunks });
}
