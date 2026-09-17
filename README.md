# AI Coding Assistant

<p align="center">
  <strong>Repository-Aware AI for Understanding, Debugging, Modifying, and Validating Code</strong>
</p>

<p align="center">
  An AI-powered software engineering assistant that combines code intelligence, hybrid retrieval, LLM reasoning, safe patching, sandboxed execution, automated testing, and iterative bug fixing.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square\&logo=fastapi\&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=flat-square\&logo=next.js\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square\&logo=postgresql\&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cache-DC382D?style=flat-square\&logo=redis\&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF4F00?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Sandbox-2496ED?style=flat-square\&logo=docker\&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178C6?style=flat-square\&logo=typescript\&logoColor=white)

</p>

---

## Overview

**AI Coding Assistant** is a repository-aware AI developer tool designed to assist with real-world software engineering workflows.

Unlike a basic code-generation chatbot, the system works with the actual repository context. It can scan and analyze source code, index repository content, retrieve relevant code using multiple search strategies, answer repository-specific questions, generate targeted patches, apply changes safely, execute tests inside an isolated Docker environment, parse failures, and iteratively attempt fixes.

The core engineering loop is:

```text
Understand
    ↓
Retrieve
    ↓
Reason
    ↓
Generate
    ↓
Patch
    ↓
Execute
    ↓
Test
    ↓
Analyze
    ↓
Fix
    ↓
Validate
```

The project is designed around the principle that **AI-generated code should be grounded in repository context and validated through execution whenever possible.**

---

## Key Capabilities

* GitHub repository cloning and management
* Repository scanning and code indexing
* Python AST-based code analysis
* Jupyter notebook parsing
* Exact code search
* BM25 lexical retrieval
* Vector similarity retrieval
* Hybrid retrieval with Reciprocal Rank Fusion
* Cross-encoder reranking
* Repository-aware AI Q&A
* AI coding agent
* Structured patch generation
* Safe patch application
* Git-aware change detection
* Docker-based sandboxed test execution
* Pytest integration
* Automated test failure parsing
* Error localization
* Iterative AI-assisted bug fixing
* Next.js developer interface

---

# Architecture

```text
                              ┌──────────────────────┐
                              │      Next.js UI      │
                              │   React + TypeScript  │
                              └──────────┬───────────┘
                                         │
                                         ▼
                              ┌──────────────────────┐
                              │       FastAPI        │
                              │       Backend        │
                              └──────────┬───────────┘
                                         │
               ┌─────────────────────────┼─────────────────────────┐
               │                         │                         │
               ▼                         ▼                         ▼
      ┌────────────────┐       ┌──────────────────┐      ┌─────────────────┐
      │  Repository    │       │ Code Intelligence│      │   AI Coding     │
      │    Manager     │       │  & Retrieval      │      │     Agent       │
      └───────┬────────┘       └────────┬─────────┘      └────────┬────────┘
              │                         │                         │
              ▼                         ▼                         ▼
      ┌────────────────┐       ┌──────────────────┐      ┌─────────────────┐
      │ Repository     │       │ Exact Search     │      │ Patch Generation│
      │ Scanner        │       │ BM25             │      │                 │
      │ AST Analyzer   │       │ Vector Search    │      │ Patch Tools     │
      │ Notebook Parser│       │ RRF Fusion       │      └────────┬────────┘
      └────────────────┘       │ Cross-Encoder    │               │
                               └────────┬─────────┘               ▼
                                        │                 ┌─────────────────┐
                                        ▼                 │ Safe Patch      │
                                ┌───────────────┐         │ Validation      │
                                │    Qdrant     │         └────────┬────────┘
                                │ Vector Store  │                  │
                                └───────────────┘                  ▼
                                                         ┌─────────────────┐
                                                         │ Docker Sandbox  │
                                                         └────────┬────────┘
                                                                  │
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │ Pytest Runner   │
                                                         └────────┬────────┘
                                                                  │
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │ Error Parser    │
                                                         └────────┬────────┘
                                                                  │
                                                                  ▼
                                                         ┌─────────────────┐
                                                         │ AI Fix Iteration│
                                                         └─────────────────┘
```

---

# End-to-End Workflow

```text
┌─────────────────────┐
│  GitHub Repository  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Repository Manager  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Scanner / Analyzer  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Code Chunking       │
│ AST Analysis        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Indexing            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│        Hybrid Retrieval             │
│                                     │
│ Exact + BM25 + Vector + RRF         │
│              ↓                      │
│      Cross-Encoder Reranker         │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────┐
│ Repository Context  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    AI Coding Agent  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Patch Generation  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Patch Validation     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Docker Test Sandbox │
└──────────┬──────────┘
           │
           ▼
      ┌────┴────┐
      │  Tests  │
      └────┬────┘
           │
      ┌────┴─────┐
      │          │
    PASS        FAIL
      │          │
      ▼          ▼
   Result    Error Parser
                 │
                 ▼
          Failure Localization
                 │
                 ▼
            AI Fix Agent
                 │
                 ▼
            New Patch
                 │
                 ▼
            Run Tests
```

---

# Intelligent Code Retrieval

Repository-level coding requires accurate context retrieval.

The project therefore uses a multi-stage retrieval pipeline instead of relying exclusively on semantic vector search.

```text
User Query
    │
    ├───────────────► Exact Search
    │
    ├───────────────► BM25 Search
    │
    └───────────────► Vector Search
                           │
                           ▼
                    RRF Score Fusion
                           │
                           ▼
                  Candidate Code Chunks
                           │
                           ▼
                  Cross-Encoder Reranker
                           │
                           ▼
                    Ranked Context
                           │
                           ▼
                      LLM Agent
```

### Retrieval Components

| Component     | Purpose                                                    |
| ------------- | ---------------------------------------------------------- |
| Exact Search  | Finds direct textual/code matches                          |
| BM25          | Strong lexical retrieval for code terminology              |
| Vector Search | Captures semantic similarity                               |
| RRF           | Combines independent retrieval rankings                    |
| Cross-Encoder | Reranks retrieved candidates using query-context relevance |

This combination allows the assistant to handle queries involving both exact identifiers and natural-language descriptions.

---

# Repository Analysis

The repository analysis layer extracts useful information before the AI agent performs reasoning.

For Python projects, AST analysis can identify:

* Functions
* Classes
* Imports
* Definitions
* Source locations
* Structural relationships

Jupyter notebooks are also processed so that notebook-based machine-learning repositories can be indexed alongside traditional source files.

Example:

```text
Repository
    │
    ├── Python Files
    │      ↓
    │    AST Parser
    │
    ├── Notebooks
    │      ↓
    │    Notebook Parser
    │
    ├── Documentation
    │
    └── Other Supported Files
           │
           ▼
      Code / Text Chunks
           │
           ▼
         Index
```

---

# Repository Q&A

The assistant supports repository-aware questions.

Example:

```text
How is the model trained in this repository?
```

Instead of answering only from the LLM's pretrained knowledge, the system performs repository retrieval first.

```text
Question
   ↓
Search Repository
   ↓
Retrieve Relevant Chunks
   ↓
Rerank Context
   ↓
Construct Prompt
   ↓
LLM
   ↓
Repository-Aware Answer
```

This approach is useful for understanding unfamiliar codebases, ML pipelines, configuration, utilities, APIs, and implementation details.

---

# AI Coding Agent

The coding agent is responsible for reasoning over repository context and producing targeted modifications.

Typical flow:

```text
Developer Request
       ↓
Repository Context
       ↓
Relevant Code Retrieval
       ↓
Agent Reasoning
       ↓
Proposed Modification
       ↓
Structured Patch
```

The agent can be used for tasks such as:

```text
Fix this failing function.

Add validation to this API.

Explain and modify this implementation.

Resolve the failing test.

Update the implementation based on the error.
```

The system separates **reasoning and patch generation** from the actual file modification process.

---

# Safe Patch Application

Generated changes are not blindly written to arbitrary filesystem locations.

The patch layer performs validation before applying modifications.

```text
Generated Patch
      │
      ▼
Path Validation
      │
      ▼
Repository Boundary Check
      │
      ▼
File Validation
      │
      ▼
Protected Path Check
      │
      ▼
Patch Application
```

The system includes protections for:

* Paths outside the repository
* Path traversal
* Git metadata
* Restricted files
* Test files
* Unsupported modification targets

This design reduces the risk of an AI-generated patch modifying unintended files.

---

# Automated Testing

Testing is an integral part of the coding workflow.

The assistant can execute repository tests through a dedicated Docker-based test runner.

```text
Repository Snapshot
        ↓
Docker Test Runner
        ↓
Pytest
        ↓
stdout / stderr
        ↓
Result Parser
        ↓
PASS / FAIL
```

Example:

```text
============================= test session starts =============================

1 passed

============================== 1 passed in 0.42s ===============================
```

A generated change is therefore evaluated based on executable test results rather than generation alone.

---

# Automated Bug Fixing

The automated fixing workflow connects code generation with test execution.

```text
┌─────────────────┐
│    Run Tests    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse Failure   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Locate Error    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Retrieve Code   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate Fix    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Apply Patch     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Run Tests Again │
└────────┬────────┘
         │
      ┌──┴──┐
      │     │
     PASS  FAIL
      │     │
      ▼     └──────► Next Iteration
    Result
```

The system can extract information such as:

* Error type
* Failing test
* File path
* Line number
* Function name
* Assertion details
* Error message

This information is then used to provide more targeted context to the fixing agent.

---

# Docker Sandbox

AI-generated code is executed inside an isolated Docker environment.

The test runner is designed with resource and network restrictions.

Example configuration:

```text
CPU              : 1 core
Memory           : 512 MB
Process Limit    : Restricted
Network          : Disabled
User             : Non-root
```

The architecture is:

```text
Host Application
       │
       ▼
Docker Test Runner
       │
       ├── Resource Limits
       ├── Network Isolation
       ├── Non-root Execution
       └── Test Execution
```

This provides an additional execution boundary between generated repository code and the host environment.

---

# Git-Aware Workflow

The assistant uses Git state to reason about repository modifications.

Supported workflow includes:

```text
Baseline Repository
       ↓
AI Modification
       ↓
Git Diff
       ↓
Modified File Detection
       ↓
Change Validation
```

This enables the system to distinguish generated changes from the repository baseline.

---

# Technology Stack

## Backend

* Python 3.12+
* FastAPI
* Pydantic
* SQLAlchemy
* Uvicorn

## AI / LLM

* Groq
* LLaMA 3.3 70B
* Sentence Transformers
* Cross-Encoder

## Retrieval

* Exact Search
* BM25
* Vector Similarity Search
* Reciprocal Rank Fusion
* Cross-Encoder Reranking
* Qdrant

## Code Intelligence

* Python AST
* Repository Scanner
* Jupyter Notebook Parser
* Code Chunking

## Data & Infrastructure

* PostgreSQL
* Redis
* Qdrant
* Docker
* Docker Compose
* Pytest

## Frontend

* Next.js
* React
* TypeScript
* CSS

---

# Project Structure

```text
AI-Coding-Assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tools/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   └── tsconfig.json
│
├── infra/
│   └── docker/
│       └── test-runner/
│           ├── Dockerfile
│           └── ...
│
├── data/
│   └── repositories/
│
├── docker-compose.yml
│
└── README.md
```

---

# Requirements

Before running the project locally, install:

* Python 3.12+
* Node.js
* npm
* Git
* Docker Desktop
* GitHub account
* Groq API key

---

# Installation

## 1. Clone the Repository

```powershell
git clone https://github.com/Shashank123-wq-tech/AI-Coding-Assistant.git
cd AI-Coding-Assistant
```

> Replace the repository URL with your actual GitHub repository URL if the repository name differs.

---

# 2. Backend Setup

Navigate to the backend:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

---

# 3. Environment Configuration

Create:

```text
backend/.env
```

Add:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/ai_coding_assistant

REDIS_URL=redis://localhost:6379/0

QDRANT_URL=http://localhost:6333

GROQ_API_KEY=your_groq_api_key

GROQ_MODEL=llama-3.3-70b-versatile
```

Replace:

```text
your_groq_api_key
```

with your actual API key.

**Do not commit `.env` or API keys to GitHub.**

---

# 4. Start Infrastructure

From the project root:

```powershell
docker compose up -d
```

Verify containers:

```powershell
docker ps
```

Expected services:

```text
PostgreSQL    localhost:5433
Redis         localhost:6379
Qdrant        localhost:6333
```

---

# 5. Start the Backend

From the backend directory:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 6. Start the Frontend

Open another terminal.

Navigate to:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start development server:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# Production Build

Build the frontend:

```powershell
npm run build
```

Start the production server:

```powershell
npm start
```

---

# API Endpoints

| Endpoint                                  | Method | Description                    |
| ----------------------------------------- | -----: | ------------------------------ |
| `/search`                                 |   POST | Search repository code         |
| `/scan`                                   |   POST | Scan repository contents       |
| `/index`                                  |   POST | Index repository content       |
| `/retrieve`                               |   POST | Retrieve relevant code         |
| `/qa`                                     |   POST | Ask repository-aware questions |
| `/agent`                                  |   POST | Execute coding-agent workflow  |
| `/agent/patch`                            |   POST | Generate a code patch          |
| `/agent/patch/apply`                      |   POST | Apply a generated patch        |
| `/api/repositories/{repository_id}/tests` |   POST | Execute repository tests       |
| `/api/repositories/{repository_id}/fix`   |   POST | Run automated fixing workflow  |

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# Example: Repository Q&A

A developer can ask:

```text
Where is the machine learning model trained?
```

The system:

```text
1. Receives the query
2. Searches the repository
3. Retrieves relevant code
4. Reranks candidate chunks
5. Builds repository context
6. Sends context to the LLM
7. Returns a repository-aware response
```

---

# Example: Automated Bug Fix

Suppose the repository contains:

```python
def add(a, b):
    return a - b
```

and:

```python
def test_add():
    assert add(2, 3) == 5
```

The workflow becomes:

```text
Pytest
  ↓
AssertionError
  ↓
Error Parser
  ↓
Failure Localization
  ↓
Relevant Code Retrieval
  ↓
AI Fix Generation
  ↓
Patch Validation
  ↓
Patch Application
  ↓
Pytest
  ↓
1 passed
```

The key design principle is that the fix is validated through execution.

---

# Running Tests

Run the backend test suite:

```powershell
pytest
```

Verbose mode:

```powershell
pytest -v
```

Run a specific test:

```powershell
pytest tests/test_repository_diff.py -v
```

---

# Security Model

The project follows a defense-in-depth approach for AI-generated modifications.

### Repository-Level Protection

```text
Repository Root Validation
        +
Path Traversal Protection
        +
Restricted Modification Targets
        +
Git Metadata Protection
        +
File Type Validation
```

### Execution-Level Protection

```text
Docker Isolation
        +
CPU Limits
        +
Memory Limits
        +
Process Limits
        +
Network Isolation
        +
Non-root Execution
```

### Patch-Level Protection

```text
AI Patch
   ↓
Validate Path
   ↓
Validate Repository Boundary
   ↓
Validate Target File
   ↓
Check Restrictions
   ↓
Apply
```

> The sandbox is a security layer, not a guarantee of complete isolation. Production deployments should apply additional container and infrastructure hardening appropriate to their threat model.

---

# Design Principles

## 1. Repository-Aware AI

The assistant should reason about the actual repository rather than generate code in isolation.

## 2. Retrieval Before Reasoning

Relevant repository context is retrieved before the LLM performs repository-level reasoning.

## 3. Small and Targeted Changes

The agent should avoid unnecessary modifications and focus changes on relevant source files.

## 4. Execution-Based Validation

Generated code should be validated through tests whenever possible.

## 5. Defense in Depth

Repository validation, patch validation, sandboxing, resource restrictions, and automated testing provide multiple protection layers.

## 6. Separation of Responsibilities

The system separates:

```text
Repository Management
        ↓
Code Intelligence
        ↓
Retrieval
        ↓
Agent Reasoning
        ↓
Patch Generation
        ↓
Patch Application
        ↓
Execution
        ↓
Validation
```

This makes the system easier to test, extend, and maintain.

---

# Current Implementation Status

### Repository Intelligence

* [x] Repository cloning
* [x] Repository registration
* [x] Repository scanning
* [x] Python AST analysis
* [x] Notebook parsing
* [x] Code chunking
* [x] Repository indexing

### Retrieval

* [x] Exact search
* [x] BM25 retrieval
* [x] Vector retrieval
* [x] Hybrid retrieval
* [x] Reciprocal Rank Fusion
* [x] Cross-encoder reranking

### AI

* [x] Repository Q&A
* [x] AI coding agent
* [x] Patch generation
* [x] Patch application

### Testing & Debugging

* [x] Docker test runner
* [x] Pytest execution
* [x] Test output capture
* [x] Error parsing
* [x] Error localization
* [x] Automated fix workflow
* [x] Git diff validation

### Frontend

* [x] Next.js application
* [x] React interface
* [x] TypeScript integration

---

# Roadmap

## Repository Intelligence

* [ ] Multi-language AST support
* [ ] JavaScript / TypeScript analysis
* [ ] C++ analysis
* [ ] Dependency graph generation
* [ ] Symbol-level indexing
* [ ] Improved cross-file reasoning

## AI Agent

* [ ] Streaming agent responses
* [ ] Improved multi-file planning
* [ ] Persistent task history
* [ ] Long-running agent tasks
* [ ] Better planning and verification loops

## GitHub Integration

* [ ] GitHub OAuth
* [ ] Pull Request generation
* [ ] Pull Request review
* [ ] Commit generation
* [ ] Branch management

## Engineering Infrastructure

* [ ] CI/CD integration
* [ ] Cloud deployment
* [ ] Stronger sandbox isolation
* [ ] Observability and tracing
* [ ] Authentication and authorization
* [ ] Production monitoring

---

# Use Cases

### Repository Understanding

```text
Understand unfamiliar codebases
Find implementations
Trace functions
Understand ML pipelines
Locate configuration
```

### Debugging

```text
Run tests
Parse failures
Locate errors
Retrieve relevant source
Generate fixes
Validate fixes
```

### Code Modification

```text
Implement changes
Generate patches
Apply safe modifications
Validate behavior
```

### Repository Q&A

```text
Ask architecture questions
Find functions and classes
Understand dependencies
Locate model training code
Understand implementation details
```

---

# Engineering Philosophy

A traditional LLM coding workflow can look like:

```text
Prompt
  ↓
LLM
  ↓
Generated Code
```

AI Coding Assistant expands this into an engineering loop:

```text
Repository
     ↓
Code Intelligence
     ↓
Retrieval
     ↓
Context
     ↓
LLM Reasoning
     ↓
Patch
     ↓
Safety Validation
     ↓
Sandbox
     ↓
Tests
     ↓
Failure Analysis
     ↓
Fix
     ↓
Validation
```

The objective is not simply to generate code.

The objective is to create a system that can **understand a repository, make targeted changes, execute those changes safely, observe the result, and use the result to improve the next action.**

---

# Example Development Loop

```text
Developer
   │
   │  "Fix the failing test"
   ▼
AI Coding Assistant
   │
   ├── Inspect repository
   ├── Retrieve relevant code
   ├── Analyze failure
   ├── Generate patch
   ├── Validate patch
   ├── Execute tests
   ├── Parse errors
   └── Iterate if required
   │
   ▼
Validated Result
```

---

# Project Goals

The project focuses on building an engineering-oriented AI system around the following principles:

```text
Repository Context
       +
Reliable Retrieval
       +
LLM Reasoning
       +
Controlled Tool Use
       +
Safe Execution
       +
Automated Validation
```

This architecture is intended to move beyond simple code completion toward **repository-level AI-assisted software engineering**.

---

# Future Vision

The long-term direction is an AI engineering workspace capable of supporting the complete development lifecycle:

```text
Understand
    ↓
Plan
    ↓
Search
    ↓
Implement
    ↓
Test
    ↓
Debug
    ↓
Fix
    ↓
Review
    ↓
Validate
    ↓
Deliver
```

The system can progressively evolve from a repository-aware coding assistant into a broader AI engineering platform.

---

# Contributing

Contributions, issues, and suggestions are welcome.

A typical contribution workflow:

```bash
git clone <repository-url>
cd AI-Coding-Assistant

git checkout -b feature/your-feature

# Make changes

pytest

git add .
git commit -m "Add your feature"

git push origin feature/your-feature
```

Then open a Pull Request describing:

* What was changed
* Why the change was required
* How it was tested
* Any known limitations

---

# Development Guidelines

When extending the project:

* Keep business logic inside appropriate services.
* Keep API contracts inside schemas.
* Avoid putting repository logic directly inside route handlers.
* Validate all filesystem paths.
* Avoid executing generated code directly on the host.
* Add tests for new functionality.
* Keep Docker execution isolated.
* Keep secrets outside source control.
* Prefer small, reviewable changes.
* Document architectural changes.

---

# Environment Variables

The following configuration is required for local development:

| Variable       | Purpose                 |
| -------------- | ----------------------- |
| `DATABASE_URL` | PostgreSQL connection   |
| `REDIS_URL`    | Redis connection        |
| `QDRANT_URL`   | Qdrant vector database  |
| `GROQ_API_KEY` | LLM API authentication  |
| `GROQ_MODEL`   | LLM model configuration |

Example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/ai_coding_assistant
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Never commit real credentials.

---

# Troubleshooting

## Docker containers are not running

Check:

```powershell
docker ps
```

Start infrastructure:

```powershell
docker compose up -d
```

---

## Backend is not starting

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then:

```powershell
uvicorn app.main:app --reload
```

---

## Frontend dependencies are missing

Run:

```powershell
cd frontend
npm install
```

Then:

```powershell
npm run dev
```

---

## Frontend production build

Run:

```powershell
npm run build
```

If the build succeeds, start:

```powershell
npm start
```

---

# Project Highlights

```text
┌─────────────────────────────────────────────────────────────┐
│                    AI CODING ASSISTANT                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Repository Understanding                                  │
│  AST-Based Code Intelligence                                │
│  Hybrid Code Retrieval                                     │
│  BM25 + Vector Search                                      │
│  RRF Retrieval Fusion                                      │
│  Cross-Encoder Reranking                                   │
│  Repository-Aware Q&A                                      │
│  LLM Coding Agent                                          │
│  Structured Patch Generation                               │
│  Safe Patch Application                                     │
│  Git-Aware Change Detection                                │
│  Docker Sandboxed Execution                                │
│  Automated Pytest Validation                               │
│  Error Parsing & Localization                              │
│  Iterative AI Bug Fixing                                   │
│  Next.js Developer Interface                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# Why This Project Matters

The central challenge in AI-assisted software engineering is not merely generating syntactically correct code.

A useful coding system must be able to:

```text
Understand the codebase
        ↓
Find the right context
        ↓
Reason about the task
        ↓
Make controlled changes
        ↓
Execute the result
        ↓
Observe failures
        ↓
Correct the implementation
        ↓
Verify the result
```

AI Coding Assistant is built around this complete feedback loop.

---

# Author

**Shashank Dixit**

MS — Data Science & Artificial Intelligence
ABV-IIITM Gwalior

GitHub:
https://github.com/Shashank123-wq-tech

---

# License

This project is currently intended for educational, portfolio, and software-engineering development purposes.

If this project is distributed publicly, add an appropriate open-source license to the repository.

---

<p align="center">
  <strong>AI Coding Assistant</strong>
  <br />
  Understand → Retrieve → Generate → Execute → Validate → Fix
</p>
