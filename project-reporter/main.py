#!/usr/bin/env python3
from pathlib import Path

# CONFIGURATION
CONFIG = {
    "exclude_paths": [
        # tooling and caches
        "node_modules", "dist", ".git", "__pycache__", "prompts", ".idea", ".vscode",
        "logs", "tmp", "project-reporter",
        # project outputs and build artifacts
        "data", "reports", ".venv", ".pytest_cache", ".ruff_cache",
        ".mypy_cache", "htmlcov", ".dist", "build", "egg-info",
    ],
    "exclude_extensions": [
        ".pyc", ".log", ".DS_Store", ".env", ".example", ".json", ".jsonl", ".ndjson"
    ],
    "exclude_files": [
        "package-lock.json", ".env", ".gitignore", "file_contents_report.txt",
    ],
    "output_file": "file_contents_report.txt",
}

def find_project_root(start_path: Path) -> Path:
    """
    Walk up from start_path until a .git directory is found, or return start_path if not found.
    """
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return start_path

def should_exclude(file_path: Path, script_path: Path, project_root: Path) -> bool:
    if file_path.resolve() == script_path:
        return True
    if file_path.suffix in CONFIG["exclude_extensions"]:
        return True
    if file_path.name in CONFIG["exclude_files"]:
        return True
    rel_parts = file_path.relative_to(project_root).parts
    if any(part in CONFIG["exclude_paths"] for part in rel_parts):
        return True
    return False

def write_directory_structure(project_root: Path, out_file, indent_level=0, script_path=None):
    if script_path is None:
        script_path = Path(__file__).resolve()
        out_file.write("FULL DIRECTORY STRUCTURE\n")
        out_file.write("========================\n\n")
    def _write_dir(dir_path: Path, indent_level: int):
        children = []
        try:
            for child in sorted(dir_path.iterdir()):
                if should_exclude(child, script_path, project_root):
                    continue
                children.append(child)
        except Exception:
            return
        if not children:
            return
        if indent_level > 0:
            out_file.write(f"{'    ' * (indent_level-1)}{dir_path.name}/\n")
        for child in children:
            if child.is_dir():
                _write_dir(child, indent_level + 1)
            else:
                out_file.write(f"{'    ' * indent_level}{child.name}\n")
    _write_dir(project_root, 0)
    out_file.write("\n\n")

def main():
    script_path = Path(__file__).resolve()
    cwd = Path.cwd()
    project_root = find_project_root(cwd)
    # Output to the project-reporter directory
    output_path = script_path.parent / CONFIG["output_file"]
    with output_path.open("w", encoding="utf-8") as out_file:
        for file_path in project_root.rglob("*"):
            if not file_path.is_file():
                continue
            if should_exclude(file_path, script_path, project_root):
                continue
            rel_path = file_path.relative_to(project_root)
            header = f"{rel_path}\n{'-' * len(str(rel_path))}\n"
            out_file.write(header)
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            out_file.write(content + "\n\n")
        write_directory_structure(project_root, out_file)
    print(f"Aggregation complete. Output written to: {output_path}")

if __name__ == "__main__":
    main() 