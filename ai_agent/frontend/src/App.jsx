import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { SendHorizontal, Volume2, LoaderCircle, Mic, Square, RotateCcw } from 'lucide-react'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [playingAudioId, setPlayingAudioId] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [showDisclaimer, setShowDisclaimer] = useState(true)
  const [showResetPopup, setShowResetPopup] = useState(false)
  const [micError, setMicError] = useState('')
  const messagesEndRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const streamRef = useRef(null)
  const chatAbortControllerRef = useRef(null)
  const transcribeAbortControllerRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTranscribing])

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

  const requestMicrophonePermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // If successful, stop the stream immediately as we just wanted to trigger permission
      stream.getTracks().forEach(track => track.stop())
      setMicError('')
      // Now start actual recording
      await startRecordingLogic()
    } catch (error) {
      console.error('Permission request failed:', error)
      setMicError('Microphone access is still blocked. Please manually enable it in your browser settings.')
    }
  }

  const startRecordingLogic = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
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

  const handleStartRecording = async () => {
    setShowDisclaimer(false)
    setMicError('')
    
    try {
      const permissionStatus = await navigator.permissions.query({ name: 'microphone' })
      
      switch (permissionStatus.state) {
        case 'granted':
          await startRecordingLogic()
          break
        case 'prompt':
          await startRecordingLogic()
          break
        case 'denied':
          setMicError('Microphone access is blocked. Please enable it in your browser site settings.')
          break
        default:
          await startRecordingLogic()
      }
    } catch (error) {
      console.error('Error checking microphone permissions:', error)
      await startRecordingLogic()
    }
  }

  const handleStopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
    
    // Close the microphone stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop()
      })
      streamRef.current = null
    }
  }

  const sendAudioToApi = async (audioBlob) => {
    setIsTranscribing(true)
    try {
      const formData = new FormData()
      formData.append('file', audioBlob, 'user_voice_query.webm')

      // First API Call - Transcription
      transcribeAbortControllerRef.current = new AbortController()
      const transcribeResponse = await fetch('http://127.0.0.1:8000/transcribe', {
        method: 'POST',
        body: formData,
        signal: transcribeAbortControllerRef.current.signal
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
      chatAbortControllerRef.current = new AbortController()
      const chatResponse = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: transcribed_text,
          history: apiHistory
        }),
        signal: chatAbortControllerRef.current.signal
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

  const handleResetChat = () => {
    // Abort any ongoing API requests
    if (chatAbortControllerRef.current) {
      chatAbortControllerRef.current.abort()
      chatAbortControllerRef.current = null
    }
    if (transcribeAbortControllerRef.current) {
      transcribeAbortControllerRef.current.abort()
      transcribeAbortControllerRef.current = null
    }
    
    // Stop recording if active
    if (isRecording) {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop()
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => {
          track.stop()
        })
        streamRef.current = null
      }
    }
    
    // Reset all states to initial values
    setMessages([])
    setInput('')
    setIsLoading(false)
    setPlayingAudioId(null)
    setIsRecording(false)
    setIsTranscribing(false)
    setShowDisclaimer(true)
    
    // Clear audio chunks
    audioChunksRef.current = []
    
    // Show success popup
    setShowResetPopup(true)
    setTimeout(() => {
      setShowResetPopup(false)
    }, 3000)
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

      chatAbortControllerRef.current = new AbortController()
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          history: apiHistory
        }),
        signal: chatAbortControllerRef.current.signal
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
    <div className="min-h-screen flex items-center justify-center p-4 m-auto">
      {/* {showResetPopup && (
        <div className="absolute top-0 right-0 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 dark:bg-green-200 dark:text-white">
          Chat cleared successfully!
        </div>
      )} */}
      <div className="bg-white flex flex-col max-w-[95vw] w-full h-[95vh] rounded-2xl drop-shadow-2xl"style={{backgroundColor: '#ffffff'}}>
        <header className="p-4  border-slate-700 flex justify-center items-center relative">
          <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR27TJM9maic67yLPtJmNFfe1BcQdQi-GP8HQ&s" alt="Anytime Fitness" className="h-8" />
          <button
            onClick={handleResetChat}
            title="Clear chat"
            className="absolute bottom-2 right-4 text-gray-500 hover:text-gray-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
          >
            <RotateCcw size={20} />
          </button>
        </header>
        
        {showDisclaimer && (
          <div className="bg-white border-2 border-red-300 p-3 mx-4 mt-2 rounded-md">
            <div className="flex items-center justify-center">
              <div className="ml-3">
                <p className="text-s text-gray-500 font-bold ">
                  AI can make mistakes. Check important info with staff.
                </p>
              </div>
            </div>
          </div>
        )}
        {micError && (
          <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mx-4 mt-2 rounded-md">
            <div className="flex items-center justify-between">
              <p className="flex-1">{micError}</p>
              {micError.includes('blocked') && (
                <button
                  onClick={requestMicrophonePermission}
                  className="ml-4 px-3 py-1 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors text-sm font-medium"
                >
                  Try Again
                </button>
              )}
            </div>
          </div>
        )}
        {
          showResetPopup && (
            <div className="bg-white mx-auto mt-auto rounded-md">
            <div className="flex items-center justify-center">
              <div className="ml-3">
                <div className="bg-green-500 text-white px-2 py-2 rounded-lg shadow-lg z-50 dark:bg-green-200 dark:text-white">
                  Chat cleared successfully!
                </div>
              </div>
            </div>
          </div>
          )
        }
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
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
                  className={`${message.role === 'user' ? 'max-w-[80%]' : 'max-w-[64%]'} rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-[#6E38D5]/80 text-white'
                      : 'bg-gray-100 text-black'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.role === 'assistant' ? (
                      <div className="prose max-w-none prose-p:text-black prose-li:text-black prose-headings:text-black prose-strong:text-black">
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
                        className="p-1.5 rounded-full hover:bg-gray-200 transition-colors"
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
              <div className="bg-[#6E38D5]/80 rounded-2xl px-4 py-3">
                <div className="flex items-center space-x-1">
                  <div className="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <div className="h-2 w-2 bg-white rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <div className="h-2 w-2 bg-white rounded-full animate-bounce" />
                </div>
              </div>
            </div>
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-black rounded-2xl px-4 py-3">
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
                if (micError) setMicError('')
              }}
              placeholder="How can I help you today?"
              className="flex-1 bg-white text-slate-800 rounded-lg px-4 py-2 border-[#00AEC7] border-2 outline-none focus:border-[#00AEC7] focus:ring-1 focus:outline-none"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={isRecording ? handleStopRecording : handleStartRecording}
              disabled={isLoading}
              className={`p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed outline-none focus:outline-none active:outline-none ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 text-white' 
                  : 'bg-white hover:bg-gray-50 text-black border-2 border-red-500'
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