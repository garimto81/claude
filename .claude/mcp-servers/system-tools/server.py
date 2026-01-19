"""
System Tools MCP Server

시스템 관리 도구를 제공하는 MCP 서버입니다.
백그라운드 작업, 프로세스 관리 등에 사용됩니다.

사용법:
    claude mcp add system-tools -- python server.py

제공 도구:
    - kill_process: 특정 프로세스 종료
    - list_background_tasks: 백그라운드 작업 목록
    - system_info: 시스템 정보 조회
"""

import json
import os
import sys


class SystemToolsServer:
    """System Tools MCP 서버"""

    def __init__(self):
        self.tools = {
            "kill_process": self.kill_process,
            "list_background_tasks": self.list_background_tasks,
            "system_info": self.system_info,
        }
        self.background_tasks = {}

    def get_tool_definitions(self) -> list[dict]:
        """도구 정의 반환"""
        return [
            {
                "name": "kill_process",
                "description": "특정 프로세스 종료 (PID 또는 이름)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pid": {"type": "integer", "description": "프로세스 ID"},
                        "name": {"type": "string", "description": "프로세스 이름"},
                        "force": {"type": "boolean", "default": False},
                    },
                },
            },
            {
                "name": "list_background_tasks",
                "description": "현재 백그라운드 작업 목록 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["running", "completed", "all"],
                        },
                    },
                },
            },
            {
                "name": "system_info",
                "description": "시스템 정보 조회 (CPU, 메모리, 디스크)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["cpu", "memory", "disk", "all"],
                        },
                    },
                },
            },
        ]

    def kill_process(
        self, pid: int = None, name: str = None, force: bool = False
    ) -> dict:
        """프로세스 종료"""
        if pid is None and name is None:
            return {"success": False, "error": "pid 또는 name 필요"}

        try:
            if pid:
                os.kill(pid, 9 if force else 15)
                return {"success": True, "message": f"Process {pid} terminated"}
            else:
                return {"success": False, "error": "이름으로 종료는 psutil 필요"}
        except ProcessLookupError:
            return {"success": False, "error": f"Process {pid} not found"}
        except PermissionError:
            return {"success": False, "error": "Permission denied"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_background_tasks(self, status: str = "all") -> dict:
        """백그라운드 작업 목록"""
        tasks = []
        for task_id, task in self.background_tasks.items():
            if status == "all" or task.get("status") == status:
                tasks.append({"id": task_id, **task})
        return {"success": True, "tasks": tasks, "count": len(tasks)}

    def system_info(self, category: str = "all") -> dict:
        """시스템 정보"""
        info = {}

        if category in ["cpu", "all"]:
            info["cpu"] = {"count": os.cpu_count()}

        if category in ["memory", "all"]:
            info["memory"] = {"note": "psutil 필요: pip install psutil"}

        if category in ["disk", "all"]:
            info["disk"] = {"note": "psutil 필요: pip install psutil"}

        return {"success": True, "info": info}

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
                "serverInfo": {"name": "system-tools", "version": "1.0.0"},
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
    server = SystemToolsServer()
    server.run()
