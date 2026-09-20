"use client";

import { useState } from "react";

import {
    applyPatch,
    generatePatch,
    PatchResponse,
    ApplyPatchResponse,
} from "../../lib/api";

interface PatchPanelProps {
    repositoryId: number | null;
}

export default function PatchPanel({
    repositoryId,
}: PatchPanelProps) {
    const [request, setRequest] = useState("");
    const [filePath, setFilePath] = useState("");
    const [result, setResult] =
        useState<PatchResponse | null>(null);
    const [applyResult, setApplyResult] =
        useState<ApplyPatchResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [applying, setApplying] = useState(false);
    const [error, setError] = useState("");

    async function handleGeneratePatch() {
        if (!repositoryId) {
            setError("Select a repository first.");
            return;
        }

        if (!request.trim()) {
            setError("Enter a change request.");
            return;
        }

        if (!filePath.trim()) {
            setError("Enter the target file path.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);
        setApplyResult(null);

        try {
            const response = await generatePatch(
                repositoryId,
                request.trim(),
                filePath.trim(),
                5,
            );

            setResult(response);
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                    "Failed to generate patch.",
            );
        } finally {
            setLoading(false);
        }
    }

    async function handleApplyPatch() {
    if (!repositoryId || !result?.changed) {
        return;
    }

    setApplying(true);
    setError("");
    setApplyResult(null);

    try {
        const fileResponse = await fetch(
            `http://127.0.0.1:8000/api/repositories/${repositoryId}/file?file_path=${encodeURIComponent(
                result.file_path,
            )}`,
        );

        if (!fileResponse.ok) {
            throw new Error(
                "Failed to read the current file.",
            );
        }

        const fileData = await fileResponse.json();

        // Check whether this patch was already applied.
        if (fileData.content === result.new_content) {
            setApplyResult({
                file_path: result.file_path,
                applied: false,
                patch:"",
                message: "Patch already applied.",
            });

            return;
        }

        const response = await applyPatch(
            repositoryId,
            result.file_path,
            fileData.content,
            result.new_content,
        );

        setApplyResult(response);
    } catch (err: any) {
        setError(
            err?.response?.data?.detail ||
                err?.message ||
                "Failed to apply patch.",
        );
    } finally {
        setApplying(false);
    }
}
    return (
        <div className="panel">
            <div className="panel-header">
                <div>
                    <h2 className="panel-title">
                        Generate Patch
                    </h2>

                    <p className="page-subtitle">
                        Ask the coding agent to modify a
                        specific source file.
                    </p>
                </div>

                <span className="topbar-status">
                    Patch
                </span>
            </div>

            <div className="panel-content">
                <input
                    value={filePath}
                    onChange={(event) =>
                        setFilePath(event.target.value)
                    }
                    placeholder="Target file, e.g. src/calculator/operations.py"
                    disabled={!repositoryId || loading}
                    style={{
                        width: "100%",
                        height: "42px",
                        padding: "0 12px",
                        border: "1px solid #d4d4d8",
                        borderRadius: "7px",
                        fontSize: "12px",
                        marginBottom: "10px",
                    }}
                />

                <textarea
                    value={request}
                    onChange={(event) =>
                        setRequest(event.target.value)
                    }
                    placeholder="Describe the code change you want..."
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
                        onClick={handleGeneratePatch}
                        disabled={
                            !repositoryId ||
                            loading ||
                            !request.trim() ||
                            !filePath.trim()
                        }
                    >
                        {loading
                            ? "Generating..."
                            : "Generate Patch"}
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
                            Generating a minimal code change...
                        </strong>
                    </div>
                )}

                {!loading && result && (
                    <div
                        style={{
                            marginTop: "18px",
                        }}
                    >
                        <div className="chat-response-header">
                            <span className="status-dot" />
                            Generated Patch
                        </div>

                        <div
                            style={{
                                marginTop: "10px",
                                padding: "10px 12px",
                                border: "1px solid #e4e4e7",
                                borderRadius: "7px",
                                fontSize: "11px",
                                fontFamily:
                                    "Consolas, monospace",
                            }}
                        >
                            {result.file_path}
                        </div>

                        <pre
                            style={{
                                marginTop: "10px",
                                padding: "14px",
                                borderRadius: "8px",
                                background: "#18181b",
                                color: "#f4f4f5",
                                overflowX: "auto",
                                fontSize: "11px",
                                lineHeight: 1.6,
                            }}
                        >
                            <code>
                                {result.patch ||
                                    "No changes generated."}
                            </code>
                        </pre>

                        <div
                            style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent:
                                    "space-between",
                                marginTop: "10px",
                            }}
                        >
                            <span
                                style={{
                                    fontSize: "12px",
                                }}
                            >
                                {result.changed
                                    ? "A code change was generated."
                                    : result.message}
                            </span>

                            {result.changed && (
                                <button
                                    className="primary-button"
                                    onClick={
                                        handleApplyPatch
                                    }
                                    disabled={applying}
                                >
                                    {applying
                                        ? "Applying..."
                                        : "Apply Patch"}
                                </button>
                            )}
                        </div>

                        {applyResult && (
                            <div
                                style={{
                                    marginTop: "12px",
                                }}
                            >
                                <div className="chat-response-header">
                                    <span className="status-dot" />
                                    {applyResult.applied
                                        ? "Patch Applied"
                                        : "Patch Not Applied"}
                                </div>

                                <p
                                    className="page-subtitle"
                                    style={{
                                        marginTop: "8px",
                                    }}
                                >
                                    {applyResult.message}
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {!loading &&
                    !result &&
                    !error && (
                        <div className="chat-empty">
                            Specify a source file and describe
                            the change you want the agent to
                            make.
                        </div>
                    )}
            </div>
        </div>
    );
}