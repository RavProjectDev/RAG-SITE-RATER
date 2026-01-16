/**
 * Example questions for RAG evaluation
 * These questions cycle in round-robin fashion
 */

export const EXAMPLE_QUESTIONS = [
  // God's Nature and Attributes
  "How can we prove God exists?",
  "If God is all-powerful, why does He need our prayers?",
  "Does God have emotions like anger or joy?",
  "How can a finite human relate to an infinite God?",
  "Why does God remain 'hidden' in the modern world?",
  "Does God care about the small details of my daily life?",
  "Is God involved in every historical event, or does He step back?",
  "What does it mean to be created in the 'Image of God'?",
  "How can God be both merciful and just simultaneously?",
  "Is it a sin to be angry with God?",

  // Suffering and Evil
  "Why do bad things happen to good people?",
  "Is suffering a punishment or a test?",
  "Does evil have an independent existence, or is it the absence of good?",
  "How should we react to natural disasters from a faith perspective?",
  "Can any positive meaning be found in tragedy?",
  "Why is there more 'bad' in the world than 'good'?",
  "Does God suffer when we suffer?",
  "How do we explain the existence of the 'Evil Inclination' (Yetzer Hara)?",
  "Why must growth often come through pain?",

  // Free Will and Destiny
  "If God knows the future, do we truly have free will?",
  "Is my life's path predetermined or created by my choices?",
  "Does 'Besheret' (destiny) apply to everything or just marriage?",
  "How much of my success is my effort versus God's help?",
  "Can prayer change a decree that God has already made?",
  "Are some people born with a 'holier' soul than others?",
  "Why are some people given harder life tests than others?",
  "Is 'luck' a Jewish concept?",
  "How do we balance 'trust in God' with 'personal initiative'?",

  // The Soul and Afterlife
  "Is there a Jewish version of 'Heaven' and 'Hell'?",
  "Do Jews believe in reincarnation (Gilgul)?",
  "Can souls interact with the living?",
  "What is the 'World to Come' (Olam Ha-Ba)?",
  "Will there be a physical resurrection of the dead?",
  "Do non-Jews have a place in the afterlife?",
  "How does our behavior here affect our soul's 'rank' later?",
  "Is the soul eternal, or can it be destroyed?",

  // Meaning and Purpose
  "What is the ultimate purpose of creation?",
  "Why did God create the world if He is already perfect?",
  "Is the primary goal of Judaism to be happy or to be holy?",
  "How do I find my specific spiritual 'mission' in the world?",
  "Is it better to do a good deed with the wrong intent or not at all?",
  "Why do we need 613 commandments to be 'good'?",
  "What is the Jewish view on the meaning of life?",
  "Can a person ever be 'too' religious?",
  "How do we define a 'miracle' in a scientific age?",
  "What is the significance of the Jewish people in the grand scheme of the universe?",
];

/**
 * Get the next question in round-robin fashion
 * Uses a simple counter stored in localStorage
 */
export function getNextExampleQuestion(): string {
  if (typeof window === 'undefined') {
    // Server-side: return first question
    return EXAMPLE_QUESTIONS[0];
  }

  try {
    // Get current index from localStorage
    const currentIndex = parseInt(localStorage.getItem('exampleQuestionIndex') || '0', 10);
    
    // Get the question
    const question = EXAMPLE_QUESTIONS[currentIndex];
    
    // Increment and wrap around
    const nextIndex = (currentIndex + 1) % EXAMPLE_QUESTIONS.length;
    localStorage.setItem('exampleQuestionIndex', nextIndex.toString());
    
    return question;
  } catch (error) {
    // Fallback if localStorage is not available
    return EXAMPLE_QUESTIONS[0];
  }
}

/**
 * Get a random example question
 */
export function getRandomExampleQuestion(): string {
  const randomIndex = Math.floor(Math.random() * EXAMPLE_QUESTIONS.length);
  return EXAMPLE_QUESTIONS[randomIndex];
}

