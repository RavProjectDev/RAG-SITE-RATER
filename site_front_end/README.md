# LLM Response Evaluator

A modern, user-friendly platform for comparing and evaluating LLM (Large Language Model) responses with advanced features for citation verification and hallucination detection.

![Homepage Screenshot](docs/screenshot-homepage.png)

## 🌟 Features

### 3-Layer Evaluation System

1. **Primary Vote** - Choose which response is better
   - "A is better"
   - "B is better"
   - "Tie"
   - "Both bad"

2. **Citation Verification** - Click citations to verify sources
   - Rate as "Supported" ✅ or "Not Supported" ❌
   - Visual feedback with color coding
   - Popover displays source snippets

3. **Hallucination Flagging** - Report problematic responses
   - Factually Incorrect
   - Ignored my instructions
   - Made up information (Hallucination)

### User Experience

- **🎭 Blind Testing** - Model names hidden until after voting (prevents brand bias)
- **📱 Mobile-Friendly** - Fully responsive design works on all devices
- **⚡ Fast & Simple** - Vote in under 10 seconds
- **🎨 Modern UI** - Clean design with Tailwind CSS and shadcn/ui
- **♿ Accessible** - Keyboard navigation and screen reader support

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- API Keys (OpenAI, Cohere, Gemini, Pinecone) - See [ENV_SETUP.md](ENV_SETUP.md)

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables (see ENV_SETUP.md)
cp .env.example .env.local
# Edit .env.local with your API keys

# Run development server
npm run dev
```

Visit `http://localhost:3000` to see the homepage.

### RAG Pipeline Setup

This application includes a **complete RAG (Retrieval-Augmented Generation) pipeline** that runs entirely in the frontend API. For detailed documentation, see [RAG_IMPLEMENTATION.md](RAG_IMPLEMENTATION.md).

**Key Features:**
- 🎲 **9 Configurations**: 3 embedding models × 3 chunking strategies
- 🔀 **Random Selection**: Each question uses 2 randomly selected configurations
- 🧠 **Multi-Model Support**: OpenAI, Cohere, and Gemini embeddings
- 📊 **Pinecone Integration**: Vector database for document retrieval
- ⚡ **Parallel Processing**: Both responses generated simultaneously
- 🎯 **GPT-4o-mini**: Generates final responses with citations

**Quick Setup:**
1. Set up Pinecone indexes: `openai`, `cohere`, `gemini`
2. Create namespaces: `fixed-size`, `semantic`, `sliding-window`
3. Add API keys to `.env.local`
4. Start the development server

See [ENV_SETUP.md](ENV_SETUP.md) for detailed API key setup instructions.

## 📁 Project Structure

```
src/
├── app/
│   ├── comparison/          # A/B comparison interface
│   │   └── page.tsx
│   ├── api/
│   │   ├── get_full_response/  # RAG pipeline endpoint
│   │   │   └── route.ts
│   │   └── submit_comparison/  # API for submitting results
│   │       └── route.ts
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Homepage
├── components/
│   ├── ui/                  # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── popover.tsx
│   │   ├── checkbox.tsx
│   │   └── ...
│   ├── CitationPopover.tsx  # Citation verification component
│   └── HallucinationFlagModal.tsx  # Hallucination reporting
├── lib/
│   ├── rag-config.ts        # RAG configurations (9 combinations)
│   ├── embeddings.ts        # Embedding generation (OpenAI, Cohere, Gemini)
│   ├── pinecone-client.ts   # Pinecone vector database queries
│   ├── llm-generator.ts     # LLM response generation
│   └── utils.ts             # Utility functions
├── types/
│   └── comparison.ts        # TypeScript type definitions
└── data/
    └── comparisonSamples.ts # Sample data for testing
```

## 🎯 Usage

### For Evaluators

1. Visit the homepage at `/`
2. Click "Start Comparing Responses"
3. Read both responses
4. (Optional) Click citations to verify sources
5. (Optional) Flag any hallucinations or issues
6. Vote for the better response
7. Click "Next Question" to continue

### For Developers

#### Customize Sample Data

Edit `src/data/comparisonSamples.ts`:

```typescript
export const sampleComparisons: ComparisonData[] = [
  {
    query: "Your question here",
    modelA: {
      id: "unique-id",
      modelName: "Model Name",
      text: "Response with citations [1] [2]",
      citations: [...]
    },
    modelB: { ... }
  }
];
```

#### Fetch Data from API

Modify `src/app/comparison/page.tsx`:

```typescript
useEffect(() => {
  fetch('/api/get_comparison')
    .then(res => res.json())
    .then(data => setData(data));
}, []);
```

#### Store Results in Database

Update `src/app/api/submit_comparison/route.ts`:

```typescript
// Add your database logic here
await db.comparisons.create({
  data: {
    vote: data.vote,
    timestamp: new Date(data.timestamp),
    // ... other fields
  },
});
```

## 📊 Data Captured

Each comparison submission includes:

```typescript
{
  vote: "A" | "B" | "tie" | "both_bad",
  timestamp: number,
  hallucination_flags: {
    modelA: HallucinationFlag[],
    modelB: HallucinationFlag[]
  },
  citation_ratings: {
    [citationId]: "supported" | "not_supported"
  },
  model_a_id: string,
  model_b_id: string,
  query: string
}
```

## 🎨 Tech Stack

### Frontend
- **Framework**: Next.js 15.4.2 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui (Radix UI)
- **Icons**: Lucide React

### RAG Pipeline
- **Vector Database**: Pinecone
- **Embedding Models**: OpenAI, Cohere, Gemini
- **LLM Generation**: OpenAI GPT-4o-mini
- **Document Retrieval**: Top-K similarity search (k=3)

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - Get up and running quickly
- [RAG Implementation](RAG_IMPLEMENTATION.md) - Complete RAG pipeline documentation
- [Environment Setup](ENV_SETUP.md) - API keys and configuration guide
- [Comparison Interface Documentation](COMPARISON_INTERFACE.md) - Detailed feature docs

## 🧪 Testing

```bash
# Run linter
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

## 🔒 Privacy & Ethics

- All model names are hidden during evaluation to prevent bias
- No personal data is collected without consent
- Evaluations are used solely for improving AI systems

## 🛣️ Roadmap

- [ ] User authentication and session management
- [ ] Analytics dashboard for aggregated results
- [ ] Export evaluation data as CSV/JSON
- [ ] Multi-language support
- [ ] Advanced filtering and search
- [ ] Integration with popular LLM APIs

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of the RAG-SITE-RATER evaluation platform.

## 🙏 Acknowledgments

Built with modern web technologies and best practices for AI evaluation.

---

**Status**: ✅ Production Ready  
**Last Updated**: December 21, 2025

For questions or support, please open an issue on GitHub.
