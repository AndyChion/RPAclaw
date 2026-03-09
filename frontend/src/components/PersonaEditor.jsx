import { useState } from 'react'
import { Save, UserPen } from 'lucide-react'

export default function PersonaEditor() {
    const [identity, setIdentity] = useState('')
    const [rules, setRules] = useState('')
    const [bootstrap, setBootstrap] = useState('')
    const [saving, setSaving] = useState(false)

    // TODO: Load from workspace files
    // identity.md, rules.md, bootstrap.md in ~/.nanobot/workspace/

    const handleSave = async () => {
        setSaving(true)
        // TODO: Save to workspace files via API
        setTimeout(() => setSaving(false), 500)
    }

    return (
        <div>
            <div className="card">
                <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <UserPen size={18} /> Agent 身份 (identity.md)
                </div>
                <textarea className="form-textarea" style={{ minHeight: '120px' }}
                    placeholder="定义 Agent 的身份和性格...&#10;例如: 你是一个友好的 RPA 自动化专家..."
                    value={identity} onChange={e => setIdentity(e.target.value)} />
            </div>

            <div className="card">
                <div className="card-title">📜 规则 (rules.md)</div>
                <textarea className="form-textarea" style={{ minHeight: '120px' }}
                    placeholder="定义 Agent 必须遵守的规则...&#10;例如: 执行 RPA 操作前必须确认用户意图..."
                    value={rules} onChange={e => setRules(e.target.value)} />
            </div>

            <div className="card">
                <div className="card-title">🚀 启动指令 (bootstrap.md)</div>
                <textarea className="form-textarea" style={{ minHeight: '120px' }}
                    placeholder="Agent 启动时执行的指令...&#10;例如: 问候用户并列出可用的 RPA 功能..."
                    value={bootstrap} onChange={e => setBootstrap(e.target.value)} />
            </div>

            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                <Save size={16} /> {saving ? '保存中...' : '保存'}
            </button>
        </div>
    )
}
