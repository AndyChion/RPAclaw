import {
    MessageSquare, Settings, Radio, Bot, Wrench, BookOpen,
    Clock, UserPen, Workflow
} from 'lucide-react'

const NAV = [
    {
        section: 'MAIN', items: [
            { id: 'chat', label: '对话 Chat', icon: MessageSquare },
        ]
    },
    {
        section: 'CONFIGURATION', items: [
            { id: 'llm', label: 'LLM 配置', icon: Settings },
            { id: 'channels', label: '渠道管理', icon: Radio },
            { id: 'agent', label: 'Agent 设置', icon: Bot },
        ]
    },
    {
        section: 'MANAGEMENT', items: [
            { id: 'tools', label: '工具 & MCP', icon: Wrench },
            { id: 'skills', label: 'Skills', icon: BookOpen },
            { id: 'cron', label: '定时任务', icon: Clock },
            { id: 'persona', label: '性格编辑', icon: UserPen },
        ]
    },
    {
        section: 'AUTOMATION', items: [
            { id: 'rpa', label: 'RPA 工作流', icon: Workflow },
        ]
    },
]

export default function Sidebar({ activePage, onNavigate }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <h1>🤖 RPAclaw</h1>
                <span className="version">v0.1</span>
            </div>
            <nav className="sidebar-nav">
                {NAV.map(section => (
                    <div className="nav-section" key={section.section}>
                        <div className="nav-section-title">{section.section}</div>
                        {section.items.map(item => {
                            const Icon = item.icon
                            return (
                                <button
                                    key={item.id}
                                    className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                                    onClick={() => onNavigate(item.id)}
                                >
                                    <Icon />
                                    <span>{item.label}</span>
                                </button>
                            )
                        })}
                    </div>
                ))}
            </nav>
        </aside>
    )
}
