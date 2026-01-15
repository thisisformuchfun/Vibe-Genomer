# Vibe-Genomer 

**The "Claude Code" for Genomics.**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status](https://img.shields.io/badge/Status-Pre--Alpha-orange)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

## 🚀 The Mission
We are building the **Autonomous Genomic Agent**.

Bioinformatics is stuck in a loop of manual piping, dependency hell, and fragile bash scripts. **Vibe-Genomer** breaks this loop. It is an agentic CLI—similar to Claude Code or OpenAI Codex—but deeply trained on the syntax of biology.

You don't write the pipeline; you define the *intent*.
> **User:** "Analyze this BAM file for large deletions in the BRCA1 region and cross-reference with ClinVar."
> **Vibe-Genomer:** *Parses file headers -> Generates filtering strategy -> Runs `samtools` & `bcftools` -> queries API -> Returns summarized report.*

## ✨ Core Philosophy
We are moving from **imperative** ("run this awk command") to **declarative** ("find these variants").
* **Agentic Execution:** The tool plans a multi-step workflow, executes it in your shell, and self-corrects if a tool fails.
* **Biologically Aware:** It understands that `chr1` and `1` are the same chromosome, and that a VCF header is not just a comment.
* **Privacy First:** Like the best CLI agents, it runs locally where possible, keeping sensitive patient data off public cloud inference wherever you choose.

## 🛠️ Tech Stack
* **Core Logic:** Python (Bridge between LLM and Shell) / Rust (Performance modules)
* **Agent Framework:** LangGraph / Custom ReAct Loop (The "Brain")
* **Integrations:** `htslib`, `samtools`, `bedtools`, `nextflow`
* **Model Support:** Agnostic (Claude 3.5 Sonnet, GPT-4o, DeepSeek-Coder, Local Llama)

## 🤝 Call for Experts (We Need You)
We are building the foundational "OS" for genomic agents. We need contributors who can bridge the gap between LLM reasoning and biological ground truth.

### 1. Bioinformaticians (The "Ground Truth")
We need experts to build the **verification layer**.
* *Challenge:* LLMs hallucinate. In biology, a hallucinated SNP is a misdiagnosis.
* *Task:* Build the "sanity check" modules that validate the agent's output against biological constraints (e.g., "Is this coordinate actually inside the gene?").

### 2. LLM / Agent Engineers (The "Brain")
We need experts in **tool use** and **context management**.
* *Challenge:* Genomic files are massive (100GB+ BAMs). You can't put them in the context window.
* *Task:* Build the RAG system that lets the agent "read" a binary genomic file without loading the whole thing.

### 3. Systems Engineers (The "Plumbing")
We need experts in **sandboxing**.
* *Challenge:* An agent running shell commands is dangerous.
* *Task:* distinct execution environments (Docker/Singularity containers) that prevent the agent from accidentally `rm -rf /` your cluster.

## ⚡ Quick Start (Pre-Alpha)

1.  **Install:**
    ```bash
    pip install vibe-genomer
    ```
2.  **Authenticate (Bring your own API key):**
    ```bash
    vibe auth --provider anthropic
    ```
3.  **Vibe:**
    ```bash
    # The magic happens here
    vibe "Take the fastq files in /data, align them to hg38, and give me a QC report."
    ```

## 🗺️ Roadmap
- [ ] **Phase 1:** CLI Agent that translates Natural Language to `samtools`/`bedtools` one-liners.
- [ ] **Phase 2:** "Planner" module for multi-step workflows (e.g., Alignment -> Sorting -> Calling).
- [ ] **Phase 3:** Interactive REPL (Read-Eval-Print Loop) for iterative data exploration.
- [ ] **Phase 4:** Local Model Support (Ollama integration) for fully offline analysis.

## 📜 License
Distributed under the Apache 2.0 License. See `LICENSE` for more information.

## 👥 Team
**Location:** Las Vegas, NV
**Organization:** Meatbag Labs

**Core Contributors:**
- Stephen Shaffer ([@thisisformuchfun](https://github.com/thisisformuchfun))

---
*Built with Claude Code and passion for open genomics.*
