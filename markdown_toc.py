"""Create a table of contents for a markdown file."""

from __future__ import annotations

import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal

import emoji


class Section:
    """Class to represent a section in the markdown file."""

    def __init__(self, title: str, level: int):
        """Initialize a Section object."""
        self.title = title
        self.level = level


class TableOfContents:
    """Class to create a table of contents for a markdown file."""

    def __init__(
        self, input_file: str, encoding: Literal["utf-8", "cp932"] = "utf-8"
    ):
        """Initialize a TableOfContents object."""
        self.input_filepath = Path(input_file)
        self.sections: list[Section] = []
        self.lines: list[str] = []
        self.i_toc_begin = None
        self.i_toc_end = None
        self.encoding = encoding
        self.toc_lines = []

    def read_contents(self):
        """Read the contents of the input file."""
        if not self.input_filepath.exists():
            raise FileNotFoundError(f"{self.input_filepath} does not exist.")
        self.lines = self.input_filepath.read_text(
            encoding=self.encoding
        ).splitlines()

    def detect_toc_block_position(self):
        """Detect the position of the TOC block in the markdown file."""
        b_search = re.compile(r"^\s*<!-- toc -->")
        e_search = re.compile(r"^\s*<!-- /toc -->")
        for i_line, line in enumerate(self.lines):
            if b_search.match(line):
                self.i_toc_begin = i_line
            if e_search.match(line):
                self.i_toc_end = i_line
        h2_search = re.compile(r"^##")
        i_first_h2 = None
        if self.i_toc_begin is None or self.i_toc_end is None:
            for i_line, line in enumerate(self.lines):
                if h2_search.match(line):
                    i_first_h2 = i_line
                    break
            if i_first_h2:
                self.lines.insert(i_first_h2, "")
                self.lines.insert(i_first_h2, "<!-- /toc -->")
                self.lines.insert(i_first_h2, "<!-- toc -->")
                self.i_toc_begin = i_first_h2
                self.i_toc_end = i_first_h2 + 1

    def parse_structure(self):
        """Parse the markdown structure to identify sections."""
        reg = re.compile(r"^\s*(#+)\s(.*)")
        for line in self.lines:
            if res := reg.match(line):
                level = len(res.group(1))
                title = res.group(2)
                section = Section(title=title, level=level)
                self.sections.append(section)
        for section in self.sections:
            if section.level == 1:
                continue
            link = (
                emoji.replace_emoji(section.title, "")
                .strip()
                .lower()
                .replace(" ", "-")
            )
            self.toc_lines.append(
                f"{' ' * (2 * (section.level - 2))}"
                + f"- [{section.title}](#{link})"
            )

    def output_new_line(self):
        """Output the new markdown file with the TOC."""
        if self.i_toc_begin is None:
            raise RuntimeError("TOC block position is not detected.")
        new_lines = (
            self.lines[0 : self.i_toc_begin + 1]
            + [""]
            + self.toc_lines
            + [""]
            + self.lines[self.i_toc_end :]
        )
        self.input_filepath.write_text(
            "\n".join(new_lines), encoding=self.encoding
        )


def main():
    """Main function to create a table of contents."""
    parser = ArgumentParser(
        prog="mardown-toc",
        description="Create a table of contents for a markdown file.",
    )
    parser.add_argument(
        "input_file", help="The name or path of the Markdown file."
    )
    parser.add_argument(
        "--encoding",
        "-e",
        choices=["utf-8", "cp932"],
        default="utf-8",
        help="File encoding (default: utf-8).",
    )
    args = parser.parse_args()
    input_file: str = args.input_file
    toc = TableOfContents(input_file)
    toc.read_contents()
    toc.detect_toc_block_position()
    toc.parse_structure()
    toc.output_new_line()
    return


if __name__ == "__main__":
    main()
