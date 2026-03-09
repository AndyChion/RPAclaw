import { useState, useEffect } from 'react'
import { Clock, Save } from 'lucide-react'

export default function CronManager() {
    const [heartbeat, setHeartbeat] = useState({ enabled: true, intervalS: 1800 })
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        fetch('/api/cron').then(r => r.json())
            .then(d => setHeartbeat(d.heartbeat || {}))
            .catch(console.error)
    }, [])

    const handleSave = async () => {
        setSaving(true)
        try {
            await fetch('/api/cron/heartbeat', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(heartbeat),
            })
        } catch (e) { console.error(e) }
        setSaving(false)
    }

    return (
        <div>
            <div className="card">
                <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Clock size={18} /> Heartbeat 心跳
                </div>
                <div className="form-group">
                    <label className="form-label">启用</label>
                    <label className="toggle">
                        <input type="checkbox" checked={heartbeat.enabled || false}
                            onChange={e => setHeartbeat({ ...heartbeat, enabled: e.target.checked })} />
                        <span className="slider" />
                    </label>
                </div>
                <div className="form-group">
                    <label className="form-label">间隔（秒）</label>
                    <input className="form-input" type="number" min={60} step={60}
                        value={heartbeat.intervalS || 1800}
                        onChange={e => setHeartbeat({ ...heartbeat, intervalS: parseInt(e.target.value) })} />
                    <p style={{ color: 'var(--text-muted)', fontSize: '11px', marginTop: '4px' }}>
                        = {Math.round((heartbeat.intervalS || 1800) / 60)} 分钟
                    </p>
                </div>
            </div>
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                <Save size={16} /> {saving ? '保存中...' : '保存'}
            </button>
        </div>
    )
}
