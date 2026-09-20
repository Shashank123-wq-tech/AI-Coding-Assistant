"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

import { askRepository } from "../../lib/api";

interface ChatPanelProps {
    repositoryId: number | null;
}

export default function ChatPanel({
    repositoryId,
}: ChatPanelProps) {
    const [query, setQuery] = useState("");
    const [answer, setAnswer] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleAsk() {
        if (!repositoryId) {
            setError("Select a repository first.");
            return;
        }

        if (!query.trim()) {
            setError("Enter a question.");
            return;
        }

        setLoading(true);
        setError("");
        setAnswer("");

        try {
            const result = await askRepository(
                repositoryId,
                query.trim(),
                5,
            );

            setAnswer(
                result.answer ||
                    "No answer was returned.",
            );
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                    "Failed to get an answer from the backend.",
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
            handleAsk();
        }
    }

    return (
        <div className="chat-workspace">
            <div className="chat-input-area">
                <textarea
                    value={query}
                    onChange={(event) =>
                        setQuery(event.target.value)
                    }
                    onKeyDown={handleKeyDown}
                    placeholder={
                        repositoryId
                            ? "Ask anything about this repository..."
                            : "Select a repository first..."
                    }
                    disabled={!repositoryId || loading}
                    rows={4}
                />

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginTop: "8px",
                    }}
                >
                    <span className="page-subtitle">
                        Enter to ask · Shift + Enter for
                        new line
                    </span>

                    <button
                        className="primary-button"
                        onClick={handleAsk}
                        disabled={
                            !repositoryId ||
                            loading ||
                            !query.trim()
                        }
                    >
                        {loading
                            ? "Thinking..."
                            : "Ask AI"}
                    </button>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}

            {loading && (
                <div className="chat-empty">
                    <div>
                        <strong>
                            Analyzing repository...
                        </strong>
                        <br />
                        Retrieving relevant code and
                        generating an answer.
                    </div>
                </div>
            )}

            {!loading && answer && (
                <div className="chat-response">
                    <div className="chat-response-header">
                        <span className="status-dot" />
                        AI Response
                    </div>

                    <div className="markdown-content">
                        <ReactMarkdown>
                            {answer}
                        </ReactMarkdown>
                    </div>
                </div>
            )}

            {!loading &&
                !answer &&
                !error && (
                    <div className="chat-empty">
                        <div>
                            <strong>
                                Ask about your codebase
                            </strong>
                            <br />
                            Understand functions,
                            architecture, dependencies,
                            implementation details, and
                            more.
                        </div>
                    </div>
                )}
        </div>
    );
}