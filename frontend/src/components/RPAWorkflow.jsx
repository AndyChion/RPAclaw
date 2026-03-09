import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Workflow, Sparkles } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'

export default function RPAWorkflow() {
    const { messages, isConnected, isLoading, sendMessage, clearMessages } = useWebSocket()
    const [input, setInput] = useState('')
    const [workflowName, setWorkflowName] = useState('')
    const [saving, setSaving] = useState(false)
    const messagesEndRef = useRef(null)

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = () => {
        const text = input.trim()
        if (!text || isLoading) return
        sendMessage(text, 'webui:rpa')
        setInput('')
    }

    const handleSaveAsSkill = async () => {
        if (!workflowName.trim()) return
        setSaving(true)
        try {
            await fetch('/api/rpa/workflows', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: workflowName,
                    messages: messages.map(m => ({ role: m.role, content: m.content, type: m.type })),
                }),
            })
            // Convert to skill
            await fetch(`/api/rpa/workflows/${encodeURIComponent(workflowName)}/to-skill`, { method: 'POST' })
            alert(`✅ RPA 工作流 "${workflowName}" 已保存为 Skill`)
        } catch (e) {
            alert('保存失败: ' + e.message)
        }
        setSaving(false)
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 100px)' }}>
            {/* Workflow header */}
            <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <Workflow size={20} style={{ color: 'var(--color-primary)' }} />
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                    通过对话搭建 RPA 工作流。完成后可保存为 Skill，以便后续复用。
                </span>
            </div>

            {/* Chat area */}
            <div style={{ flex: 1, overflow: 'auto', padding: '0 0 12px 0', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {messages.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
                        <Sparkles size={40} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                        <p>描述你想要自动化的任务</p>
                        <p style={{ fontSize: '12px', marginTop: '4px' }}>例如: "帮我每天自动打开 xxx.com，登录并下载报表"</p>
                    </div>
                )}
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-message ${msg.role}`}>
                        <div className="chat-avatar">
                            {msg.role === 'assistant' ? <Bot size={16} /> : <User size={16} />}
                        </div>
                        <div className="chat-bubble">
                            {msg.type === 'progress' ? (
                                <div className="chat-progress">{msg.tool_hint ? `🔧 ${msg.content}` : `💭 ${msg.content}`}</div>
                            ) : (
                                <div dangerouslySetInnerHTML={{ __html: simpleMarkdown(msg.content || '') }} />
                            )}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Save as skill */}
            {messages.length > 2 && (
                <div className="card" style={{ display: 'flex', gap: '10px', alignItems: 'center', padding: '12px 16px' }}>
                    <input className="form-input" style={{ flex: 1 }} placeholder="工作流名称 (e.g. daily-report-download)"
                        value={workflowName} onChange={e => setWorkflowName(e.target.value)} />
                    <button className="btn btn-success" onClick={handleSaveAsSkill} disabled={saving || !workflowName.trim()}>
                        <Sparkles size={16} /> {saving ? '保存中...' : '保存为 Skill'}
                    </button>
                </div>
            )}

            {/* Input */}
            <div style={{ display: 'flex', gap: '10px', paddingTop: '8px' }}>
                <textarea className="chat-input" placeholder="描述 RPA 任务..." value={input}
                    onChange={e => setInput(e.target.value)} rows={1}
                    onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }} />
                <button className="chat-send-btn" onClick={handleSend} disabled={!input.trim() || isLoading}>
                    <Send size={18} />
                </button>
            </div>
        </div>
    )
}

function simpleMarkdown(text) {
    if (!text) return ''
    return text
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br/>')
}
