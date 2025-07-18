
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# ============================================================================
# 1. MCP 서버 구현 (계산 도구들)
# ============================================================================

app = Server("claude-calculator-server")

@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """사용 가능한 계산 도구 목록"""
    return [
        types.Tool(
            name="add_numbers",
            description="두 개의 숫자를 더합니다. 덧셈, 더하기, +, plus 등의 요청에 사용됩니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "number1": {"type": "number", "description": "첫 번째 숫자"},
                    "number2": {"type": "number", "description": "두 번째 숫자"}
                },
                "required": ["number1", "number2"]
            }
        ),
        types.Tool(
            name="summarize",
            description="회의 내용이 텍스트 형태로 전달될 것입니다. 이 함수는 "
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """도구 호출 처리"""
    try:
        num1 = float(arguments["number1"])
        num2 = float(arguments["number2"])
        
        if name == "add_numbers":
            result = num1 + num2
            operation = "+"
            
            # elif: result = function()
        else:
            return [types.TextContent(type="text", text=f"❌ 알 수 없는 도구: {name}")]
        
        if result == int(result):
            result_str = str(int(result))
        else:
            result_str = f"{result:.6f}".rstrip('0').rstrip('.')
        
        response_text = f"🧮 계산 결과: {num1} {operation} {num2} = {result_str}"
        
        return [types.TextContent(type="text", text=response_text)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"❌ 계산 오류: {str(e)}")]

@app.list_resources()
async def list_resources() -> List[types.Resource]:
    return []

@app.read_resource()
async def read_resource(uri: str) -> str:
    raise NotImplementedError("리소스 기능 없음")