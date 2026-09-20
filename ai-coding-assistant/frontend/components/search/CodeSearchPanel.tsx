"use client";

import { useState } from "react";

import {
    searchRepository,
    SearchResult,
} from "../../lib/api";

interface CodeSearchPanelProps {
    repositoryId: number | null;
}

export default function CodeSearchPanel({
    repositoryId,
}: CodeSearchPanelProps) {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSearch() {
        if (!repositoryId) {
            setError("Select a repository first.");
            return;
        }

        if (!query.trim()) {
            setError("Enter a search query.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const response = await searchRepository(
                repositoryId,
                query.trim(),
                10,
            );

            setResults(response.results);
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                "Failed to search repository.",
            );
            setResults([]);
        } finally {
            setLoading(false);
        }
    }

    function handleKeyDown(
        event: React.KeyboardEvent<HTMLInputElement>,
    ) {
        if (event.key === "Enter") {
            handleSearch();
        }
    }

    return (
        <div className="panel">

            <div className="panel-header">

                <div>
                    <h2 className="panel-title">
                        Code Search
                    </h2>

                    <p className="page-subtitle">
                        Search across the indexed repository.
                    </p>
                </div>

                {results.length > 0 && (
                    <span className="topbar-status">
                        {results.length} results
                    </span>
                )}

            </div>


            <div className="panel-content">

                <div
                    style={{
                        display: "flex",
                        gap: "8px",
                    }}
                >

                    <input
                        value={query}
                        onChange={(event) =>
                            setQuery(event.target.value)
                        }
                        onKeyDown={handleKeyDown}
                        placeholder="Search functions, classes, imports..."
                        disabled={
                            !repositoryId ||
                            loading
                        }
                        style={{
                            flex: 1,
                            height: "42px",
                            padding: "0 12px",
                            border: "1px solid #d4d4d8",
                            borderRadius: "7px",
                            fontSize: "12px",
                            outline: "none",
                        }}
                    />

                    <button
                        className="primary-button"
                        onClick={handleSearch}
                        disabled={
                            !repositoryId ||
                            loading ||
                            !query.trim()
                        }
                    >
                        {loading
                            ? "Searching..."
                            : "Search"}
                    </button>

                </div>


                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}


                {!loading &&
                    results.length === 0 &&
                    !error && (
                        <div className="chat-empty">
                            Search the repository to find
                            relevant code.
                        </div>
                    )}


                {results.length > 0 && (

                    <div
                        style={{
                            marginTop: "18px",
                            display: "flex",
                            flexDirection: "column",
                            gap: "12px",
                        }}
                    >

                        {results.map(
                            (result, index) => {

                                const filePath =
                                    String(
                                        result.file_path ||
                                        "Unknown file",
                                    );

                                const content =
                                    String(
                                        result.content ||
                                        "",
                                    );

                                const language =
                                    String(
                                        result.language ||
                                        "text",
                                    );

                                const score =
                                    result.score;

                                return (
                                    <div
                                        key={
                                            String(
                                                result.chunk_id ||
                                                index,
                                            )
                                        }
                                        style={{
                                            border: "1px solid #e4e4e7",
                                            borderRadius: "8px",
                                            overflow: "hidden",
                                        }}
                                    >

                                        <div
                                            style={{
                                                display: "flex",
                                                alignItems:
                                                    "center",
                                                justifyContent:
                                                    "space-between",
                                                padding:
                                                    "10px 12px",
                                                background:
                                                    "#fafafa",
                                                borderBottom:
                                                    "1px solid #e4e4e7",
                                            }}
                                        >

                                            <span
                                                style={{
                                                    fontFamily:
                                                        "monospace",
                                                    fontSize:
                                                        "11px",
                                                    fontWeight:
                                                        600,
                                                }}
                                            >
                                                {filePath}
                                            </span>

                                            <span
                                                style={{
                                                    fontSize:
                                                        "10px",
                                                    color:
                                                        "#71717a",
                                                }}
                                            >
                                                {language}
                                                {score !==
                                                    undefined &&
                                                    ` · score ${score}`}
                                            </span>

                                        </div>


                                        <pre
                                            style={{
                                                margin: 0,
                                                padding:
                                                    "14px",
                                                overflowX:
                                                    "auto",
                                                background:
                                                    "#18181b",
                                                color:
                                                    "#f4f4f5",
                                                fontFamily:
                                                    "Consolas, monospace",
                                                fontSize:
                                                    "11px",
                                                lineHeight:
                                                    1.6,
                                            }}
                                        >
                                            <code>
                                                {content}
                                            </code>
                                        </pre>

                                    </div>
                                );
                            },
                        )}

                    </div>

                )}

            </div>

        </div>
    );
}