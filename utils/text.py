from html import escape


def h(value) -> str:
    """Escapes a value for safe use inside HTML-parse-mode Telegram messages.

    Any user-supplied text (names, task titles, descriptions, usernames, etc.)
    MUST be passed through this before being interpolated into a message that
    uses <b>, <i> and similar tags — otherwise stray '<', '>' or '&' characters
    in the user's input make Telegram's HTML parser fail with:
    'Bad Request: can't parse entities'.
    """
    if value is None:
        return "—"
    return escape(str(value))
