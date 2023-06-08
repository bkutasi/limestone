import re

# Find code blocks
def has_open_code_block(text):
    count = text.count("```")
    return count % 2 == 1

# Find inline code
def has_open_inline_code(text):
    count = len(re.findall(r'(?<![`])`(?![`])', text))
    return count % 2 == 1

# Escape special chars inside code blocks
def escape_code_blocks(text):
    pattern = r"```([\s\S]*?)```"
    code_blocks = re.findall(pattern, text)
    for block in code_blocks:
        escaped_block = block.replace("\\", "\\\\").replace("`", "\\`")
        text = text.replace(f"```{block}```", f"```{escaped_block}```")
    return text

# Escape special chars outside code blocks
def escape(text):
    # In all other places characters
    # _ * [ ] ( ) ~ ` > # + - = | { } . !
    # must be escaped with the preceding character '\'.
    text = escape_code_blocks(text)
    text = re.sub(r"_", '\_', text)
    text = re.sub(r"\*{2}(.*?)\*{2}", '@@@\\1@@@', text)
    text = re.sub(r"\n\*\s", '\n\n• ', text)
    text = re.sub(r"\*", '\*', text)
    text = re.sub(r"\@{3}(.*?)\@{3}", '*\\1*', text)
    text = re.sub(r"\!?\[(.*?)\]\((.*?)\)", '@@@\\1@@@^^^\\2^^^', text)
    text = re.sub(r"\[", '\[', text)
    text = re.sub(r"\]", '\]', text)
    text = re.sub(r"\(", '\(', text)
    text = re.sub(r"\)", '\)', text)
    text = re.sub(r"\@{3}(.*?)\@{3}\^{3}(.*?)\^{3}", '[\\1](\\2)', text)
    text = re.sub(r"~", '\~', text)
    text = re.sub(r">", '\>', text)
    text = re.sub(r"#", '\#', text)
    text = re.sub(r"\+", '\+', text)
    text = re.sub(r"\n-\s", '\n\n• ', text)
    text = re.sub(r"\-", '\-', text)
    text = re.sub(r"=", '\=', text)
    text = re.sub(r"\|", '\|', text)
    text = re.sub(r"{", '\{', text)
    text = re.sub(r"}", '\}', text)
    text = re.sub(r"\.", '\.', text)
    text = re.sub(r"!", '\!', text)
    return text