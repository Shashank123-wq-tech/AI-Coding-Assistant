"use client";

import { useEffect, useState } from "react";

import ChatPanel from "../components/chat/ChatPanel";
import {
    getRepositories,
    Repository,
} from "../lib/api";


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
                    setSelectedRepositoryId(
                        result[0].id
                    );
                }

            } catch (err: any) {

                setError(
                    err?.response?.data?.detail ||
                    "Failed to load repositories."
                );

            } finally {

                setLoading(false);

            }
        }


        loadRepositories();

    }, []);


    return (

        <main
            style={{
                padding: "40px",
                fontFamily: "Arial",
            }}
        >

            <h1>
                AI Coding Assistant
            </h1>


            <p>
                Repository-aware AI coding assistant.
            </p>


            <section
                style={{
                    marginTop: "30px",
                }}
            >

                <h2>
                    Repository
                </h2>


                {loading && (
                    <p>
                        Loading repositories...
                    </p>
                )}


                {error && (
                    <p>
                        {error}
                    </p>
                )}


                {!loading &&
                    !error &&
                    repositories.length === 0 && (
                        <p>
                            No repositories connected.
                        </p>
                    )}


                {repositories.length > 0 && (

                    <select
                        value={
                            selectedRepositoryId ?? ""
                        }
                        onChange={(event) =>
                            setSelectedRepositoryId(
                                Number(event.target.value)
                            )
                        }
                        style={{
                            padding: "10px",
                            minWidth: "300px",
                        }}
                    >

                        {repositories.map(
                            (repository) => (
                                <option
                                    key={repository.id}
                                    value={repository.id}
                                >
                                    {repository.name}
                                </option>
                            )
                        )}

                    </select>

                )}

            </section>


            <section
                style={{
                    marginTop: "30px",
                    maxWidth: "800px",
                }}
            >

                <ChatPanel
                    repositoryId={
                        selectedRepositoryId
                    }
                />

            </section>

        </main>

    );
}