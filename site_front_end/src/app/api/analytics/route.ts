import { NextRequest, NextResponse } from "next/server";
import { getUserFormsResponseCollection } from "@/lib/mongodb";
import { calculateEloRatings, getLeaderboard } from "@/lib/elo-rating";

export async function GET(req: NextRequest) {
  try {
    // Check password from query parameter
    const searchParams = req.nextUrl.searchParams;
    const providedPassword = searchParams.get("password");
    const expectedPassword = process.env.PASSCODE;

    if (!expectedPassword) {
      return NextResponse.json(
        { error: "Analytics not configured. PASSCODE not set." },
        { status: 500 }
      );
    }

    if (!providedPassword || providedPassword !== expectedPassword) {
      return NextResponse.json(
        { error: "Unauthorized. Invalid password." },
        { status: 401 }
      );
    }

    // Fetch data from MongoDB
    const collection = await getUserFormsResponseCollection();

    // Get all responses
    const allResponses = await collection.find({}).sort({ created_at: -1 }).toArray();

    // Calculate analytics
    const totalResponses = allResponses.length;

    // Calculate Elo ratings from all comparisons
    const comparisons = allResponses.map((r) => ({
      model_a_id: r.model_a_id,
      model_b_id: r.model_b_id,
      vote: r.vote as 'A' | 'B' | 'tie' | 'both_bad',
    }));

    const eloMap = calculateEloRatings(comparisons);
    const leaderboard = getLeaderboard(eloMap);

    // Also keep the old modelWins format for backward compatibility
    const modelWins: Record<string, { wins: number; losses: number; ties: number; bothBad: number }> = {};
    leaderboard.forEach((rating) => {
      modelWins[rating.configuration] = {
        wins: rating.wins,
        losses: rating.losses,
        ties: rating.ties,
        bothBad: rating.bothBad,
      };
    });

    // Hallucination flags - broken down by model
    let totalFlags = 0;
    const flagTypes: Record<string, number> = {};
    const flagsByModel: Record<string, Record<string, number>> = {};

    allResponses.forEach((response) => {
      if (response.hallucination_flags) {
        const flagsA = response.hallucination_flags.modelA || [];
        const flagsB = response.hallucination_flags.modelB || [];
        
        // Track flags for model A
        const modelAId = response.model_a_id;
        if (!flagsByModel[modelAId]) {
          flagsByModel[modelAId] = {};
        }
        flagsA.forEach((flag) => {
          flagTypes[flag] = (flagTypes[flag] || 0) + 1;
          flagsByModel[modelAId][flag] = (flagsByModel[modelAId][flag] || 0) + 1;
          totalFlags++;
        });
        
        // Track flags for model B
        const modelBId = response.model_b_id;
        if (!flagsByModel[modelBId]) {
          flagsByModel[modelBId] = {};
        }
        flagsB.forEach((flag) => {
          flagTypes[flag] = (flagTypes[flag] || 0) + 1;
          flagsByModel[modelBId][flag] = (flagsByModel[modelBId][flag] || 0) + 1;
          totalFlags++;
        });
      }
    });

    // Recent responses (last 10) - include actual response messages
    const recentResponses = allResponses.slice(0, 10).map((r) => ({
      _id: r._id.toString(),
      vote: r.vote,
      query: r.query,
      model_a_id: r.model_a_id,
      model_b_id: r.model_b_id,
      model_a_response: r.model_a_response || "Response not available",
      model_b_response: r.model_b_response || "Response not available",
      timestamp: r.timestamp,
      created_at: r.created_at,
      has_flags: !!(
        (r.hallucination_flags?.modelA?.length || 0) > 0 ||
        (r.hallucination_flags?.modelB?.length || 0) > 0
      ),
      hallucination_flags: r.hallucination_flags || { modelA: [], modelB: [] },
    }));

    return NextResponse.json({
      summary: {
        totalResponses,
        hallucinationStats: {
          total: totalFlags,
          byType: flagTypes,
          byModel: flagsByModel,
        },
      },
      leaderboard: leaderboard.map((rating, index) => ({
        rank: index + 1,
        configuration: rating.configuration,
        elo: Math.round(rating.elo),
        winRate: rating.winRate,
        wins: rating.wins,
        losses: rating.losses,
        ties: rating.ties,
        bothBad: rating.bothBad,
        totalComparisons: rating.totalComparisons,
      })),
      modelPerformance: modelWins,
      recentResponses,
    });
  } catch (error) {
    console.error("Error fetching analytics:", error);
    return NextResponse.json(
      { error: "Failed to fetch analytics data" },
      { status: 500 }
    );
  }
}

