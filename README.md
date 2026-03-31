# Supervisor Multi-Agent (계층형 다중 에이전트 시스템)

## 1. 프로젝트 개요

이 프로젝트는 LangGraph를 활용하여 하나의 관리자(Supervisor) 에이전트가 전체 작업 흐름을 통제하고 하위 에이전트(작업자)들에게 역할을 위임하는 수직적 조직 구조를 구현한 시스템입니다.

사용자가 복합적인 과제를 지시하면, 관리자 에이전트는 이를 분석하여 데이터를 수집하는 리서처(Researcher)와 보고서를 작성하는 분석가(Analyst)에게 순차적으로 작업을 지시합니다. 각 작업자가 임무를 마치면 제어권은 다시 관리자에게 돌아오며, 관리자가 최종적으로 목표 달성 여부를 판단하여 작업을 종료(FINISH)하는 지능적인 워크플로우를 가집니다.

## 2. 시스템 아키텍처

본 시스템은 중앙 통제 방식의 동적 라우팅 워크플로우를 가집니다.

1. **State Definition:** 전체 과제(Task), 리서치 데이터, 분석 결과, 다음 작업자 지정, 구체적 지시사항을 전역 상태로 공유합니다.
2. **Supervisor Node (관리자):** 현재까지 누적된 상태 데이터를 평가하여 다음 작업을 수행할 에이전트(researcher, analyst)를 결정하고, 그에 맞는 구체적인 프롬프트(지시사항)를 작성합니다. 과제가 완수되었다고 판단하면 'FINISH'를 선언합니다.
3. **Researcher Node (리서처):** 관리자의 지시를 받아 DuckDuckGo 웹 검색을 수행하고, 획득한 원시 데이터를 상태 객체에 누적합니다.
4. **Analyst Node (분석가):** 관리자의 지시와 누적된 리서치 데이터를 바탕으로 최종 마크다운 보고서를 작성합니다.
5. **Conditional Routing:** 관리자의 결정에 따라 작업자 노드로 분기하거나 종료(END) 노드로 이동하며, 작업자 노드는 실행이 끝나면 무조건 다시 관리자 노드로 연결되어 보고하는 순환 구조를 형성합니다.

## 3. 기술 스택

* **Language:** Python 3.10+
* **Package Manager:** uv
* **LLM:** OpenAI gpt-4o-mini (관리자, 리서처, 분석가 페르소나 부여)
* **Data Validation:** Pydantic (v2)
* **Orchestration:** LangGraph (계층형 라우팅), LangChain
* **Search Tool:** DuckDuckGo Search API (duckduckgo-search, ddgs)
* **Web Framework:** Streamlit

## 4. 프로젝트 구조

supervisor-agent/
├── .env                  
├── requirements.txt      
├── main.py               
└── app/
    ├── __init__.py
    └── graph.py          

## 5. 설치 및 실행 가이드

### 5.1. 환경 변수 설정
프로젝트 루트 경로에 .env 파일을 생성하고 API 키를 입력하십시오.

OPENAI_API_KEY=sk-your-api-key-here

### 5.2. 의존성 설치 및 앱 실행
독립된 가상환경을 구성하고 애플리케이션을 구동합니다.

uv venv
uv pip install -r requirements.txt
uv run streamlit run main.py

## 6. 테스트 시나리오 및 검증 방법

애플리케이션 구동 후 다음 과정을 통해 수직적 위임 아키텍처를 검증합니다.

* **복합 과제 입력:** 좌측 패널에 "최근 주요 인공지능 기업들의 동향을 검색하고, 이를 바탕으로 시장 전망 보고서를 작성하십시오"와 같은 다단계 과제를 입력합니다.
* **동적 위임 확인:** 관리자가 상황을 판단하여 먼저 Researcher에게 웹 검색을 지시하고, 완료 후 다시 Analyst에게 분석을 지시하는 단계적 흐름이 우측 패널에 표시되는지 확인합니다.
* **작업 종료(FINISH) 검증:** Analyst의 보고서 작성이 완료된 후 제어권을 넘겨받은 관리자가 스스로 목표 달성을 인지하고 FINISH를 선언하여 파이프라인을 정상 종료하는지 점검합니다.

## 7. 실행 화면