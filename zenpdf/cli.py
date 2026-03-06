"""CLI interface for zenpdf"""

import sys
import os
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from zenpdf import __version__
from zenpdf.config import Config
from zenpdf.loader import DocumentLoader
from zenpdf.splitter import TextSplitter
from zenpdf.vectorstore import VectorStore
from zenpdf.llm import OllamaLLMWrapper
from zenpdf.rag import RAGChain
from zenpdf.history import ChatHistory

console = Console()


def get_components(config: Config):
    """Initialize all components"""
    vectorstore = VectorStore(
        db_path=config.get("db_path"),
        embed_model=config.get("embed_model"),
    )

    llm = OllamaLLMWrapper(
        model=config.get("model"),
        temperature=config.get("temperature"),
        stream=config.get("stream"),
    )

    chat_history = ChatHistory(
        max_size=config.get("history_size"),
        history_path=config.get("history_path"),
    )

    splitter = TextSplitter(
        chunk_size=config.get("chunk_size"),
        chunk_overlap=config.get("chunk_overlap"),
    )

    rag = RAGChain(
        vectorstore=vectorstore,
        llm=llm,
        chat_history=chat_history,
        k=config.get("k"),
        stream=config.get("stream"),
    )

    return vectorstore, llm, chat_history, splitter, rag


@click.group()
@click.version_option(version=__version__)
def main():
    """zenpdf - Serene local PDF Q&A with RAG"""
    pass


@main.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--chunk-size", "-c", type=int, help="Chunk size for text splitting")
@click.option("--chunk-overlap", "-o", type=int, help="Chunk overlap")
def index(path: str, chunk_size: int, chunk_overlap: int):
    """Index a PDF, DOCX, TXT file or directory"""
    config = Config()

    if chunk_size:
        config.set("chunk_size", chunk_size)
    if chunk_overlap:
        config.set("chunk_overlap", chunk_overlap)

    vectorstore, llm, chat_history, splitter, rag = get_components(config)

    console.print(f"[cyan]Loading documents from: {path}[/cyan]")

    try:
        path_obj = Path(path)
        if path_obj.is_file():
            documents = DocumentLoader.load_file(path)
        else:
            documents = DocumentLoader.load_directory(path)

        if not documents:
            console.print("[red]No documents found![/red]")
            return

        console.print(f"[cyan]Splitting into chunks...[/cyan]")
        chunks = splitter.split_documents(documents)

        console.print(f"[cyan]Indexing {len(chunks)} chunks...[/cyan]")
        ids = vectorstore.add_documents(chunks)

        console.print(
            f"[green]Successfully indexed {len(ids)} chunks from {len(documents)} document(s)![/green]"
        )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("question")
@click.option("-k", "--num-chunks", type=int, help="Number of chunks to retrieve")
def ask(question: str, num_chunks: int):
    """Ask a question to indexed documents"""
    config = Config()
    vectorstore, llm, chat_history, splitter, rag = get_components(config)

    try:
        stats = vectorstore.get_stats()
        if stats["total_chunks"] == 0:
            console.print("[red]No documents indexed. Run 'zenpdf index <file>' first.[/red]")
            sys.exit(1)

        console.print(f"[cyan]Thinking...[/cyan]")

        if config.get("stream"):
            console.print("")
            result = rag.ask(question, k=num_chunks)
            
            seen_files = set()
            unique_sources = []
            for src in result["sources"]:
                source_file = src["metadata"].get("source", "unknown")
                if source_file not in seen_files:
                    seen_files.add(source_file)
                    unique_sources.append(src)
            result["sources"] = unique_sources
            
            answer_parts = []
            for chunk in llm.stream_generate(result["answer"]):
                console.print(chunk, end="")
                answer_parts.append(chunk)

            console.print("\n")

            chat_history.add(question, "".join(answer_parts), result["sources"])

            if result["sources"]:
                console.print("\n[dim]Sources:[/dim]")
                for i, src in enumerate(result["sources"], 1):
                    source_file = src["metadata"].get("source", src["metadata"].get("source_file", "unknown"))
                    console.print(f"  [dim]{i}. {source_file}[/dim]")
        else:
            result = rag.ask(question, k=num_chunks)
            console.print(Panel(result["answer"], title="Answer"))

            chat_history.add(question, result["answer"], result["sources"])

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
def interactive():
    """Interactive Q&A mode"""
    config = Config()
    vectorstore, llm, chat_history, splitter, rag = get_components(config)

    console.print(
        Panel.fit(
            "[bold cyan]Welcome to zenpdf Interactive Mode![/bold cyan]\n"
            "Type 'quit' or 'exit' to leave\n"
            "Type 'clear' to clear chat history\n"
            "Type 'help' for commands"
        )
    )

    while True:
        try:
            question = console.input("\n[bold green]>[/bold green] ")

            if question.lower() in ["quit", "exit"]:
                console.print("[cyan]Goodbye![/cyan]")
                break

            if question.lower() == "clear":
                chat_history.clear()
                console.print("[cyan]Chat history cleared![/cyan]")
                continue

            if question.lower() == "help":
                console.print("""
Commands:
  quit/exit - Leave interactive mode
  clear    - Clear chat history
  status   - Show vector store status
""")
                continue

            if question.lower() == "status":
                stats = vectorstore.get_stats()
                console.print(Panel(str(stats), title="Status"))
                continue

            if not question.strip():
                continue

            stats = vectorstore.get_stats()
            if stats["total_chunks"] == 0:
                console.print("[red]No documents indexed. Run 'zenpdf index <file>' first.[/red]")
                continue

            console.print("")
            result = rag.ask(question)

            seen_files = set()
            unique_sources = []
            for src in result["sources"]:
                source_file = src["metadata"].get("source", "unknown")
                if source_file not in seen_files:
                    seen_files.add(source_file)
                    unique_sources.append(src)
            result["sources"] = unique_sources

            answer_parts = []
            for chunk in llm.stream_generate(result["answer"]):
                console.print(chunk, end="")
                answer_parts.append(chunk)

            console.print("\n")

            chat_history.add(question, "".join(answer_parts), result["sources"])

        except KeyboardInterrupt:
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@main.command()
def refs():
    """Show sources for last answer"""
    config = Config()
    _, _, chat_history, _, _ = get_components(config)

    messages = chat_history.get_history()
    if not messages:
        console.print("[yellow]No chat history found.[/yellow]")
        return

    last_msg = messages[-1]

    if not last_msg.sources:
        console.print("[yellow]No sources for last answer.[/yellow]")
        return

    console.print(f"[cyan]Sources for: {last_msg.question}[/cyan]\n")

    for i, src in enumerate(last_msg.sources, 1):
        source_file = src["metadata"].get("source", src["metadata"].get("source_file", "unknown"))
        content = src["content"][:200] + "..." if len(src["content"]) > 200 else src["content"]

        console.print(f"[bold]{i}. {source_file}[/bold]")
        console.print(f"   [dim]{content}[/dim]\n")


@main.command()
def list():
    """List all indexed documents"""
    config = Config()
    vectorstore, _, _, _, _ = get_components(config)

    docs = vectorstore.list_documents()

    if not docs:
        console.print("[yellow]No documents indexed.[/yellow]")
        return

    table = Table(title="Indexed Documents")
    table.add_column("ID", style="cyan")
    table.add_column("Source File", style="green")

    for doc in docs:
        table.add_row(doc["id"], doc["source_file"])

    console.print(table)


@main.command()
@click.argument("doc_id")
def remove(doc_id: str):
    """Remove a document by ID"""
    config = Config()
    vectorstore, _, _, _, _ = get_components(config)

    if vectorstore.delete_document(doc_id):
        console.print(f"[green]Document {doc_id} removed![/green]")
    else:
        console.print(f"[red]Failed to remove document {doc_id}[/red]")


@main.command()
def clear():
    """Clear all indexed documents"""
    config = Config()
    vectorstore, _, _, _, _ = get_components(config)

    if click.confirm("Are you sure you want to clear all documents?"):
        vectorstore.clear_all()
        console.print("[green]All documents cleared![/green]")


@main.command()
def status():
    """Show vector store status"""
    config = Config()
    vectorstore, _, _, _, _ = get_components(config)

    stats = vectorstore.get_stats()

    table = Table(title="zenpdf Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in stats.items():
        table.add_row(key, str(value))

    console.print(table)


@main.command()
def reset():
    """Reset vector store completely"""
    config = Config()
    vectorstore, _, _, _, _ = get_components(config)

    if click.confirm("Are you sure you want to RESET everything? This cannot be undone!"):
        vectorstore.reset()
        console.print("[green]Vector store reset![/green]")


@main.group(name="config")
def config_cmd():
    """Show current configuration"""
    pass

@config_cmd.command("show")
def config_show():
    """Show all configuration"""
    config = Config()
    table = Table(title="zenpdf Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    for key, val in config.all.items():
        table.add_row(key, str(val))
    console.print(table)


@config_cmd.command("model")
@click.argument("model_name")
def config_model(model_name: str):
    """Set LLM model"""
    config = Config()
    config.set("model", model_name)
    config.save()
    console.print(f"[green]Model set to: {model_name}[/green]")


@config_cmd.command("embed")
@click.argument("embed_model")
def config_embed(embed_model: str):
    """Set embedding model"""
    config = Config()
    config.set("embed_model", embed_model)
    config.save()
    console.print(f"[green]Embedding model set to: {embed_model}[/green]")


@config_cmd.command("chunk-size")
@click.argument("size", type=int)
def config_chunk_size(size: int):
    """Set chunk size"""
    config = Config()
    config.set("chunk_size", size)
    config.save()
    console.print(f"[green]Chunk size set to: {size}[/green]")


@config_cmd.command("overlap")
@click.argument("overlap", type=int)
def config_overlap(overlap: int):
    """Set chunk overlap"""
    config = Config()
    config.set("chunk_overlap", overlap)
    config.save()
    console.print(f"[green]Chunk overlap set to: {overlap}[/green]")


@config_cmd.command("k")
@click.argument("k", type=int)
def config_k(k: int):
    """Set default k (number of retrieved chunks)"""
    config = Config()
    config.set("k", k)
    config.save()
    console.print(f"[green]Default k set to: {k}[/green]")


@config_cmd.command("db-path")
@click.argument("path")
def config_db_path(path: str):
    """Set database path"""
    config = Config()
    config.set("db_path", path)
    config.save()
    console.print(f"[green]Database path set to: {path}[/green]")


@config_cmd.command("history-size")
@click.argument("size", type=int)
def config_history_size(size: int):
    """Set max chat history size"""
    config = Config()
    config.set("history_size", size)
    config.save()
    console.print(f"[green]History size set to: {size}[/green]")


@main.command()
def history():
    """Show chat history"""
    config = Config()
    _, _, chat_history, _, _ = get_components(config)

    messages = chat_history.get_history()

    if not messages:
        console.print("[yellow]No chat history.[/yellow]")
        return

    for i, msg in enumerate(messages, 1):
        console.print(f"\n[bold cyan]Q{i}: {msg.question}[/bold cyan]")
        if msg.answer:
            console.print(f"A: {msg.answer[:100]}...")


@main.command()
@click.argument("filename")
@click.option("--format", "-f", type=click.Choice(["md", "json"]), default="md")
def export(filename: str, format: str):
    """Export chat history to file"""
    config = Config()
    _, _, chat_history, _, _ = get_components(config)

    if format == "md":
        content = chat_history.export_markdown()
    else:
        content = chat_history.export_json()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    console.print(f"[green]History exported to: {filename}[/green]")


if __name__ == "__main__":
    main()
