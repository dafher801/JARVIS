import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import anthropic
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
            name="subtract_numbers", 
            description="두 개의 숫자를 뺍니다. 빼기, 차이, -, minus 등의 요청에 사용됩니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "number1": {"type": "number", "description": "첫 번째 숫자 (피감수)"},
                    "number2": {"type": "number", "description": "두 번째 숫자 (감수)"}
                },
                "required": ["number1", "number2"]
            }
        ),
        types.Tool(
            name="multiply_numbers",
            description="두 개의 숫자를 곱합니다. 곱하기, 곱셈, ×, *, multiply 등의 요청에 사용됩니다.",
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
            name="divide_numbers",
            description="두 개의 숫자를 나눕니다. 나누기, 나눔, /, divide 등의 요청에 사용됩니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "number1": {"type": "number", "description": "첫 번째 숫자 (피제수)"},
                    "number2": {"type": "number", "description": "두 번째 숫자 (제수)"}
                },
                "required": ["number1", "number2"]
            }
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
        elif name == "subtract_numbers":
            result = num1 - num2
            operation = "-"
        elif name == "multiply_numbers":
            result = num1 * num2
            operation = "×"
        elif name == "divide_numbers":
            if num2 == 0:
                return [types.TextContent(type="text", text="❌ 오류: 0으로 나눌 수 없습니다!")]
            result = num1 / num2
            operation = "÷"
        else:
            return [types.TextContent(type="text", text=f"❌ 알 수 없는 도구: {name}")]
        
        # 결과 포맷팅
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

# ============================================================================
# 2. Claude AI 클라이언트
# ============================================================================

class ClaudeCalculatorClient:
    """Claude AI를 사용한 자연어 처리 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경변수를 설정하거나 API 키를 제공해주세요.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.tools = []
        
    async def initialize_tools(self):
        """MCP 도구 정보 가져오기"""
        self.tools = await list_tools()
        print(f"✅ {len(self.tools)}개 도구 로드됨: {[t.name for t in self.tools]}")
    
    def _format_tools_for_claude(self) -> List[Dict]:
        """Claude API 형식으로 도구 정보 변환"""
        claude_tools = []
        for tool in self.tools:
            claude_tools.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            })
        return claude_tools
    
    async def process_user_message(self, user_input: str) -> str:
        """사용자 메시지를 Claude가 처리하고 필요시 도구 호출"""
        try:
            print(f"🤔 Claude가 분석 중: '{user_input}'")
            
            # Claude에게 메시지 전송
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # 최신 Claude 모델
                max_tokens=1000,
                tools=self._format_tools_for_claude(),
                tool_choice={"type": "auto"},
                messages=[{
                    "role": "user", 
                    "content": f"""이것은 수학 계산 요청입니다: "{user_input}"

텍스트로 답하지 말고 반드시 도구를 사용해서 계산하세요.

숫자를 찾아서 적절한 도구를 호출해주세요:
- 더하기/덧셈/+ → add_numbers 도구 사용
- 빼기/뺄셈/- → subtract_numbers 도구 사용  
- 곱하기/곱셈/× → multiply_numbers 도구 사용
- 나누기/나눗셈/÷ → divide_numbers 도구 사용

절대 텍스트로만 응답하지 마세요. 도구를 사용하세요."""
                }]
            )
            
            # Claude의 응답 처리
            if response.content:
                for content in response.content:
                    if hasattr(content, 'type'):
                        if content.type == "tool_use":
                            # 도구 호출이 필요한 경우
                            tool_name = content.name
                            tool_args = content.input
                            
                            print(f"🔧 Claude가 도구 호출: {tool_name}({tool_args})")
                            
                            # MCP 도구 실행
                            results = await call_tool(tool_name, tool_args)
                            tool_result = results[0].text if results else "계산 실패"
                            
                            # Claude에게 도구 결과 전달하고 최종 응답 받기
                            final_response = self.client.messages.create(
                                model="claude-3-5-sonnet-20241022",
                                max_tokens=1000,
                                messages=[
                                    {
                                        "role": "user", 
                                        "content": user_input
                                    },
                                    {
                                        "role": "assistant",
                                        "content": response.content
                                    },
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "tool_result",
                                                "tool_use_id": content.id,
                                                "content": tool_result
                                            }
                                        ]
                                    }
                                ]
                            )
                            
                            return final_response.content[0].text if final_response.content else tool_result
                        
                        elif content.type == "text":
                            # 일반 텍스트 응답
                            return content.text
            
            return "죄송합니다. 응답을 처리할 수 없습니다."
            
        except Exception as e:
            return f"❌ Claude 처리 오류: {str(e)}"

# ============================================================================
# 3. 대화형 시스템
# ============================================================================

class InteractiveCalculatorSystem:
    """대화형 계산기 시스템"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.claude_client = ClaudeCalculatorClient(api_key)
    
    async def start_chat(self):
        """채팅 시작"""
        print("🚀 Claude AI 계산기가 시작되었습니다!")
        print("=" * 60)
        print("💡 사용 예시:")
        print("  • '5와 3을 더해줘'")
        print("  • '10에서 4를 빼면?'") 
        print("  • '7 곱하기 8은 얼마야?'")
        print("  • '15를 3으로 나눠줘'")
        print("  • '안녕하세요' (일반 대화도 가능)")
        print("=" * 60)
        print("⚠️  종료: 'quit', 'exit', '종료' 입력")
        print()
        
        # 도구 초기화
        await self.claude_client.initialize_tools()
        
        while True:
            try:
                user_input = input("💬 당신: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '종료', 'q']:
                    print("👋 Claude 계산기를 종료합니다. 안녕히 가세요!")
                    break
                
                # Claude가 처리
                response = await self.claude_client.process_user_message(user_input)
                print(f"🤖 Claude: {response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Claude 계산기를 종료합니다!")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {str(e)}\n")

# ============================================================================
# 4. 메인 실행부
# ============================================================================

async def setup_api_key():
    """API 키 설정"""
    api_key = os.getenv("CLAUDE_SCENARIO_SCRIPT_SUB_KEY")
    
    if not api_key:
        print("🔑 Anthropic API 키가 필요합니다.")
        print("1. 환경변수로 설정: ANTHROPIC_API_KEY=your_key")
        print("2. 또는 아래에 직접 입력:")
        
        api_key = input("API 키를 입력하세요: ").strip()
        if not api_key:
            print("❌ API 키가 필요합니다. 프로그램을 종료합니다.")
            sys.exit(1)
    
    return api_key

async def run_mcp_server():
    """순수 MCP 서버 모드"""
    print("🚀 MCP 서버 모드로 실행 중...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

async def main():
    """메인 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # MCP 서버 모드
        await run_mcp_server()
    else:
        # Claude AI 채팅 모드 (기본)
        try:
            api_key = await setup_api_key()
            calculator = InteractiveCalculatorSystem(api_key)
            await calculator.start_chat()
        except Exception as e:
            print(f"❌ 시작 오류: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())