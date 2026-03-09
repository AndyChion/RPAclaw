import { useState, useEffect } from 'react'
import { Save, Eye, EyeOff } from 'lucide-react'

export default function ConfigEditor({ page }) {
    const [data, setData] = useState(null)
    const [saving, setSaving] = useState(false)
    const [showKeys, setShowKeys] = useState({})

    useEffect(() => {
        const endpoints = { llm: '/api/config/providers', channels: '/api/config/channels', agent: '/api/config/agent' }
        const endpoint = endpoints[page] || '/api/config'
        fetch(endpoint).then(r => r.json()).then(setData).catch(console.error)
    }, [page])

    const handleSave = async () => {
        setSaving(true)
        const endpoints = { llm: '/api/config/providers', channels: '/api/config/channels', agent: '/api/config/agent' }
        try {
            await fetch(endpoints[page], { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        } catch (e) { console.error(e) }
        setSaving(false)
    }

    if (!data) return <div style={{ color: 'var(--text-muted)', padding: '40px 0', textAlign: 'center' }}>加载中...</div>

    if (page === 'llm') return <ProvidersEditor data={data} onSave={handleSave} saving={saving} showKeys={showKeys} setShowKeys={setShowKeys} />
    if (page === 'channels') return <ChannelsEditor data={data} setData={setData} onSave={handleSave} saving={saving} />
    if (page === 'agent') return <AgentEditor data={data} setData={setData} onSave={handleSave} saving={saving} />

    return <JsonEditor data={data} setData={setData} onSave={handleSave} saving={saving} />
}

function ProvidersEditor({ data, onSave, saving, showKeys, setShowKeys }) {
    const providers = data.providers || data
    return (
        <div>
            {Object.entries(providers).filter(([, v]) => typeof v === 'object').map(([name, prov]) => (
                <div className="card" key={name}>
                    <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        {name}
                        {prov._hasKey && <span className="badge badge-success">✓ Key</span>}
                    </div>
                    <div className="form-group">
                        <label className="form-label">API Key</label>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <input className="form-input" type={showKeys[name] ? 'text' : 'password'} value={prov.apiKey || ''} readOnly placeholder="Not configured" />
                            <button className="btn btn-ghost" onClick={() => setShowKeys(s => ({ ...s, [name]: !s[name] }))}>
                                {showKeys[name] ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                        </div>
                    </div>
                    {prov.apiBase && (
                        <div className="form-group">
                            <label className="form-label">API Base</label>
                            <input className="form-input" value={prov.apiBase} readOnly />
                        </div>
                    )}
                </div>
            ))}
            <button className="btn btn-primary" onClick={onSave} disabled={saving}>
                <Save size={16} /> {saving ? '保存中...' : '保存配置'}
            </button>
        </div>
    )
}

function ChannelsEditor({ data, setData, onSave, saving }) {
    const channels = ['telegram', 'feishu', 'dingtalk', 'slack', 'discord', 'whatsapp', 'email', 'qq', 'matrix']
    return (
        <div>
            {channels.filter(ch => data[ch]).map(ch => (
                <div className="card" key={ch}>
                    <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>{ch.charAt(0).toUpperCase() + ch.slice(1)}</span>
                        <label className="toggle">
                            <input type="checkbox" checked={data[ch]?.enabled || false}
                                onChange={e => setData({ ...data, [ch]: { ...data[ch], enabled: e.target.checked } })} />
                            <span className="slider" />
                        </label>
                    </div>
                </div>
            ))}
            <button className="btn btn-primary" onClick={onSave} disabled={saving}>
                <Save size={16} /> {saving ? '保存中...' : '保存'}
            </button>
        </div>
    )
}

function AgentEditor({ data, setData, onSave, saving }) {
    const update = (key, val) => setData({ ...data, [key]: val })
    return (
        <div>
            <div className="card">
                <div className="form-group">
                    <label className="form-label">模型 Model</label>
                    <input className="form-input" value={data.model || ''} onChange={e => update('model', e.target.value)} />
                </div>
                <div className="form-group">
                    <label className="form-label">Temperature</label>
                    <input className="form-input" type="number" step="0.1" min="0" max="2" value={data.temperature ?? 0.1} onChange={e => update('temperature', parseFloat(e.target.value))} />
                </div>
                <div className="form-group">
                    <label className="form-label">Max Tokens</label>
                    <input className="form-input" type="number" value={data.maxTokens || 8192} onChange={e => update('maxTokens', parseInt(e.target.value))} />
                </div>
                <div className="form-group">
                    <label className="form-label">Max Tool Iterations</label>
                    <input className="form-input" type="number" value={data.maxToolIterations || 40} onChange={e => update('maxToolIterations', parseInt(e.target.value))} />
                </div>
                <div className="form-group">
                    <label className="form-label">Workspace</label>
                    <input className="form-input" value={data.workspace || ''} onChange={e => update('workspace', e.target.value)} />
                </div>
            </div>
            <button className="btn btn-primary" onClick={onSave} disabled={saving}>
                <Save size={16} /> {saving ? '保存中...' : '保存设置'}
            </button>
        </div>
    )
}

function JsonEditor({ data, setData, onSave, saving }) {
    const [text, setText] = useState(JSON.stringify(data, null, 2))
    return (
        <div>
            <textarea className="form-textarea" style={{ minHeight: '400px' }} value={text}
                onChange={e => { setText(e.target.value); try { setData(JSON.parse(e.target.value)) } catch { } }} />
            <button className="btn btn-primary" onClick={onSave} disabled={saving} style={{ marginTop: '12px' }}>
                <Save size={16} /> {saving ? '保存中...' : '保存'}
            </button>
        </div>
    )
}
