// Elo Rating System for Model Comparison

export interface EloRating {
  configuration: string;
  elo: number;
  wins: number;
  losses: number;
  ties: number;
  bothBad: number;
  totalComparisons: number;
  winRate: number;
}

/**
 * Calculate Elo rating updates based on match result
 * @param eloA - Current Elo of model A
 * @param eloB - Current Elo of model B
 * @param result - 'A' if A wins, 'B' if B wins, 'tie' if tie, 'both_bad' if both bad
 * @param kFactor - K-factor (default 32, standard for chess)
 * @returns Updated Elo ratings for both models
 */
export function calculateEloUpdate(
  eloA: number,
  eloB: number,
  result: 'A' | 'B' | 'tie' | 'both_bad',
  kFactor: number = 32
): { newEloA: number; newEloB: number } {
  // Expected score for A (probability of A winning)
  const expectedA = 1 / (1 + Math.pow(10, (eloB - eloA) / 400));
  const expectedB = 1 - expectedA;

  // Actual score based on result
  let actualA: number;
  let actualB: number;

  switch (result) {
    case 'A':
      // A wins
      actualA = 1;
      actualB = 0;
      break;
    case 'B':
      // B wins
      actualA = 0;
      actualB = 1;
      break;
    case 'tie':
      // Tie
      actualA = 0.5;
      actualB = 0.5;
      break;
    case 'both_bad':
      // Both bad - treat as tie (no one wins)
      actualA = 0.5;
      actualB = 0.5;
      break;
    default:
      actualA = 0.5;
      actualB = 0.5;
  }

  // Calculate new Elo ratings
  const newEloA = eloA + kFactor * (actualA - expectedA);
  const newEloB = eloB + kFactor * (actualB - expectedB);

  return { newEloA, newEloB };
}

/**
 * Process all comparisons and calculate Elo ratings for all configurations
 * @param comparisons - Array of comparison results from database
 * @returns Map of configuration to EloRating
 */
export function calculateEloRatings(
  comparisons: Array<{
    model_a_id: string;
    model_b_id: string;
    vote: 'A' | 'B' | 'tie' | 'both_bad';
  }>
): Map<string, EloRating> {
  // Initialize all configurations with 1000 Elo
  const eloMap = new Map<string, EloRating>();
  const initialElo = 1000;

  // First pass: collect all unique configurations and initialize
  comparisons.forEach((comp) => {
    if (!eloMap.has(comp.model_a_id)) {
      eloMap.set(comp.model_a_id, {
        configuration: comp.model_a_id,
        elo: initialElo,
        wins: 0,
        losses: 0,
        ties: 0,
        bothBad: 0,
        totalComparisons: 0,
        winRate: 0,
      });
    }
    if (!eloMap.has(comp.model_b_id)) {
      eloMap.set(comp.model_b_id, {
        configuration: comp.model_b_id,
        elo: initialElo,
        wins: 0,
        losses: 0,
        ties: 0,
        bothBad: 0,
        totalComparisons: 0,
        winRate: 0,
      });
    }
  });

  // Second pass: process comparisons chronologically and update Elo
  // Sort by timestamp if available (for more accurate progression)
  comparisons.forEach((comp) => {
    const configA = eloMap.get(comp.model_a_id)!;
    const configB = eloMap.get(comp.model_b_id)!;

    // Update Elo ratings
    const { newEloA, newEloB } = calculateEloUpdate(
      configA.elo,
      configB.elo,
      comp.vote
    );

    configA.elo = newEloA;
    configB.elo = newEloB;

    // Update statistics
    configA.totalComparisons++;
    configB.totalComparisons++;

    switch (comp.vote) {
      case 'A':
        configA.wins++;
        configB.losses++;
        break;
      case 'B':
        configA.losses++;
        configB.wins++;
        break;
      case 'tie':
        configA.ties++;
        configB.ties++;
        break;
      case 'both_bad':
        configA.bothBad++;
        configB.bothBad++;
        break;
    }
  });

  // Calculate win rates
  eloMap.forEach((rating) => {
    const totalDecisive = rating.wins + rating.losses;
    rating.winRate = totalDecisive > 0 ? (rating.wins / totalDecisive) * 100 : 0;
  });

  return eloMap;
}

/**
 * Convert Elo map to sorted leaderboard array
 */
export function getLeaderboard(eloMap: Map<string, EloRating>): EloRating[] {
  return Array.from(eloMap.values()).sort((a, b) => b.elo - a.elo);
}

