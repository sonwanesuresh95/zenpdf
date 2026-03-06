# zenpdf

<p align="center">
  <img src="https://img.shields.io/pypi/v/zenpdf" alt="PyPI Version">
  <img src="https://img.shields.io/pypi/pyversions/zenpdf" alt="Python Versions">
  <img src="https://img.shields.io/pypi/l/zenpdf" alt="License">
  <a href="https://pypi.org/project/zenpdf/">
    <img src="https://img.shields.io/pypi/dm/zenpdf" alt="PyPI Downloads">
  </a>
</p>


A peaceful CLI tool for chatting with your documents using local AI models. All processing happens on your machine - no cloud APIs, no data leaves your device.

## Features

- 🔒 **Local-First** - No cloud APIs, all processing on your machine
- 📄 **Multi-Format** - PDF, DOCX, and TXT support
- ⚡ **Streaming** - Real-time AI responses as they're generated
- 💾 **Persistent History** - Chat history saved between sessions
- 📚 **Source Attribution** - Know which documents informed each answer
- 🎨 **Beautiful CLI** - Rich terminal interface with colors and tables
- ⚙️ **Fully Configurable** - Customize models, chunk sizes, and more

## Installation

```bash
pip install zenpdf
```

## Quick Start

```bash
# 1. Make sure Ollama is running
ollama

# 2. Pull required models (if not already done)
ollama pull llama3.2:1b
ollama pull nomic-embed-text

# 3. Index a document
zenpdf index ./my-document.pdf

# 4. Ask questions!
zenpdf ask "What is this document about?"

# 5. Interactive mode
zenpdf interactive
```

## Commands

### Document Operations

| Command | Description |
|---------|-------------|
| `zenpdf index <path>` | Index PDF/DOCX/TXT file or directory |
| `zenpdf list` | List indexed documents |
| `zenpdf remove <id>` | Remove document by ID |
| `zenpdf clear` | Clear all documents |

### Query Operations

| Command | Description |
|---------|-------------|
| `zenpdf ask "question?"` | Ask a question |
| `zenpdf ask "??" -k 6` | Custom k chunks |
| `zenpdf interactive` | Interactive Q&A mode |

### Reference & History

| Command | Description |
|---------|-------------|
| `zenpdf refs` | Show sources for last answer |
| `zenpdf history` | Show chat history |
| `zenpdf export <file>` | Export history (MD/JSON) |

### Configuration

| Command | Description |
|---------|-------------|
| `zenpdf config show` | Show all config |
| `zenpdf config model <name>` | Set LLM model |
| `zenpdf config embed <name>` | Set embedding model |
| `zenpdf config chunk-size <n>` | Set chunk size |
| `zenpdf config overlap <n>` | Set chunk overlap |
| `zenpdf config k <n>` | Set default retrieved chunks |
| `zenpdf config db-path <path>` | Set database path |
| `zenpdf config history-size <n>` | Set max history size |

### Utilities

| Command | Description |
|---------|-------------|
| `zenpdf status` | Show database status |
| `zenpdf reset` | Reset vector store |
| `zenpdf --version` | Show version |
| `zenpdf --help` | Show help |

## Configuration

Default settings (view with `zenpdf config show`):

| Setting | Default | Description |
|---------|---------|-------------|
| `model` | llama3.2:1b | Ollama LLM model |
| `embed_model` | nomic-embed-text | Embedding model |
| `chunk_size` | 1000 | Text chunk size |
| `chunk_overlap` | 100 | Chunk overlap |
| `k` | 4 | Retrieved chunks |
| `db_path` | ./zenpdf_db | Vector database path |
| `history_size` | 50 | Max chat history |
| `temperature` | 0.7 | LLM temperature |

Configuration is saved to `.zenpdf_config.json` in your working directory.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running
- Ollama models:
  - `llama3.2:1b` (or your preferred model)
  - `nomic-embed-text` (for embeddings)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Document   │────▶│   Splitter   │────▶│   ChromaDB  │
│   Loader    │     │   (Chunks)   │     │   (Vectors) │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                      ┌──────────────┐           │
                      │   Ollama     │◀──────────┘
                      │  (Embeddings)│
                      └──────┬───────┘
                             │
                      ┌──────▼───────┐
                      │  RAG Chain   │
                      └──────┬───────┘
                             │
                      ┌──────▼───────┐
                      │      LLM     │
                      │   (Ollama)   │
                      └──────────────┘
```

## Tech Stack

- [LangChain](https://langchain.dev/) - LLM orchestration
- [Chroma](https://www.trychroma.com/) - Vector database
- [Ollama](https://ollama.ai/) - Local LLMs
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please open an issue or submit a PR.

---

Made with ❤️ for local AI
