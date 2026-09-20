"use client";

import { useState } from "react";

import { analyzeWithAgent } from "../../lib/api";

interface AgentPanelProps {
    repositoryId: number | null;
}

export default function AgentPanel({
    repositoryId,
}: AgentPanelProps) {
    const [request, setRequest] = useState("");
    const [result, setResult] = useState<unknown>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleAnalyze() {
        if (!repositoryId) {
            setError("Select a repository first.");
            return;
        }

        if (!request.trim()) {
            setError("Enter a request.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const response = await analyzeWithAgent(
                repositoryId,
                request.trim(),
                8,
            );

            setResult(response);
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                    "Failed to analyze the repository.",
            );
        } finally {
            setLoading(false);
        }
    }

    function handleKeyDown(
        event: React.KeyboardEvent<HTMLTextAreaElement>,
    ) {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            handleAnalyze();
        }
    }

    return (
        <div className="panel">
            <div className="panel-header">
                <div>
                    <h2 className="panel-title">
                        Coding Agent
                    </h2>
                    <p className="page-subtitle">
                        Analyze the repository with an
                        AI coding agent.
                    </p>
                </div>

                <span className="topbar-status">
                    Agent
                </span>
            </div>

            <div className="panel-content">
                <textarea
                    value={request}
                    onChange={(event) =>
                        setRequest(event.target.value)
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="Ask the agent to analyze the repository..."
                    disabled={!repositoryId || loading}
                    rows={5}
                    style={{
                        width: "100%",
                        resize: "vertical",
                    }}
                />

                <div
                    style={{
                        display: "flex",
                        justifyContent: "flex-end",
                        marginTop: "10px",
                    }}
                >
                    <button
                        className="primary-button"
                        onClick={handleAnalyze}
                        disabled={
                            !repositoryId ||
                            loading ||
                            !request.trim()
                        }
                    >
                        {loading
                            ? "Analyzing..."
                            : "Run Agent"}
                    </button>
                </div>

                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                {loading && (
                    <div className="chat-empty">
                        <strong>
                            Agent is analyzing the
                            repository...
                        </strong>
                    </div>
                )}

                {!loading && result !== null && (
                    <div
                        style={{
                            marginTop: "18px",
                        }}
                    >
                        <div className="chat-response-header">
                            <span className="status-dot" />
                            Agent Result
                        </div>

                        <pre
                            style={{
                                marginTop: "10px",
                                padding: "14px",
                                borderRadius: "8px",
                                background:
                                    "#18181b",
                                color: "#f4f4f5",
                                overflowX: "auto",
                                fontSize: "11px",
                                lineHeight: 1.6,
                            }}
                        >
                            {JSON.stringify(
                                result,
                                null,
                                2,
                            )}
                        </pre>
                    </div>
                )}

                {!loading &&
                    result === null &&
                    !error && (
                        <div className="chat-empty">
                            Describe what you want the
                            coding agent to analyze.
                        </div>
                    )}
            </div>
        </div>
    );
}