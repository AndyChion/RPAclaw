import { useState, useRef, useEffect } from 'react'
import { Send, Trash2, Bot, User } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'

export default function Chat() {
    const { messages, isConnected, isLoading, sendMessage, clearMessages } = useWebSocket()
    const [input, setInput] = useState('')
    const messagesEndRef = useRef(null)
    const inputRef = useRef(null)

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = () => {
        const text = input.trim()
        if (!text || isLoading) return
        sendMessage(text)
        setInput('')
        inputRef.current?.focus()
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="chat-container">
            {/* Header */}
            <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h2>💬 对话 Chat</h2>
                    <p style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span className={`status-dot ${isConnected ? 'online' : 'offline'}`} />
                        {isConnected ? '已连接' : '连接中...'}
                    </p>
                </div>
                <button className="btn btn-ghost" onClick={clearMessages} title="清空消息">
                    <Trash2 size={16} /> 清空
                </button>
            </div>

            {/* Messages */}
            <div className="chat-messages">
                {messages.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
                        <Bot size={48} style={{ margin: '0 auto 16px', opacity: 0.3 }} />
                        <p>发送消息开始对话</p>
                        <p style={{ fontSize: '12px', marginTop: '8px' }}>
                            支持 RPA 自动化 · 浏览器控制 · 文档处理 · 邮件 · 桌面操作
                        </p>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div key={i} className={`chat-message ${msg.role}`}>
                        <div className="chat-avatar">
                            {msg.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
                        </div>
                        <div className="chat-bubble">
                            {msg.type === 'progress' ? (
                                <div className="chat-progress">
                                    {msg.tool_hint ? `🔧 ${msg.content}` : `💭 ${msg.content}`}
                                </div>
                            ) : msg.type === 'error' ? (
                                <div style={{ color: 'var(--color-error)' }}>❌ {msg.content}</div>
                            ) : (
                                <div dangerouslySetInnerHTML={{ __html: simpleMarkdown(msg.content || '') }} />
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="chat-message assistant">
                        <div className="chat-avatar"><Bot size={16} /></div>
                        <div className="chat-bubble">
                            <div className="loading-dots"><span>·</span><span>·</span><span>·</span></div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="chat-input-area">
                <textarea
                    ref={inputRef}
                    className="chat-input"
                    placeholder="输入消息... (Shift+Enter 换行)"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={1}
                />
                <button
                    className="chat-send-btn"
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    )
}

// Simple markdown to HTML (code blocks, bold, inline code)
function simpleMarkdown(text) {
    if (!text) return ''
    return text
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br/>')
}
