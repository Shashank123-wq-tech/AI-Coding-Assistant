"use client";

import Editor from "@monaco-editor/react";


interface CodeEditorProps {

    value: string;

    language?: string;
}


export default function CodeEditor({

    value,

    language = "python",

}: CodeEditorProps) {

    return (

        <Editor

            height="600px"

            defaultLanguage={language}

            value={value}

            theme="vs-dark"

        />

    );
}
