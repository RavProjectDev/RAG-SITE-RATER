import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  // Parse the question from the request body (not used in mock)
  const { question } = await req.json();
  const data  = `Miriam's criticism of Moses. Her disapproval. It is hard to grasp that Miriam, the devoted and loyal sister who as a little girl stood
alone on the shore of the Nile, to watch the floating ark, because she had faith and hope, as far as her brother is concerned,
her little brother the baby in the ark, while all adults including the mother and father, resigned and abandoned the baby. 
This sister it is quite puzzling should suddenly turn into an accuser? Into prosecuting attorney? Of her great brother. 
Strange Equally un-understandable incomprehensible, is the strictness and the sadness and the speed with which the 
Almighty meted out`; // test 
  // Mock chunks
  const chunks = [
    { id: 'chunk1', content: data },
    { id: 'chunk2', content: data },
    { id: 'chunk3', content: data },
  ];

  return NextResponse.json({ chunks });
} 