import json

from backend.app.ai.services.db_evidence import get_stop_evidence


def run_tool(tool_name: str, arguments: dict) -> dict:
    """
    Controlled tool dispatcher.

    Only explicitly registered read-only tools are allowed.
    """

    allowed_tools = {
        "get_stop_evidence": get_stop_evidence,
    }

    if tool_name not in allowed_tools:
        return {
            "success": False,
            "error": "TOOL_NOT_ALLOWED",
        }

    try:
        result = allowed_tools[tool_name](**arguments)

        return {
            "success": True,
            "tool": tool_name,
            "result": result,
        }

    except Exception as error:
        return {
            "success": False,
            "tool": tool_name,
            "error": str(error),
        }


if __name__ == "__main__":

    print("=== CONTROLLED TOOL TEST ===")

    result = run_tool(
        "get_stop_evidence",
        {"stop_id": "1"},
    )

    print(json.dumps(result, indent=2))
