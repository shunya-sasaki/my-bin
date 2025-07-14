"""Sync snippets between VS Code and Neovim."""

import json
import platform
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict


class SnippetDict(TypedDict):
    """Type for a snippet dictionary."""

    prefix: str
    scope: str
    description: str
    body: list[str]


class NvimSnippet(TypedDict):
    """Type for a Neovim snippet."""

    language: str
    path: str


@dataclass
class _SnippetFile:
    name: str
    exists_in_vscode: bool
    exists_in_nvim: bool


class SnippetsSync:
    """Class to sync snippets between VS Code and Neovim."""

    def __init__(self):
        """Initialize the SnippetsSync class."""
        self.vscode_dirpath, self.nvim_dirpath = self._detect_config_dirpathes()
        self.snippets_files = self.list_snippets_files()

    def _detect_config_dirpathes(self) -> tuple[Path, Path]:
        """Detect the configuration directories for VS Code and Neovim."""
        home_dirpath = Path.home()
        system = platform.system()
        match system:
            case "Windows":
                vscode_dirpath = home_dirpath / "AppData" / "Roaming" / "Code" / "User"
                nvim_dirpath = home_dirpath / "AppData" / "Local" / "nvim"
            case "Darwin":
                vscode_dirpath = (
                    home_dirpath / "Library" / "Application Support" / "Code" / "User"
                )
                nvim_dirpath = home_dirpath / ".config" / "nvim"
            case "Linux":
                vscode_dirpath = home_dirpath / ".config" / "Code" / "User"
                nvim_dirpath = home_dirpath / ".config" / "nvim"
            case _:
                raise RuntimeError(f"Unsupported platform: {system}")
        return vscode_dirpath, nvim_dirpath

    def list_snippets_files(self) -> list[_SnippetFile]:
        """List all snippet files in VS Code and Neovim directories."""
        nvim_snippets_dirpath = self.nvim_dirpath / "snippets"
        vscode_snippets_dirpath = self.vscode_dirpath / "snippets"
        nvim_snippets_filepaths = list(nvim_snippets_dirpath.glob("*.code-snippets"))
        vscode_snippets_filepaths = list(
            vscode_snippets_dirpath.glob("*.code-snippets")
        )
        nvim_filenames = [f.name for f in nvim_snippets_filepaths]
        vscode_filenames = [f.name for f in vscode_snippets_filepaths]
        snippets_filenames = set(nvim_filenames + vscode_filenames)
        snippets_files: list[_SnippetFile] = []
        for filename in snippets_filenames:
            exists_in_vscode = filename in vscode_filenames
            exists_in_nvim = filename in nvim_filenames
            snippets_file = _SnippetFile(
                name=filename,
                exists_in_vscode=exists_in_vscode,
                exists_in_nvim=exists_in_nvim,
            )
            snippets_files.append(snippets_file)
        return snippets_files

    def vscode_to_nvim(self, force_copy: bool = False):
        """Copy snippets files that are not in nvim"""
        for snippets_file in self.snippets_files:
            if force_copy or (
                snippets_file.exists_in_vscode and not snippets_file.exists_in_nvim
            ):
                try:
                    with open(
                        self.vscode_dirpath / "snippets" / snippets_file.name,
                        "r",
                        encoding="utf-8",
                    ) as fin:
                        lines = fin.readlines()
                except UnicodeDecodeError:
                    with open(
                        self.vscode_dirpath / "snippets" / snippets_file.name,
                        "r",
                        encoding="cp932",
                    ) as fin:
                        lines = fin.readlines()
                valid_lines: list[str] = []
                for line in lines:
                    is_invalid = re.match(r"^\s+//[\s]+", line)
                    if not is_invalid:
                        valid_lines.append(line)
                with open(
                    self.nvim_dirpath / "snippets" / snippets_file.name,
                    "w",
                    encoding="utf-8",
                ) as fout:
                    fout.writelines("".join(valid_lines))

    def nvim_to_vscode(self):
        """Copy snippets files that are not in vscode"""
        for snippets_file in self.snippets_files:
            if snippets_file.exists_in_nvim and not snippets_file.exists_in_vscode:
                nvim_snippets_path = self.nvim_dirpath / "snippets" / snippets_file.name
                vscode_snippets_path = (
                    self.vscode_dirpath / "snippets" / snippets_file.name
                )
                shutil.copy2(nvim_snippets_path, vscode_snippets_path)

    def create_package_json(self):
        """Create package.json for Neovim snippets."""
        snippets_filepaths = (self.nvim_dirpath / "snippets").glob("*.code-snippets")
        snippets = []
        for snippets_filepath in snippets_filepaths:
            scopes: list[str] = []
            try:
                with open(snippets_filepath, "r", encoding="utf-8") as fin:
                    snippets_json: dict[str, SnippetDict] = json.load(fin)
            except json.decoder.JSONDecodeError:
                print(f"[ERROR] {snippets_filepath.name}")
                print(f"[ERROR] {snippets_filepath.as_posix()}")
                raise
            except UnicodeDecodeError:
                print(f"[ERROR] {snippets_filepath.name}")
                raise
            for snippet in snippets_json.values():
                snippet_scopes = snippet.get("scope", "").split(",")
                scopes += snippet_scopes
            language = ",".join(set(scopes)).replace(" ", "")
            path = f"./{snippets_filepath.name}"
            print(f"{path}")
            print(f"  {language}")
            snippet = {"language": language, "path": path}
            snippets.append(snippet)
        dict_package = {"name": "nvim-snippets", "contributes": {"snippets": snippets}}
        with open(
            self.nvim_dirpath / "snippets" / "package.json", "w", encoding="utf-8"
        ) as fout:
            json.dump(dict_package, fout, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    syncer = SnippetsSync()
    syncer.nvim_to_vscode()
    syncer.vscode_to_nvim(force_copy=True)
    syncer.create_package_json()
