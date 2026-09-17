"use client";

import { useState } from "react";

import {
    askRepository,
} from "../../lib/api";


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
            );

            setAnswer(
                result.answer ||
                "No answer was returned.",
            );

        } catch (err: any) {

            const message =
                err?.response?.data?.detail ||
                "Failed to get an answer from the backend.";

            setError(message);

        } finally {

            setLoading(false);

        }
    }


    return (
        <div>

            <h2>
                Repository Chat
            </h2>


            <textarea
                value={query}
                onChange={(event) =>
                    setQuery(event.target.value)
                }
                placeholder={
                    repositoryId
                        ? "Ask about the code..."
                        : "Select a repository first..."
                }
                disabled={!repositoryId || loading}
                rows={5}
            />


            <button
                onClick={handleAsk}
                disabled={
                    !repositoryId ||
                    loading ||
                    !query.trim()
                }
            >
                {loading ? "Thinking..." : "Send"}
            </button>


            {error && (
                <p>
                    {error}
                </p>
            )}


            {answer && (
                <div>
                    <h3>
                        Answer
                    </h3>

                    <p>
                        {answer}
                    </p>
                </div>
            )}

        </div>
    );
}