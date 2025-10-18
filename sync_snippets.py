"""Sync snippets between VS Code and Neovim."""

import json
import logging
import platform
import re
import shutil
from argparse import ArgumentParser
from dataclasses import dataclass
from logging import Formatter, Logger, StreamHandler
from pathlib import Path
from typing import TypedDict

parser = ArgumentParser(description="Sync snippets between VS Code and Neovim.")
parser.add_argument("--force-vscode", "-v", action="store_true")

logger = Logger(__name__)
logger.setLevel(logging.DEBUG)
fmt = "[%(asctime)s.%(msecs)03d] %(levelname)-8s" + ": %(message)s"
datefmt = r"%Y-%m-%d %H:%M:%S"
formatter = Formatter(fmt=fmt, datefmt=datefmt)
handler = StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


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
                        match = re.search(r'"scope":\s*"([^"]+)"', line)
                        if match:
                            scopes_str = match.group(1)
                            scopes = [
                                self._convert_scope_from_vscode_to_nvim(scope.strip())
                                for scope in scopes_str.split(",")
                            ]
                            line = re.sub(
                                r'"scope":\s*"[^"]+"',
                                f'"scope": "{",".join(scopes)}"',
                                line,
                            )
                        valid_lines.append(line)
                with open(
                    self.nvim_dirpath / "snippets" / snippets_file.name,
                    "w",
                    encoding="utf-8",
                ) as fout:
                    fout.writelines("".join(valid_lines))
                logger.info(f"Copied {snippets_file.name} from vscode to nvim.")

    def nvim_to_vscode(self):
        """Copy snippets files that are not in vscode"""
        for snippets_file in self.snippets_files:
            if snippets_file.exists_in_nvim and not snippets_file.exists_in_vscode:
                nvim_snippets_path = self.nvim_dirpath / "snippets" / snippets_file.name
                vscode_snippets_path = (
                    self.vscode_dirpath / "snippets" / snippets_file.name
                )
                shutil.copy2(nvim_snippets_path, vscode_snippets_path)
                logger.info(f"Copied {nvim_snippets_path.name} from nvim to vscode.")

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
                logger.error(f"{snippets_filepath.name}")
                logger.error(f"{snippets_filepath.as_posix()}")
                raise
            except UnicodeDecodeError:
                logger.error(f"{snippets_filepath.name}")
                raise
            for snippet in snippets_json.values():
                snippet_scopes = snippet.get("scope", "").split(",")
                snippet_scopes = [
                    self._convert_scope_from_vscode_to_nvim(scope.strip())
                    for scope in snippet_scopes
                ]
                scopes += snippet_scopes
            language = ",".join(set(scopes)).replace(" ", "")
            if language == "":
                language = "all"
            path = f"./{snippets_filepath.name}"
            snippet = {"language": language, "path": path}
            snippets.append(snippet)
        dict_package = {"name": "nvim-snippets", "contributes": {"snippets": snippets}}
        with open(
            self.nvim_dirpath / "snippets" / "package.json", "w", encoding="utf-8"
        ) as fout:
            json.dump(dict_package, fout, indent=2, ensure_ascii=False)

    def _convert_scope_from_vscode_to_nvim(self, scope: str) -> str:
        """Convert VS Code scope to Neovim scope."""
        match scope:
            case "plaintext":
                return "text"
            case "bat":
                return "dosbatch"
            case "powershell":
                return "ps1"
            case "ignore":
                return "gitignore"
            case "shellscript":
                return "sh,zsh"
            case "pip-requirements":
                return "requirements"
            case _:
                return scope

    def _convert_scope_from_nvim_to_vscode(self, scope: str) -> str:
        """Convert Neovim scope to VS Code scope."""
        match scope:
            case "text":
                return "plaintext"
            case "dosbatch":
                return "bat"
            case "ps1":
                return "powershell"
            case "gitignore":
                return "ignore"
            case "sh":
                return "shellscript"
            case "zsh":
                return "shellscript"
            case "bash":
                return "shellscript"
            case "requirements":
                return "pip-requirements"
            case _:
                return scope


if __name__ == "__main__":
    logger.info("Starting snippets sync...")
    args = parser.parse_args()
    if args.force_vscode:
        logger.warning(
            "Force copy from VS Code to Neovim is enabled."
            + " This will overwrite existing files in Neovim."
        )
    syncer = SnippetsSync()
    syncer.nvim_to_vscode()
    syncer.vscode_to_nvim(force_copy=args.force_vscode)
    syncer.create_package_json()
