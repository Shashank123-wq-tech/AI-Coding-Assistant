# AI Coding Assistant

> An AI-powered development assistant that understands software repositories, searches code intelligently, generates safe code changes, runs tests in an isolated environment, analyzes failures, and iteratively fixes bugs.

## Overview

**AI Coding Assistant** is a production-oriented AI developer tool designed to help engineers understand, debug, modify, and validate existing codebases.

Instead of treating a repository as plain text, the system combines **repository analysis, AST-based code intelligence, lexical search, BM25 retrieval, vector search, hybrid retrieval, reranking, LLM-based reasoning, automated patch generation, and sandboxed test execution** into a single workflow.

The goal is to provide an end-to-end coding workflow:

```text
Repository
    ↓
Clone / Scan
    ↓
Code & AST Analysis
    ↓
Indexing
    ↓
Hybrid Code Retrieval
    ↓
AI Agent
    ↓
Patch Generation
    ↓
Sandboxed Test Execution
    ↓
Error Analysis
    ↓
Automatic Fix
    ↓
Validated Result
