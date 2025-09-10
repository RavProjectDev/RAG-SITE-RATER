import { NextRequest, NextResponse } from 'next/server';
import { BASE_URL } from '@/lib/utils';

// Fetch a full generated response for a given question
export async function POST(req: NextRequest) {
  try {
    const { question } = await req.json();
    if (!question || typeof question !== 'string') {
      return NextResponse.json({ error: 'Invalid question' }, { status: 400 });
    }

    // Explicitly call the backend full-response endpoint via GET with path param
    const url = `${BASE_URL}/form/full/${encodeURIComponent(question)}`;
    const response = await fetch(url, { method: 'GET' });
    if (!response.ok) {
      throw new Error(`Upstream error ${response.status} for ${url}`);
    }
    const data = await response.json();

    // Normalize to a simple shape { responses: [{ message, transcript_data, prompt_id }] }
    const normalize = (item: any) => {
      const message =
        typeof item?.llm_response === 'string' ? item.llm_response :
        (typeof item?.message === 'string' ? item.message : '');
      const transcript_data = Array.isArray(item?.transcript_data) ? item.transcript_data : [];
      const promptIdRaw = item?.prompt_id;
      const prompt_id = (typeof promptIdRaw === 'number' || typeof promptIdRaw === 'string') ? promptIdRaw : undefined;
      return { message, transcript_data, prompt_id };
    };

    let responses: Array<{ message: string; transcript_data: unknown[]; prompt_id?: string }>;
    if (Array.isArray(data)) {
      responses = data.map(normalize).map(r => ({ ...r, prompt_id: r.prompt_id != null ? String(r.prompt_id) : undefined }));
    } else if (Array.isArray(data?.responses)) {
      responses = data.responses.map(normalize).map((r: any) => ({ ...r, prompt_id: r.prompt_id != null ? String(r.prompt_id) : undefined }));
    } else if (typeof data === 'object' && data) {
      const r = normalize(data);
      responses = [{ ...r, prompt_id: r.prompt_id != null ? String(r.prompt_id) : undefined }];
    } else {
      responses = [];
    }

    return NextResponse.json({ responses });
  } catch (error) {
    console.error('Error in get_full_response:', error);
    return NextResponse.json({ error: (error instanceof Error ? error.message : 'Unknown error') }, { status: 500 });
  }
}

