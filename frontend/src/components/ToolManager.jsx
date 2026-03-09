import { useState, useEffect } from 'react'
import { Wrench, Server, BookOpen } from 'lucide-react'

export default function ToolManager({ page }) {
    if (page === 'skills') return <SkillsManager />
    return <ToolsAndMCP />
}

function ToolsAndMCP() {
    const [tools, setTools] = useState([])
    const [mcp, setMcp] = useState({})

    useEffect(() => {
        fetch('/api/tools').then(r => r.json()).then(d => setTools(d.tools || [])).catch(console.error)
        fetch('/api/mcp').then(r => r.json()).then(d => setMcp(d.mcp_servers || {})).catch(console.error)
    }, [])

    return (
        <div>
            <h3 style={{ fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Wrench size={18} /> 已注册工具 ({tools.length})
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '12px', marginBottom: '32px' }}>
                {tools.map(tool => (
                    <div className="card" key={tool.name}>
                        <div className="card-title">{tool.name}</div>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '12.5px', lineHeight: '1.5' }}>{tool.description}</p>
                    </div>
                ))}
            </div>

            <h3 style={{ fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Server size={18} /> MCP 服务器
            </h3>
            {Object.keys(mcp).length === 0 ? (
                <p style={{ color: 'var(--text-muted)' }}>暂无配置的 MCP 服务器</p>
            ) : (
                Object.entries(mcp).map(([name, cfg]) => (
                    <div className="card" key={name}>
                        <div className="card-title">{name}</div>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '12.5px' }}>
                            Type: {cfg.type || 'stdio'} | Command: {cfg.command || cfg.url || '—'}
                        </p>
                    </div>
                ))
            )}
        </div>
    )
}

function SkillsManager() {
    const [skills, setSkills] = useState([])
    const [selected, setSelected] = useState(null)
    const [content, setContent] = useState('')

    useEffect(() => {
        fetch('/api/skills').then(r => r.json()).then(d => setSkills(d.skills || [])).catch(console.error)
    }, [])

    const viewSkill = async (name) => {
        const res = await fetch(`/api/skills/${name}`)
        const data = await res.json()
        setSelected(name)
        setContent(data.content || '')
    }

    return (
        <div>
            <h3 style={{ fontSize: '16px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={18} /> Skills ({skills.length})
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px' }}>
                <div>
                    {skills.map(skill => (
                        <div className="card" key={skill.name} onClick={() => viewSkill(skill.name)}
                            style={{ cursor: 'pointer', borderColor: selected === skill.name ? 'var(--color-primary)' : undefined }}>
                            <div className="card-title">{skill.name}</div>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{skill.description}</p>
                        </div>
                    ))}
                </div>
                <div>
                    {selected ? (
                        <pre style={{
                            background: 'var(--bg-surface)', padding: '16px', borderRadius: 'var(--radius-md)',
                            fontSize: '12.5px', fontFamily: 'var(--font-mono)', whiteSpace: 'pre-wrap', overflow: 'auto',
                            maxHeight: '60vh', border: '1px solid var(--bg-glass-border)'
                        }}>
                            {content}
                        </pre>
                    ) : (
                        <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px 0' }}>选择一个 Skill 查看内容</p>
                    )}
                </div>
            </div>
        </div>
    )
}
