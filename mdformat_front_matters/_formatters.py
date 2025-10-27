"""Front matter formatters using python-frontmatter."""

from __future__ import annotations

import frontmatter  # type: ignore[import-untyped]


class YAMLFormatter:
    """YAML formatter using python-frontmatter."""

    @staticmethod
    def format(content: str) -> str:
        """Format YAML content.

        Args:
            content: Raw YAML string to format.

        Returns:
            Formatted YAML string.

        """
        try:
            # Parse the YAML content
            metadata, _ = frontmatter.parse(f"---\n{content}\n---\n")

            # If content is empty, return empty string
            if not metadata:
                return ""

            # Create a post with the metadata
            post = frontmatter.Post("", **metadata)

            # Dump back to YAML (without the content part)
            formatted = frontmatter.dumps(post, handler=frontmatter.YAMLHandler())

            # Remove the document delimiters
            formatted = formatted.removeprefix("---\n")

            # Remove trailing dashes and newlines
            if formatted.endswith("\n---\n"):
                formatted = formatted[:-5]
            elif formatted.endswith("\n---"):
                formatted = formatted[:-4]

            formatted = formatted.rstrip("\n")

            # Handle empty result
            if not formatted.strip():
                return ""

            return formatted  # noqa: TRY300

        except Exception:
            # If formatting fails, return original content
            return content


class TOMLFormatter:
    """TOML formatter using python-frontmatter."""

    @staticmethod
    def format(content: str) -> str:
        """Format TOML content.

        Args:
            content: Raw TOML string to format.

        Returns:
            Formatted TOML string.

        """
        try:
            # Parse the TOML content
            metadata, _ = frontmatter.parse(
                f"+++\n{content}\n+++\n",
                handler=frontmatter.TOMLHandler(),
            )

            # Create a post with the metadata
            post = frontmatter.Post("", **metadata)

            # Dump back to TOML
            formatted = frontmatter.dumps(post, handler=frontmatter.TOMLHandler())

            # Remove the +++ delimiters
            formatted = formatted.removeprefix("+++\n")
            if formatted.endswith("\n+++\n"):
                formatted = formatted[:-5]
            elif formatted.endswith("\n+++"):
                formatted = formatted[:-4]

            return formatted.rstrip("\n")

        except Exception:
            # If formatting fails, return original content
            return content


class JSONFormatter:
    """JSON formatter using python-frontmatter."""

    @staticmethod
    def format(content: str) -> str:
        """Format JSON content.

        Args:
            content: Raw JSON string to format.

        Returns:
            Formatted JSON string.

        """
        try:
            # Parse the JSON content
            metadata, _ = frontmatter.parse(
                f"{content}\n",
                handler=frontmatter.JSONHandler(),
            )

            # Create a post with the metadata
            post = frontmatter.Post("", **metadata)

            # Dump back to JSON
            formatted = frontmatter.dumps(post, handler=frontmatter.JSONHandler())

            # Remove the outer braces and extract just the metadata
            # python-frontmatter wraps JSON, we need just the inner content
            if formatted.startswith("{\n") and formatted.endswith("\n}\n"):
                # Extract lines between first and last brace
                lines = formatted.split("\n")
                if len(lines) > 2:  # noqa: PLR2004
                    # Remove first/last lines (braces + newline)
                    inner = "\n".join(lines[1:-2])
                    if inner.strip():
                        return f"{{\n{inner}\n}}"

            # Fallback: return formatted as-is without trailing newline
            return formatted.rstrip("\n")

        except Exception:
            # If formatting fails, return original content
            return content
