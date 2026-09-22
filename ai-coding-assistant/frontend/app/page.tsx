"use client";

import { useEffect, useState } from "react";

import ChatPanel from "../components/chat/ChatPanel";
import CodeSearchPanel from "../components/search/CodeSearchPanel";
import AgentPanel from "../components/agent/AgentPanel";
import PatchPanel from "../components/agent/PatchPanel";
import TestPanel from "../components/tests/TestPanel";
import ReviewPanel from "../components/review/ReviewPanel";
import {
    getRepositories,
    Repository,
} from "../lib/api";

const navigation = [
    { icon: "⌂", label: "Overview" },
    { icon: "⌕", label: "Code Search" },
    { icon: "◇", label: "Code" },
    { icon: "◉", label: "AI Chat" },
    { icon: "⚡", label: "Agent" },
    { icon: "✓", label: "Tests" },
    { icon: "◆", label: "Code Review" },
];

export default function Home() {
    const [repositories, setRepositories] = useState<Repository[]>([]);
    const [selectedRepositoryId, setSelectedRepositoryId] =
        useState<number | null>(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function loadRepositories() {
            try {
                const result = await getRepositories();

                setRepositories(result);

                if (result.length > 0) {
                    setSelectedRepositoryId(result[0].id);
                }
            } catch (err: any) {
                setError(
                    err?.response?.data?.detail ||
                    "Failed to load repositories.",
                );
            } finally {
                setLoading(false);
            }
        }

        loadRepositories();
    }, []);

    const selectedRepository = repositories.find(
        (repository) =>
            repository.id === selectedRepositoryId,
    );

    return (
        <div className="app-shell">

            {/* Sidebar */}
            <aside className="sidebar">

                <div className="brand">
                    <div className="brand-mark">
                        AI
                    </div>

                    <div className="brand-text">
                        <span className="brand-title">
                            AI Coding Assistant
                        </span>

                        <span className="brand-subtitle">
                            Developer Workspace
                        </span>
                    </div>
                </div>

                <div className="sidebar-section">

                    <div className="sidebar-label">
                        Workspace
                    </div>

                    <nav className="sidebar-nav">

                        {navigation.map((item, index) => (
                            <button
                                key={item.label}
                                className={
                                    index === 0
                                        ? "sidebar-item active"
                                        : "sidebar-item"
                                }
                            >
                                <span className="sidebar-icon">
                                    {item.icon}
                                </span>

                                <span>
                                    {item.label}
                                </span>
                            </button>
                        ))}

                    </nav>

                </div>

                <div className="sidebar-section">

                    <div className="sidebar-label">
                        Repository
                    </div>

                    <div className="sidebar-nav">

                        <button className="sidebar-item">
                            <span className="sidebar-icon">
                                ●
                            </span>

                            <span>
                                {selectedRepository?.name ||
                                    "No repository"}
                            </span>
                        </button>

                    </div>

                </div>

                <div className="sidebar-bottom">

                    <div className="connection-status">

                        <span className="status-dot" />

                        <div className="connection-text">

                            <span className="connection-title">
                                Backend Connected
                            </span>

                            <span className="connection-subtitle">
                                API · localhost:8000
                            </span>

                        </div>

                    </div>

                </div>

            </aside>


            {/* Main Content */}
            <div className="main-content">

                {/* Topbar */}
                <header className="topbar">

                    <div className="page-heading">

                        <h1 className="page-title">
                            Developer Workspace
                        </h1>

                        <p className="page-subtitle">
                            Analyze, search, modify and review
                            your codebase with AI.
                        </p>

                    </div>

                    <div className="topbar-status">

                        <span className="status-dot" />

                        System operational

                    </div>

                </header>


                {/* Workspace */}
                <main className="workspace">

                    {/* Repository */}
                    <section className="repository-card">

                        <div className="card-header">

                            <div>
                                <h2 className="card-title">
                                    Repository
                                </h2>

                                <p className="card-description">
                                    Select the codebase you want
                                    the assistant to work with.
                                </p>
                            </div>

                            {selectedRepository && (
                                <span className="topbar-status">
                                    {selectedRepository.status}
                                </span>
                            )}

                        </div>


                        {loading && (
                            <p className="loading-message">
                                Loading repositories...
                            </p>
                        )}


                        {error && (
                            <div className="error-message">
                                {error}
                            </div>
                        )}


                        {!loading &&
                            !error &&
                            repositories.length === 0 && (
                                <p className="loading-message">
                                    No repositories connected.
                                </p>
                            )}


                        {repositories.length > 0 && (

                            <select
                                className="repository-select"
                                value={
                                    selectedRepositoryId ?? ""
                                }
                                onChange={(event) =>
                                    setSelectedRepositoryId(
                                        Number(
                                            event.target.value,
                                        ),
                                    )
                                }
                            >

                                {repositories.map(
                                    (repository) => (
                                        <option
                                            key={repository.id}
                                            value={
                                                repository.id
                                            }
                                        >
                                            {repository.name}
                                        </option>
                                    ),
                                )}

                            </select>

                        )}

                    </section>


                    {/* Workspace panels */}
                    <section style={{ marginBottom: "16px" }}>
                        <CodeSearchPanel
                            repositoryId={selectedRepositoryId}
                        />    
                    </section>
                    <section style={{ marginBottom: "16px" }}>
                        <AgentPanel
                             repositoryId={selectedRepositoryId}
                        />
                    </section>
                    <section style={{ marginBottom: "16px" }}>
                        <PatchPanel
                            repositoryId={selectedRepositoryId}
                        />
                    </section>
                    <section style={{ marginBottom: "16px" }}>
                        <TestPanel
                            repositoryId={selectedRepositoryId}
                        />
                    </section>
                    <section style={{ marginBottom: "16px" }}>
                        <ReviewPanel
                            repositoryId={selectedRepositoryId}
                        />
                    </section>
                    <section className="workspace-grid">

                        {/* Main workspace */}
                        <div className="panel">

                            <div className="panel-header">

                                <div>
                                    <h2 className="panel-title">
                                        AI Workspace
                                    </h2>
                                </div>

                                <span className="page-subtitle">
                                    Repository-aware
                                </span>

                            </div>

                            <div className="panel-content">

                                <div className="chat-empty">

                                    <div>
                                        <strong>
                                            AI Coding Workspace
                                        </strong>

                                        <br />

                                        Ask questions about your
                                        repository, understand
                                        architecture, and work
                                        with your codebase.
                                    </div>

                                </div>

                            </div>

                        </div>


                        {/* Chat */}
                        <div className="panel chat-panel">

                            <div className="panel-header">

                                <h2 className="panel-title">
                                    AI Chat
                                </h2>

                                <span className="page-subtitle">
                                    Context aware
                                </span>

                            </div>

                            <ChatPanel
                                repositoryId={
                                    selectedRepositoryId
                                }
                            />

                        </div>

                    </section>

                </main>

            </div>

        </div>
    );
}