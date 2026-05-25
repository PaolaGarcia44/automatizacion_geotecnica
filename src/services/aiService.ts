// AI Assistant service
// Prepared for future LLM integration (OpenAI, Anthropic, or backend FastAPI)

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface AskQuestionRequest {
  question: string
  projectId?: string
  context?: Record<string, unknown>
}

export interface AskQuestionResponse {
  answer: string
  confidence?: number
  sources?: string[]
}

/**
 * Ask a question to the AI assistant about geotechnical projects
 * Prepared for OpenAI, Anthropic, or custom FastAPI backend
 * @param request - Question and context
 * @returns Promise with AI response
 */
export const askQuestion = async (
  _request: AskQuestionRequest
): Promise<AskQuestionResponse> => {
  console.log('AI question answering is not yet implemented.')
  console.log('This service is prepared for:')
  console.log('- OpenAI GPT-4 integration')
  console.log('- Anthropic Claude integration')
  console.log('- Custom FastAPI backend with LLM')

  return {
    answer: 'The AI assistant is prepared but not yet connected. Please configure your LLM provider in environment variables.',
    confidence: 0,
    sources: [],
  }
}

/**
 * Generate suggested questions based on document context
 * @param projectId - Project identifier
 * @returns Promise with suggested questions
 */
export const getSuggestedQuestions = async (
  _projectId?: string
): Promise<string[]> => {
  console.log('Suggested questions generation is not yet implemented')
  return [
    '¿Cuál es el CBR promedio del proyecto?',
    'Resume los resultados de los ensayos de laboratorio',
    '¿Cuáles son las principales recomendaciones?',
  ]
}

/**
 * Chat with the AI assistant (streaming prepared)
 * @param messages - Chat history
 * @returns Promise with streaming response
 */
export const streamChat = async (
  _messages: ChatMessage[]
): Promise<AsyncGenerator<string, void, unknown> | null> => {
  console.log('AI streaming chat is prepared but not yet implemented')
  return null
}

/**
 * Analyze a geotechnical document with AI
 * @param documentContent - Document text
 * @param analysisType - Type of analysis requested
 * @returns Promise with analysis result
 */
export const analyzeDocument = async (
  _documentContent: string,
  _analysisType: string
): Promise<string> => {
  console.log('Document analysis is prepared but not yet implemented')
  return 'Document analysis feature is coming soon'
}
