"use client";

import { useState } from "react";
import {
    reviewRepository,
    CodeReviewResponse,
} from "../../lib/api";

interface ReviewPanelProps {
    repositoryId: number | null;
}

export default function ReviewPanel({
    repositoryId,
}: ReviewPanelProps) {
    const [result, setResult] = useState<CodeReviewResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleReview() {
        if (!repositoryId) {
            setError("Please select a repository first.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const response = await reviewRepository(repositoryId);
            setResult(response);
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to review repository.",
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="rounded-xl border border-gray-800 bg-gray-950 p-5">
            <div className="mb-4 flex items-center justify-between">
                <div>
                    <h2 className="text-lg font-semibold text-white">
                        Code Review
                    </h2>
                    <p className="text-sm text-gray-400">
                        Analyze the current repository diff for bugs,
                        security, performance, and maintainability issues.
                    </p>
                </div>

                <button
                    type="button"
                    onClick={handleReview}
                    disabled={loading || !repositoryId}
                    className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                    {loading ? "Reviewing..." : "Run Review"}
                </button>
            </div>

            {error && (
                <div className="mb-4 rounded-lg border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
                    {error}
                </div>
            )}

            {result && (
                <div className="space-y-4">
                    <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
                        <div className="mb-2 text-sm font-medium text-gray-300">
                            Summary
                        </div>

                        <p className="text-sm leading-6 text-gray-200">
                            {result.summary}
                        </p>

                        <div className="mt-3 text-xs text-gray-500">
                            Diff size: {result.diff_size}
                        </div>
                    </div>

                    {result.issues.length === 0 ? (
                        <div className="rounded-lg border border-green-800 bg-green-950/30 p-4 text-sm text-green-300">
                            No review issues were detected.
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {result.issues.map((issue, index) => (
                                <div
                                    key={`${issue.file}-${issue.line}-${index}`}
                                    className="rounded-lg border border-gray-800 bg-gray-900 p-4"
                                >
                                    <div className="mb-2 flex flex-wrap items-center gap-2">
                                        <span className="rounded-md bg-red-500/10 px-2 py-1 text-xs font-medium uppercase text-red-300">
                                            {issue.severity}
                                        </span>

                                        <span className="rounded-md bg-blue-500/10 px-2 py-1 text-xs font-medium text-blue-300">
                                            {issue.category}
                                        </span>

                                        <span className="text-xs text-gray-500">
                                            {issue.file}
                                            {issue.line
                                                ? `:${issue.line}`
                                                : ""}
                                        </span>
                                    </div>

                                    <p className="text-sm text-gray-200">
                                        {issue.message}
                                    </p>

                                    {issue.suggestion && (
                                        <div className="mt-3 rounded-md bg-gray-950 p-3">
                                            <div className="mb-1 text-xs font-medium text-gray-400">
                                                Suggestion
                                            </div>

                                            <p className="text-sm text-gray-300">
                                                {issue.suggestion}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </section>
    );
}
