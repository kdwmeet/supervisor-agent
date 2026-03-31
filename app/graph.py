from typing import TypedDict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, START, END

load_dotenv()

# Pydantic 스키마 정의
class SupervisorDecision(BaseModel):
    """관리자의 다음 작업자 지시"""
    next_worker: str = Field(description="다음 작업을 수행할 에이전트. 'researcher', 'analyst', 'FINISH' 중 하나를 선택하십시오.")
    instruction: str = Field(description="선택된 에이전트에게 전달할 구체적인 작업 지시사항. FINISH인 경우 최종 완료 메시지를 작성하십시오.")

# 상태 정의
class TeamState(TypedDict):
    task: str
    research_data: str
    analysis_result: str
    next_worker: str
    instruction: str

# 도구 및 노드 구현
search_tool = DuckDuckGoSearchRun()

def supervisor_node(state: TeamState):
    """작업 진행 상황을 파악하고 다음 작업자를 결정합니다."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    structured_llm = llm.with_structured_output(SupervisorDecision)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 팀을 이끄는 관리자(Supervisor)입니다.
당신의 팀에는 데이터를 수집하는 'researcher'와 수집된 데이터를 바탕으로 보고서를 작성하는 'analyst'가 있습니다.
주어진 목표(Task)를 달성하기 위해 현재까지의 진행 상황을 바탕으로 다음에 누가 작업해야 할지 결정하십시오.
데이터가 부족하다면 researcher에게 검색을 지시하고, 데이터가 충분하다면 analyst에게 보고서 작성을 지시하십시오.
최종 보고서가 작성되었고 목표가 완전히 달성되었다면 next_worker를 'FINISH'로 설정하십시오."""),
        ("user", "목표: {task}\n\n수집된 데이터: {research}\n\n분석 결과: {analysis}")
    ])

    result: SupervisorDecision = (prompt | structured_llm).invoke({
        "task": state["task"],
        "research": state.get("research_data", "아직 수집되지 않음"),
        "analysis": state.get("analysis_result", "아직 작성되지 않음")
    })

    return {"next_worker": result.next_worker, "instruction": result.instruction}

def resaercher_node(state: TeamState):
    """웹 검색을 통해 데이터를 수집합니다."""
    try:
        search_result = search_tool.invoke(state["instruction"])
    except Exception as e:
        search_result = f"검색 중 오류 발생: {str(e)}"

        # 기존 데이터에 새로운 검색 결과를 누적
        current_data = state.get("research_data", "")
        new_data = f"{current_data}\n\n[추가 검색 결과]\n{search_result}" if current_data else search_result

        return {"research_data": new_data}
    
def analyst_node(state: TeamState):
    """수집된 데이터를 분석하고 최종 보고서를 작성합니다."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 수석 데이터 분석가입니다. 관리자의 지시사항과 수집된 데이터를 바탕으로 마크다운 형식의 깔끔하고 구조화된 분석 보고서를 작성하십시오."),
        ("user", "지시사항: {instruction}\n\n수집된 데이터:\n{research}")
    ])

    response = (prompt | llm).invoke({
        "instruction": state["instruction"],
        "research": state["research_data"]
    })

    return {"analysis_result": response.content}
   
# 라우팅 로직
def route_supervisor(state: TeamState):
    """관리자의 결정에 따라 분기합니다."""
    if state["next_worker"] == "FINISH":
        return END
    return state["next_worker"]

# 그래프 조립
workflow = StateGraph(TeamState)

workflow.add_node("supervisor_node", supervisor_node)
workflow.add_node("researcher", resaercher_node)
workflow.add_node("analyst", analyst_node)

# 항상 관리자부터 시작하여 업무를 파악
workflow.add_edge(START, "supervisor_node")

# 관리자의 결정에 따르 조건부 라우팅
workflow.add_conditional_edges(
    "supervisor_node",
    route_supervisor,
    {"researcher": "researcher", "analyst": "analyst", END: END}
)

# 하위 작업자들은 일이 끝나면 무조건 다시 관리자에게 결과를 보고함
workflow.add_edge("researcher", "supervisor_node")
workflow.add_edge("analyst", "supervisor_node")

app_graph = workflow.compile()