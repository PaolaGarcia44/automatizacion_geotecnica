'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, MessageCircle, Zap } from 'lucide-react'
import { MainLayout } from '@/layouts/MainLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const suggestedQuestions = [
  '¿Cuál es el CBR promedio del proyecto X?',
  'Resume el informe del municipio de Medellín',
  '¿Qué ensayos se realizaron en el proyecto Y?',
  'Analiza los resultados de cimentaciones',
]

const initialMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: 'Hola 👋 Soy tu asistente de IA para análisis geotécnico. Puedo ayudarte a resumir informes, analizar datos, responder preguntas sobre tus proyectos y mucho más. ¿En qué puedo ayudarte hoy?',
    timestamp: new Date(Date.now() - 5000),
  },
]

export default function AIPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim()
    if (!messageText) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // Simulate AI response
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `Esta es una respuesta simulada del asistente de IA. En una implementación real, aquí se conectaría con un modelo de lenguaje como OpenAI GPT-4 o Anthropic Claude para analizar tu pregunta: "${messageText}"\n\nEl asistente está completamente preparado para recibir respuestas reales del backend.`,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, assistantMessage])
    setIsLoading(false)
  }

  return (
    <MainLayout>
      <div className='page-padding container-main h-full flex flex-col'>
        {/* Page Header */}
        <div className='mb-6'>
          <h1 className='text-3xl font-bold text-secondary-900 mb-2 flex items-center gap-2'>
            <Zap className='h-8 w-8 text-primary-600' />
            Asistente de IA
          </h1>
          <p className='text-secondary-600'>
            Haz preguntas sobre tus proyectos geotécnicos y obtén análisis detallados
          </p>
        </div>

        <div className='flex-1 flex flex-col gap-6 min-h-0'>
          {/* Chat Container */}
          <Card className='border-secondary-200 flex-1 flex flex-col min-h-0'>
            {/* Messages Area */}
            <CardContent className='flex-1 overflow-y-auto p-6 space-y-4'>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user'
                      ? 'flex-row-reverse'
                      : 'flex-row'
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      message.role === 'user'
                        ? 'bg-primary-100 text-primary-600'
                        : 'bg-secondary-200 text-secondary-600'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <span className='text-sm font-bold'>TÚ</span>
                    ) : (
                      <Zap className='h-4 w-4' />
                    )}
                  </div>

                  {/* Message Bubble */}
                  <div
                    className={`flex-1 max-w-2xl ${
                      message.role === 'user'
                        ? 'text-right'
                        : 'text-left'
                    }`}
                  >
                    <div
                      className={`inline-block rounded-lg px-4 py-2 ${
                        message.role === 'user'
                          ? 'bg-primary-600 text-white rounded-br-none'
                          : 'bg-secondary-100 text-secondary-900 rounded-bl-none'
                      }`}
                    >
                      <p className='text-sm whitespace-pre-wrap'>
                        {message.content}
                      </p>
                    </div>
                    <p className='text-xs text-secondary-500 mt-1'>
                      {message.timestamp.toLocaleTimeString('es-CO', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className='flex gap-3'>
                  <div className='flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-secondary-200'>
                    <Loader2 className='h-4 w-4 text-secondary-600 animate-spin' />
                  </div>
                  <div className='bg-secondary-100 rounded-lg rounded-bl-none px-4 py-2'>
                    <div className='flex gap-1'>
                      <div className='w-2 h-2 bg-secondary-600 rounded-full animate-bounce' />
                      <div className='w-2 h-2 bg-secondary-600 rounded-full animate-bounce delay-100' />
                      <div className='w-2 h-2 bg-secondary-600 rounded-full animate-bounce delay-200' />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </CardContent>

            {/* Suggested Questions */}
            {messages.length === 1 && (
              <div className='border-t border-secondary-200 p-6 bg-secondary-50'>
                <p className='text-sm font-medium text-secondary-700 mb-3'>
                  Sugerencias de preguntas:
                </p>
                <div className='grid grid-cols-1 md:grid-cols-2 gap-2'>
                  {suggestedQuestions.map((question, i) => (
                    <Button
                      key={i}
                      variant='outline'
                      className='justify-start text-left h-auto py-2 px-3 text-sm'
                      onClick={() => handleSendMessage(question)}
                    >
                      <MessageCircle className='h-4 w-4 mr-2 flex-shrink-0' />
                      <span className='line-clamp-2'>{question}</span>
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className='border-t border-secondary-200 p-6 bg-white'>
              <div className='flex gap-2'>
                <Input
                  placeholder='Escribe tu pregunta...'
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !isLoading) {
                      handleSendMessage()
                    }
                  }}
                  disabled={isLoading}
                  className='flex-1'
                />
                <Button
                  onClick={() => handleSendMessage()}
                  disabled={!inputValue.trim() || isLoading}
                  className='gap-2'
                >
                  <Send className='h-4 w-4' />
                  <span className='hidden sm:inline'>Enviar</span>
                </Button>
              </div>
              <p className='text-xs text-secondary-500 mt-2'>
                ℹ️ El asistente de IA está preparado para recibir respuestas reales
                de modelos de lenguaje. Por ahora, muestra respuestas simuladas.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}
