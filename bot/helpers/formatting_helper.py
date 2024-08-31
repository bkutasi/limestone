import re


class TextFormatter:
    """
    A class used to format text for markdown rendering.

    ...

    Methods
    -------
    has_open_code_block(text: str) -> bool
        Returns True if the text has an open code block, False otherwise.
    has_open_inline_code(text: str) -> bool
        Returns True if the text has an open inline code block, False otherwise.
    escape_code_blocks(text: str) -> str
        Escapes characters in code blocks in the text.
    escape(text: str) -> str
        Escapes characters in the text for markdown rendering.
    """

    @staticmethod
    def has_open_code_block(text: str) -> bool:
        """
        Checks if the text has an open code block.

        Parameters
        ----------
        text : str
            The text to check.

        Returns
        -------
        bool
            True if the text has an open code block, False otherwise.
        """
        count = text.count("```")
        return count % 2 == 1

    @staticmethod
    def has_open_inline_code(text: str) -> bool:
        """
        Checks if the text has an open inline code block.

        Parameters
        ----------
        text : str
            The text to check.

        Returns
        -------
        bool
            True if the text has an open inline code block, False otherwise.
        """
        count = len(re.findall(r"(?<![`])`(?![`])", text))
        return count % 2 == 1

    @staticmethod
    def escape_code_blocks(text: str) -> str:
        """
        Escapes characters in code blocks in the text.

        Parameters
        ----------
        text : str
            The text to escape.

        Returns
        -------
        str
            The escaped text.
        """
        pattern = r"```([\s\S]*?)```"
        code_blocks = re.findall(pattern, text)

        for block in code_blocks:
            escaped_block = block.replace("\\", "\\\\").replace("`", "\\`")
            text = text.replace(f"```{block}```", f"```{escaped_block}```")

        return text

    @staticmethod
    def escape(text: str) -> str:
        """
        Escapes characters in the text for markdown rendering.

        Parameters
        ----------
        text : str
            The text to escape.

        Returns
        -------
        str
            The escaped text.
        """

        # List of characters to escape
        chars_to_escape = r"_*~#+-={}!.|()<>[]"

        # Escape characters in code blocks
        text = TextFormatter.escape_code_blocks(text)

        # Escape the characters using regex
        escaped_text = re.sub(
            r"([{}])".format(re.escape(chars_to_escape)), r"\\\1", text
        )

        return escaped_text
