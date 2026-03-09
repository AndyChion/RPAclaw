import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'
import ConfigEditor from './components/ConfigEditor'
import ToolManager from './components/ToolManager'
import CronManager from './components/CronManager'
import PersonaEditor from './components/PersonaEditor'
import RPAWorkflow from './components/RPAWorkflow'

const PAGES = {
    chat: { component: Chat, title: '对话 Chat', desc: '与 Agent 流式对话' },
    llm: { component: ConfigEditor, title: 'LLM 配置', desc: '管理大模型 Provider 和 API Key' },
    channels: { component: ConfigEditor, title: '渠道管理', desc: '配置 Telegram / 微信 / 钉钉等消息渠道' },
    agent: { component: ConfigEditor, title: 'Agent 设置', desc: '模型参数、Temperature、工具迭代次数等' },
    tools: { component: ToolManager, title: '工具管理', desc: '查看已注册工具和 MCP 服务器' },
    skills: { component: ToolManager, title: 'Skills 管理', desc: '查看和管理 Agent 技能' },
    cron: { component: CronManager, title: '定时任务', desc: '管理 Cron 和 Heartbeat 心跳' },
    persona: { component: PersonaEditor, title: '性格编辑', desc: '编辑 Agent 身份、规则、启动指令' },
    rpa: { component: RPAWorkflow, title: 'RPA 工作流', desc: '搭建 RPA 自动化流程并转为 Skill' },
}

export default function App() {
    const [activePage, setActivePage] = useState('chat')

    const pageConfig = PAGES[activePage] || PAGES.chat
    const PageComponent = pageConfig.component

    return (
        <div className="app-layout">
            <Sidebar activePage={activePage} onNavigate={setActivePage} />
            <main className="main-content">
                {activePage === 'chat' ? (
                    <PageComponent />
                ) : (
                    <>
                        <div className="page-header">
                            <h2>{pageConfig.title}</h2>
                            <p>{pageConfig.desc}</p>
                        </div>
                        <div className="page-body">
                            <PageComponent page={activePage} />
                        </div>
                    </>
                )}
            </main>
        </div>
    )
}
