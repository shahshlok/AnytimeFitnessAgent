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
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [showDisclaimer, setShowDisclaimer] = useState(true)
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
    setShowDisclaimer(false)
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
    setIsTranscribing(true)
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

      // Stop transcribing indicator and add user message
      setIsTranscribing(false)
      const userMessage = { id: Date.now(), role: 'user', content: transcribed_text }
      setMessages(prev => [...prev, userMessage])

      // Start loading indicator for AI response
      setIsLoading(true)

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
      setIsTranscribing(false)
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    setShowDisclaimer(false)
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
    <div className="min-h-screen flex items-center justify-center p-4 m-auto" style={{backgroundImage: 'url(https://cdn.prod.website-files.com/66aa8fe9dc4db68f448a978f/674d6f816fb0202f972b2ab7_line-blend-5-aqua.svg)', backgroundSize: 'cover', backgroundPosition: 'center', backgroundColor: '#440099'}}>
      <div className="bg-white flex flex-col max-w-[95vw] w-full h-[95vh] rounded-2xl drop-shadow-2xl"style={{backgroundColor: '#440099'}}>
        <header className="p-4  border-slate-700 flex justify-center">
          <img src="https://cdn.prod.website-files.com/66aa8fe9dc4db68f448a978f/6759b321193738fec4167167_logo-white-desktop.svg" alt="Anytime Fitness" className="h-8" />
        </header>
        
        {showDisclaimer && (
          <div className="bg-slate-800/30 border-b-2 border-[#EF3340] p-3 mx-4 mt-2 rounded-md">
            <div className="flex items-center justify-center">
              <div className="ml-3">
                <p className="text-s text-[#EF3340] font-bold ">
                  AI can make mistakes. Check important info with staff.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center space-y-4">
              <h2 className="text-2xl font-bold text-[#00AEC7]">Welcome</h2>
              <p className="text-[#00AEC7] max-w-md">
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
                      ? 'bg-[#6E38D5] text-white'
                      : 'bg-slate-800/60 text-slate-200'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.role === 'assistant' ? (
                      <div className="prose max-w-none prose-invert prose-p:text-slate-300 prose-li:text-slate-300">
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
          {isTranscribing && (
            <div className="flex justify-end">
              <div className="bg-[#6E38D5] rounded-2xl px-4 py-3">
                <div className="flex items-center space-x-1">
                  <div className="h-2 w-2 bg-blue-200 rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <div className="h-2 w-2 bg-blue-200 rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <div className="h-2 w-2 bg-blue-200 rounded-full animate-bounce" />
                </div>
              </div>
            </div>
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 text-slate-200 rounded-2xl px-4 py-3">
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

        <form onSubmit={handleSubmit} className="p-4 border-slate-700">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => {
                setInput(e.target.value)
                if (e.target.value.trim()) setShowDisclaimer(false)
              }}
              placeholder="Type your message..."
              className="flex-1 bg-slate-800/60 text-slate-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-violet-500"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={isRecording ? handleStopRecording : handleStartRecording}
              disabled={isLoading}
              className={`p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-slate-700 hover:bg-slate-600 text-slate-200'
              }`}
            >
              {isRecording ? <Square size={20} /> : <Mic size={20} />}
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="bg-[#6E38D5] text-white p-2 rounded-full hover:bg-[#5B2FB8] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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