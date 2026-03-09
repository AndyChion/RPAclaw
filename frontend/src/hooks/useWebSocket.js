import { useState, useCallback, useRef, useEffect } from 'react'

export function useWebSocket(url) {
    const [messages, setMessages] = useState([])
    const [isConnected, setIsConnected] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const wsRef = useRef(null)
    const reconnectTimer = useRef(null)

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = url || `${protocol}//${window.location.host}/ws/chat`
        const ws = new WebSocket(wsUrl)

        ws.onopen = () => {
            setIsConnected(true)
            clearTimeout(reconnectTimer.current)
        }

        ws.onclose = () => {
            setIsConnected(false)
            setIsLoading(false)
            reconnectTimer.current = setTimeout(connect, 3000)
        }

        ws.onerror = () => {
            setIsConnected(false)
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)

                if (data.type === 'progress') {
                    setMessages(prev => {
                        const last = prev[prev.length - 1]
                        if (last?.type === 'progress') {
                            return [...prev.slice(0, -1), { ...data, role: 'assistant' }]
                        }
                        return [...prev, { ...data, role: 'assistant' }]
                    })
                } else if (data.type === 'message') {
                    setMessages(prev => {
                        // Replace last progress with final message
                        const filtered = prev.filter(m => m.type !== 'progress')
                        return [...filtered, { ...data, role: 'assistant' }]
                    })
                    setIsLoading(false)
                } else if (data.type === 'error') {
                    setMessages(prev => [...prev, { ...data, role: 'assistant' }])
                    setIsLoading(false)
                }
            } catch (e) {
                console.error('WebSocket parse error:', e)
            }
        }

        wsRef.current = ws
    }, [url])

    const sendMessage = useCallback((content, sessionKey = 'webui:default') => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

        setMessages(prev => [...prev, { type: 'message', role: 'user', content }])
        setIsLoading(true)

        wsRef.current.send(JSON.stringify({ content, session_key: sessionKey }))
    }, [])

    const clearMessages = useCallback(() => {
        setMessages([])
    }, [])

    useEffect(() => {
        connect()
        return () => {
            clearTimeout(reconnectTimer.current)
            wsRef.current?.close()
        }
    }, [connect])

    return { messages, isConnected, isLoading, sendMessage, clearMessages }
}
