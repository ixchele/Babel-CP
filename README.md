# Project Babel-CP (or Babel-Arena)

> **A fully immersive, terminal-based competitive programming arena.**  
> Built for the CLI ecosystem. No browsers. No distractions. Just code.

---

## About The  Project

Traditional competitive programming platforms (like LeetCode or DOMjudge) rely on web browsers, breaking the natural workflow of terminal-native developers. 

**Project Babel** brings the hackathon directly into the terminal. Designed specifically for the 1337/42 coding ecosystem, it allows students to compete in a Terminal User Interface (TUI). 

The name **Babel** reflects both the unification of multiple programming languages (C, C++, Python, etc.) inside a single execution engine, and the visual concept of climbing a tower via the real-time leaderboard.

---

## System Architecture

Babel is built on a strict **3-tier microservices architecture** to ensure complete decoupling, security, and zero impact on local campus machines.

### 1. The Client (`babel-cli`)
* **Role:** The local frontend running on the competitor's machine.
* **Tech Stack:** Python + Textual.
* **Concept:** A "dumb" asynchronous client. It handles the UI, reads the local source files, and sends HTTP REST requests. It contains no evaluation logic and does not require `root` access.

### 2. The Core Server (`babel-api`)
* **Role:** The orchestrator and state manager, hosted on an external Server.
* **Tech Stack:** Python (FastAPI) + SQLite.
* **Concept:** Handles token-based authentication, serves the problem sets, routes code to the execution sandbox, and broadcasts real-time leaderboard updates. It **never** executes untrusted code itself.

### 3. The Execution Engine (`babel-judge`)
* **Role:** An isolated, secure Linux sandbox.
* **Tech Stack:** **Judge0 CE** running in Docker.
* **Concept:** Compiles and runs the code, injects hidden test cases (stdin), and strictly monitors resource limits (CPU time, Memory allocation). It returns exact metrics and verdicts (`Accepted`, `TLE`, `Segfault`).

---

## The Submission Lifecycle

1. **Code:** The competitor solves the algorithmic problem locally using their preferred editor or the internal one.
2. **Submit:** Inside the Babel TUI, they select their source file (e.g., `solution.cpp`) and hit submit.
3. **Transport:** The TUI fires an encrypted `POST` request with the payload to the Babel API.
4. **Delegation:** The API matches the problem ID, fetches the expected `in/out` test cases, and forwards the job to the Judge0 Docker container.
5. **Execution:** Judge0 spins up a secure jail, compiles the code, and evaluates the output.
6. **Verdict:** The API receives the result, updates the SQLite database, and pushes the new leaderboard state. The competitor's terminal instantly flashes with their verdict.

---

## Security & Authentication

To ensure a frictionless and secure experience during a live hackathon:
* **Token-Based Auth:** We bypass complex password management. Organizers generate unique 6-character access tokens (e.g., `X8B-93N`) mapped to student IDs. Competitors simply enter their token in the TUI to access the arena.
* **Zero Pollution:** The entire backend infrastructure (API + Judge0 + DB) is containerized via Docker. Post-event, a simple `docker compose down -v` wipes the server completely clean.

---
# cp-interface
