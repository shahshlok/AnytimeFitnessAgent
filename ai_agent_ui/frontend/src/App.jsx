import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { SendHorizontal, Volume2, LoaderCircle, Mic, Square } from 'lucide-react'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [playingAudioId, setPlayingAudioId] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const messagesEndRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handlePlayAudio = async (text, messageId) => {
    setPlayingAudioId(messageId)
    try {
      const response = await fetch('http://127.0.0.1:8000/speak', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        throw new Error('Failed to get audio')
      }

      const audioBlob = await response.blob()
      const audio = new Audio(URL.createObjectURL(audioBlob))
      await audio.play()
    } catch (error) {
      console.error('Error playing audio:', error)
    } finally {
      setPlayingAudioId(null)
    }
  }

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        sendAudioToApi(audioBlob)
        audioChunksRef.current = []
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Error accessing microphone:', error)
      setMessages(prev => [...prev, { 
        id: Date.now(),
        role: 'assistant', 
        content: 'Sorry, I could not access your microphone. Please ensure you have granted microphone permissions.' 
      }])
    }
  }

  const handleStopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const sendAudioToApi = async (audioBlob) => {
    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'user_voice_query.webm')

      // First API Call - Transcription
      const transcribeResponse = await fetch('http://127.0.0.1:8000/transcribe', {
        method: 'POST',
        body: formData,
      })

      if (!transcribeResponse.ok) {
        throw new Error('Failed to transcribe audio')
      }

      const { transcribed_text } = await transcribeResponse.json()
      
      if (!transcribed_text || transcribed_text.trim() === '') {
        throw new Error('No speech detected in audio')
      }

      // Immediate UI Update - Add user message
      const userMessage = { id: Date.now(), role: 'user', content: transcribed_text }
      setMessages(prev => [...prev, userMessage])

      // Get current history before adding the new user message
      const apiHistory = messages.map(msg => ({ role: msg.role, content: msg.content }))

      // Second API Call - AI Response
      const chatResponse = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: transcribed_text,
          history: apiHistory
        }),
      })

      if (!chatResponse.ok) {
        throw new Error('Failed to get AI response')
      }

      const { reply } = await chatResponse.json()
      
      // Add assistant's message to chat
      setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', content: reply }])
    } catch (error) {
      console.error('Error processing voice input:', error)
      setMessages(prev => [...prev, { 
        id: Date.now(),
        role: 'assistant', 
        content: 'Sorry, I encountered an error processing your voice input. Please try again.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = { id: Date.now(), role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const apiHistory = messages.map(msg => ({ role: msg.role, content: msg.content }));

      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          history: apiHistory
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      setMessages(prev => [...prev, { id: Date.now(), role: 'assistant', content: data.reply }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        id: Date.now(),
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white min-h-screen flex items-center justify-center p-4">
      <div className="bg-gray-50 flex flex-col max-w-4xl w-full h-[95vh] rounded-2xl border border-gray-200 shadow-sm">
        <header className="p-4 border-b border-gray-200">
          <h1 className="text-lg font-semibold text-gray-800">Anytime Fitness AI Assistant</h1>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4">
              <h2 className="text-2xl font-semibold text-gray-800">Welcome</h2>
              <p className="text-gray-600 max-w-md">
                Ask me anything about Anytime Fitness!
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.role === 'assistant' ? (
                      <div className="prose max-w-none prose-p:text-gray-800 prose-li:text-gray-800">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      message.content
                    )}
                    {message.role === 'assistant' && (
                      <button
                        onClick={() => handlePlayAudio(message.content, message.id)}
                        className="p-1.5 rounded-full hover:bg-slate-700 transition-colors"
                        disabled={playingAudioId === message.id}
                      >
                        {playingAudioId === message.id ? (
                          <LoaderCircle size={16} className="animate-spin" />
                        ) : (
                          <Volume2 size={16} />
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 rounded-2xl px-4 py-3">
                <div className="flex items-center space-x-1">
                  <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-white text-gray-800 rounded-lg px-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={isRecording ? handleStopRecording : handleStartRecording}
              disabled={isLoading}
              className={`p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
              }`}
            >
              {isRecording ? <Square size={20} /> : <Mic size={20} />}
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <SendHorizontal size={20} />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default App