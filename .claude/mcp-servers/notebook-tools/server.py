"""
Notebook Tools MCP Server

Jupyter 노트북 관련 도구를 제공하는 MCP 서버입니다.
.ipynb 파일 작업 시에만 활성화됩니다.

사용법:
    claude mcp add notebook-tools -- python server.py

제공 도구:
    - notebook_edit: Jupyter 셀 편집
    - notebook_run: 셀 실행
    - notebook_export: 노트북 내보내기
"""

import json
import sys


class NotebookToolsServer:
    """Notebook Tools MCP 서버"""

    def __init__(self):
        self.tools = {
            "notebook_edit": self.notebook_edit,
            "notebook_run": self.notebook_run,
            "notebook_export": self.notebook_export,
        }

    def get_tool_definitions(self) -> list[dict]:
        """도구 정의 반환"""
        return [
            {
                "name": "notebook_edit",
                "description": "Jupyter 노트북 셀 편집",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "notebook_path": {
                            "type": "string",
                            "description": "노트북 파일 경로",
                        },
                        "cell_index": {"type": "integer", "description": "셀 인덱스"},
                        "new_source": {"type": "string", "description": "새 소스 코드"},
                        "cell_type": {"type": "string", "enum": ["code", "markdown"]},
                    },
                    "required": ["notebook_path", "cell_index", "new_source"],
                },
            },
            {
                "name": "notebook_run",
                "description": "Jupyter 노트북 셀 실행",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "notebook_path": {"type": "string"},
                        "cell_index": {"type": "integer"},
                    },
                    "required": ["notebook_path", "cell_index"],
                },
            },
            {
                "name": "notebook_export",
                "description": "노트북을 다른 형식으로 내보내기",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "notebook_path": {"type": "string"},
                        "format": {
                            "type": "string",
                            "enum": ["html", "pdf", "py", "md"],
                        },
                        "output_path": {"type": "string"},
                    },
                    "required": ["notebook_path", "format"],
                },
            },
        ]

    def notebook_edit(
        self,
        notebook_path: str,
        cell_index: int,
        new_source: str,
        cell_type: str = "code",
    ) -> dict:
        """노트북 셀 편집"""
        try:
            with open(notebook_path, "r", encoding="utf-8") as f:
                notebook = json.load(f)

            if 0 <= cell_index < len(notebook.get("cells", [])):
                notebook["cells"][cell_index]["source"] = new_source.split("\n")
                notebook["cells"][cell_index]["cell_type"] = cell_type

                with open(notebook_path, "w", encoding="utf-8") as f:
                    json.dump(notebook, f, indent=2, ensure_ascii=False)

                return {"success": True, "message": f"Cell {cell_index} updated"}
            else:
                return {"success": False, "error": f"Invalid cell index: {cell_index}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def notebook_run(self, notebook_path: str, cell_index: int) -> dict:
        """노트북 셀 실행 (nbclient 필요)"""
        return {"success": False, "error": "nbclient 패키지 필요: pip install nbclient"}

    def notebook_export(
        self, notebook_path: str, format: str, output_path: str = None
    ) -> dict:
        """노트북 내보내기 (nbconvert 필요)"""
        return {
            "success": False,
            "error": "nbconvert 패키지 필요: pip install nbconvert",
        }

    def handle_request(self, request: dict) -> dict:
        """MCP JSON-RPC 요청 처리"""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")

        result = None
        error = None

        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "notebook-tools", "version": "1.0.0"},
            }
        elif method == "notifications/initialized":
            return None  # No response for notifications
        elif method == "tools/list":
            result = {"tools": self.get_tool_definitions()}
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            if tool_name in self.tools:
                tool_result = self.tools[tool_name](**arguments)
                result = {
                    "content": [{"type": "text", "text": json.dumps(tool_result)}]
                }
            else:
                error = {"code": -32601, "message": f"Unknown tool: {tool_name}"}
        else:
            error = {"code": -32601, "message": f"Method not found: {method}"}

        if error:
            return {"jsonrpc": "2.0", "id": req_id, "error": error}
        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    def run(self):
        """서버 실행 (stdio JSON-RPC)"""
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                if response:  # Skip None responses (notifications)
                    print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    server = NotebookToolsServer()
    server.run()
