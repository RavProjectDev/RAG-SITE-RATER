import { NextRequest, NextResponse } from "next/server";
import type { ComparisonResult } from "@/types/comparison";
import { getUserFormsResponseCollection } from "@/lib/mongodb";

export async function POST(request: NextRequest) {
  try {
    const data: ComparisonResult = await request.json();

    // Validate the data
    if (!data.vote || !data.model_a_id || !data.model_b_id) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Prepare document for MongoDB
    const document = {
      vote: data.vote,
      timestamp: new Date(data.timestamp),
      query: data.query,
      model_a_id: data.model_a_id,
      model_b_id: data.model_b_id,
      model_a_response: data.model_a_response,
      model_b_response: data.model_b_response,
      hallucination_flags: data.hallucination_flags,
      created_at: new Date(), // Additional timestamp for when it was saved to DB
    };

    // Save to MongoDB
    const collection = await getUserFormsResponseCollection();
    const result = await collection.insertOne(document);

    // Log the comparison result
    console.log("Comparison Result saved to MongoDB:", {
      insertedId: result.insertedId,
      vote: data.vote,
      timestamp: new Date(data.timestamp).toISOString(),
      query: data.query,
      model_a: data.model_a_id,
      model_b: data.model_b_id,
    });

    return NextResponse.json(
      { 
        success: true,
        message: "Comparison submitted successfully",
        data: {
          id: result.insertedId.toString(),
          vote: data.vote,
          timestamp: data.timestamp,
        }
      },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error processing comparison submission:", error);
    
    // Provide more specific error messages
    if (error instanceof Error) {
      if (error.message.includes('MONGODB_URI')) {
        return NextResponse.json(
          { error: "Database configuration error. Please check MONGODB_URI environment variable." },
          { status: 500 }
        );
      }
    }
    
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

