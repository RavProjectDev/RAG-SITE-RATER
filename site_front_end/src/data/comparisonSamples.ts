import type { ComparisonData } from "@/types/comparison";

/**
 * Sample comparison data for testing the A/B interface
 * Replace this with actual data from your LLM evaluation pipeline
 */
export const sampleComparisons: ComparisonData[] = [
  {
    query: "What are the main differences between React and Vue.js in terms of performance and learning curve?",
    modelA: {
      id: "model-a-1",
      modelName: "GPT-4",
      text: "React and Vue.js have distinct characteristics. React typically has a steeper learning curve [1] due to its JSX syntax and the need to understand concepts like hooks. However, React's virtual DOM implementation provides excellent performance for large applications [2]. Vue.js, on the other hand, is often praised for being more beginner-friendly [3] with its template-based syntax, and it also offers comparable performance to React in most scenarios.",
      citations: [
        {
          id: "a-1",
          number: 1,
          text: "React's learning curve can be steep for beginners, especially when dealing with JSX and component lifecycle methods. The introduction of Hooks has made things easier, but there's still a significant amount to learn.",
          source: "React Documentation - Getting Started",
        },
        {
          id: "a-2",
          number: 2,
          text: "React's virtual DOM efficiently updates and renders components, making it highly performant for complex, data-intensive applications. Benchmarks show React handles thousands of component updates per second.",
          source: "React Performance Optimization Guide",
        },
        {
          id: "a-3",
          number: 3,
          text: "Vue.js is designed to be incrementally adoptable and is often considered easier to learn than React. Its template syntax is familiar to developers who have worked with HTML.",
          source: "Vue.js Official Guide - Introduction",
        },
      ],
    },
    modelB: {
      id: "model-b-1",
      modelName: "Claude Sonnet",
      text: "When comparing React and Vue.js, several key differences emerge. React utilizes a component-based architecture with JSX [1], which can be challenging for newcomers but provides powerful composition patterns. Vue.js offers a gentler learning curve with its HTML-based template syntax [2]. In terms of performance, both frameworks are highly optimized, with React excelling in scenarios requiring frequent re-renders [3] and Vue providing excellent performance out-of-the-box with less configuration.",
      citations: [
        {
          id: "b-1",
          number: 1,
          text: "React uses JSX, a syntax extension that allows you to write HTML-like code in JavaScript. This provides great flexibility but requires understanding JavaScript ES6+ features.",
          source: "React Core Concepts Documentation",
        },
        {
          id: "b-2",
          number: 2,
          text: "Vue's single-file components use standard HTML, CSS, and JavaScript, making them accessible to developers familiar with web development basics. The framework gradually introduces more advanced concepts.",
          source: "Vue.js Core Team - Design Principles",
        },
        {
          id: "b-3",
          number: 3,
          text: "React's reconciliation algorithm and fiber architecture make it particularly efficient at handling frequent updates and complex component trees. Performance benchmarks consistently show React performing well in stress tests.",
          source: "JavaScript Framework Benchmarks 2024",
        },
      ],
    },
  },
  {
    query: "Explain the concept of quantum entanglement in simple terms.",
    modelA: {
      id: "model-a-2",
      modelName: "GPT-4",
      text: "Quantum entanglement is a phenomenon where two particles become connected in such a way that the state of one instantly affects the state of the other [1], regardless of the distance between them. Einstein famously called this 'spooky action at a distance' [2]. This doesn't allow for faster-than-light communication, but it has important applications in quantum computing and cryptography [3].",
      citations: [
        {
          id: "a2-1",
          number: 1,
          text: "When particles are entangled, measuring a property of one particle instantly determines the corresponding property of the other, no matter how far apart they are.",
          source: "Introduction to Quantum Mechanics - MIT OpenCourseWare",
        },
        {
          id: "a2-2",
          number: 2,
          text: "Albert Einstein, along with Podolsky and Rosen, questioned quantum entanglement in their famous EPR paper, referring to it as 'spooky action at a distance' because it seemed to violate the principle of locality.",
          source: "Einstein-Podolsky-Rosen Paradox - Stanford Encyclopedia of Philosophy",
        },
        {
          id: "a2-3",
          number: 3,
          text: "Quantum entanglement is fundamental to quantum computing, enabling quantum bits (qubits) to process information in ways classical bits cannot. It's also used in quantum key distribution for secure communication.",
          source: "Quantum Computing: An Applied Approach - Springer 2023",
        },
      ],
    },
    modelB: {
      id: "model-b-2",
      modelName: "Claude Sonnet",
      text: "Quantum entanglement occurs when pairs or groups of particles interact in ways that make their quantum states interdependent [1]. Think of it like having two magic coins: when you flip one and it lands on heads, the other instantly becomes tails, no matter where it is [2]. This counterintuitive property has been experimentally verified and forms the basis of emerging quantum technologies [3].",
      citations: [
        {
          id: "b2-1",
          number: 1,
          text: "Entangled particles share a quantum state, meaning the quantum properties of one particle cannot be described independently of the others, even when separated by large distances.",
          source: "Quantum Entanglement and Bell's Theorem - Nature Physics Review",
        },
        {
          id: "b2-2",
          number: 2,
          text: "A common analogy for entanglement involves correlated measurements: if entangled particles are measured, their outcomes will be correlated in specific ways predicted by quantum mechanics, as if they 'know' about each other instantly.",
          source: "Understanding Quantum Mechanics - Oxford University Press",
        },
        {
          id: "b2-3",
          number: 3,
          text: "Experiments by Alain Aspect and others have conclusively demonstrated quantum entanglement, with the 2022 Nobel Prize in Physics awarded for work proving that quantum mechanics accurately describes these phenomena.",
          source: "Nobel Prize in Physics 2022 - Scientific Background",
        },
      ],
    },
  },
];

/**
 * Utility function to get a random comparison
 */
export function getRandomComparison(): ComparisonData {
  const randomIndex = Math.floor(Math.random() * sampleComparisons.length);
  return sampleComparisons[randomIndex];
}

/**
 * Utility function to get a comparison by index
 */
export function getComparisonByIndex(index: number): ComparisonData | null {
  if (index >= 0 && index < sampleComparisons.length) {
    return sampleComparisons[index];
  }
  return null;
}

