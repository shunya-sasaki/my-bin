"""Convert a text file to a VSCode snippet file."""

import json
import os
import sys
from pathlib import Path


def create_snippet(
    file_path: str, snippet_name: str
) -> dict[str, dict[str, str | list[str]]]:
    """
    Reads the content of a file and creates a VSCode snippet.

    Args:
        file_path (str): The path to the file to be converted.
        snippet_name (str): The name of the snippet.

    Returns:
        dict: A dictionary representing the VSCode snippet.
    """
    try:
        with open(file_path, "r") as f:
            body: list[str] = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    body = [line.rstrip("\n") for line in body]

    snippet = {
        snippet_name: {
            "prefix": snippet_name,
            "scope": "",
            "description": f"Snippet for {snippet_name}",
            "body": body,
        }
    }
    return snippet


def main():
    """
    Main function to convert a text file to a VSCode snippet.
    """
    if len(sys.argv) != 2:
        print(
            "Usage: python text_to_snippet.py <input_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    input_file = sys.argv[1]
    input_filepath = Path(input_file)
    output_filepath = input_filepath.with_suffix(".code-snippets")

    if not output_filepath.name.endswith(".code-snippets"):
        print(
            "Error: Output file must have a .code-snippets extension.", file=sys.stderr
        )
        sys.exit(1)

    snippet_name = os.path.splitext(os.path.basename(input_file))[0]
    snippet_data = create_snippet(input_file, snippet_name)

    try:
        with open(output_filepath, "w") as f:
            json.dump(snippet_data, f, indent=4)
    except IOError as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Snippet '{snippet_name}' created successfully in '{output_filepath.name}'")


if __name__ == "__main__":
    main()
