"use client";

import { useState } from "react";

import {
    runRepositoryTests,
    fixRepositoryErrors,
    TestResultResponse,
    FixErrorsResponse,
} from "../../lib/api";

interface TestPanelProps {
    repositoryId: number | null;
}

export default function TestPanel({
    repositoryId,
}: TestPanelProps) {
    const [result, setResult] =
        useState<TestResultResponse | null>(null);
    
    const [fixResult, setFixResult] =
        useState<FixErrorsResponse | null>(null);
    
    const [fixing, setFixing] =
        useState(false);    

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    async function handleRunTests() {
        if (!repositoryId) {
            setError("Please select a repository first.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const response =
                await runRepositoryTests(repositoryId);

            setResult(response);
        } catch (err: any) {
            setError(
                err?.response?.data?.detail ||
                    err?.message ||
                    "Failed to run tests.",
            );
        } finally {
            setLoading(false);
        }
    }
    async function handleFixErrors() {
    if (!repositoryId) {
        setError("Please select a repository first.");
        return;
    }

    setFixing(true);
    setError("");
    setFixResult(null);

    try {
        const request =
            result?.error?.message ||
            "Fix the failing tests and make the repository tests pass.";

        

        const response =
            await fixRepositoryErrors(
                repositoryId,
                request,
            );

        setFixResult(response);

        // Refresh the test result after the fix process.
        if (response.final_test) {
            setResult(response.final_test);
        }
    } catch (err: any) {
        setError(
            err?.response?.data?.detail ||
                err?.message ||
                "Failed to fix repository errors.",
        );
    } finally {
        setFixing(false);
    }
}

    return (
        <section className="rounded-xl border border-gray-800 bg-gray-950 p-5">
            <div className="mb-4">
                <h2 className="text-lg font-semibold text-white">
                    Tests
                </h2>

                <p className="mt-1 text-sm text-gray-400">
                    Run the repository test suite inside the sandbox.
                </p>
            </div>

            <button
                type="button"
                onClick={handleRunTests}
                disabled={!repositoryId || loading}
                className="rounded-lg bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {loading ? "Running Tests..." : "Run Tests"}
            </button>
            {result?.status === "failed" && (
                <button
                 type="button"
                 onClick={handleFixErrors}
                disabled={fixing}
                className="ml-3 rounded-lg bg-yellow-500 px-4 py-2 text-sm font-medium text-black transition hover:bg-yellow-400 disabled:cursor-not-allowed disabled:opacity-50"
                >
               {fixing ? "Fixing Errors..." : "Fix Errors"}
            </button>
)}

            {error && (
                <div className="mt-4 rounded-lg border border-red-800 bg-red-950/40 p-4">
                    <p className="text-sm font-medium text-red-400">
                        Test Execution Error
                    </p>

                    <p className="mt-1 whitespace-pre-wrap text-sm text-red-300">
                        {error}
                    </p>
                </div>
            )}

            {result && (
                <div className="mt-5 space-y-4">
                    <div
                        className={`rounded-lg border p-4 ${
                            result.status === "passed"
                                ? "border-green-800 bg-green-950/30"
                                : "border-red-800 bg-red-950/30"
                        }`}
                    >
                        <div className="flex items-center justify-between">
                            <div>
                                <p
                                    className={`text-sm font-semibold ${
                                        result.status === "passed"
                                            ? "text-green-400"
                                            : "text-red-400"
                                    }`}
                                >
                                    {result.status === "passed"
                                        ? "✓ Tests Passed"
                                        : "✗ Tests Failed"}
                                </p>

                                <p className="mt-1 text-sm text-gray-300">
                                    Return code: {result.returncode}
                                </p>
                            </div>

                            <span className="rounded-md bg-gray-900 px-3 py-1 text-xs text-gray-400">
                                {result.status}
                            </span>
                        </div>
                    </div>

                    {result.stdout && (
                        <div>
                            <p className="mb-2 text-sm font-medium text-gray-300">
                                Test Output
                            </p>

                            <pre className="max-h-64 overflow-auto rounded-lg border border-gray-800 bg-black p-4 text-xs leading-5 text-gray-300">
                                {result.stdout}
                            </pre>
                        </div>
                    )}

                    {result.stderr && (
                        <div>
                            <p className="mb-2 text-sm font-medium text-red-400">
                                Error Output
                            </p>

                            <pre className="max-h-64 overflow-auto rounded-lg border border-red-900 bg-black p-4 text-xs leading-5 text-red-300">
                                {result.stderr}
                            </pre>
                        </div>
                    )}

                    {result.error?.has_error && (
                        <div className="rounded-lg border border-yellow-800 bg-yellow-950/20 p-4">
                            <p className="text-sm font-semibold text-yellow-400">
                                Error Details
                            </p>

                            {result.error.error_type && (
                                <p className="mt-2 text-sm text-gray-300">
                                    <span className="font-medium">
                                        Type:
                                    </span>{" "}
                                    {result.error.error_type}
                                </p>
                            )}

                            {result.error.message && (
                                <p className="mt-1 text-sm text-gray-300">
                                    <span className="font-medium">
                                        Message:
                                    </span>{" "}
                                    {result.error.message}
                                </p>
                            )}

                            {result.error.file && (
                                <p className="mt-1 text-sm text-gray-300">
                                    <span className="font-medium">
                                        File:
                                    </span>{" "}
                                    {result.error.file}
                                </p>
                            )}

                            {result.error.line !== null && (
                                <p className="mt-1 text-sm text-gray-300">
                                    <span className="font-medium">
                                        Line:
                                    </span>{" "}
                                    {result.error.line}
                                </p>
                            )}
                        </div>
                    )}
                </div>
            )}
        </section>
    );
}