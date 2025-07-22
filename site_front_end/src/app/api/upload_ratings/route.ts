import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  // Parse ratings from the request body
  const { ratings } = await req.json();

  // In a real app, you would store ratings here
  // For mock, just return success
  return NextResponse.json({ success: true });
} 