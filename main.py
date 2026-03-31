import streamlit as st
from app.graph import app_graph

st.set_page_config(page_title="계층형 다중 에이전트", layout="wide")

st.title("계층형 다중 에이전트 시스템 (Supervisor Multi-Agent)")
st.markdown("관리자 에이전트가 전체 목표를 이해하고, 리서처와 분석가에게 순차적으로 업무를 지시하여 최종 결과물을 도출합니다.")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("업무 지시")
    with st.form(key="supervisor_from"):
        task_input = st.text_area(
            "에이전트 팀에 지시할 복합적인 과제를 입력하십시오.",
            placeholder= "예: 최근 주요 빅테크 기업들의 분기 실적 발표 요점과 시장의 반응을 조사하고, 이를 바탕으로 요약 보고서를 작성해 주심시요.",
            height=200
        )
        submit_btn = st.form_submit_button("작업 시작", use_container_width=True)

with col2:
    st.subheader("실시간 진행 상황 및 결과")
    
    if submit_btn and task_input.strip():
        initial_state = {
            "task": task_input,
            "research_data": "",
            "analysis_result": "",
            "next_worker": "",
            "instruction": ""
        }
        
        status_placeholder = st.empty()
        final_state = initial_state.copy()
        
        with st.spinner("관리자가 업무를 계획하고 지시를 내리고 있습니다..."):
            for output in app_graph.stream(initial_state):
                for node_name, state_update in output.items():
                    # 상태 업데이트 병합
                    final_state.update(state_update)
                    
                    with status_placeholder.container():
                        if node_name == "supervisor_node":
                            worker = state_update.get("next_worker", "판단 중")
                            if worker == "FINISH":
                                st.success("[관리자] 모든 작업이 완료되었습니다. 결과를 출력합니다.")
                            else:
                                st.info(f"[관리자] '{worker}' 에이전트에게 업무 지시:\n- {state_update.get('instruction')}")
                        elif node_name == "researcher":
                            st.warning("[리서처] 웹 검색을 수행하고 데이터를 수집했습니다.")
                        elif node_name == "analyst":
                            st.success("[분석가] 수집된 데이터를 분석하여 보고서 작성을 완료했습니다.")
                            
        # 최종 결과 출력
        if final_state.get("analysis_result"):
            with st.container(border=True):
                st.markdown("### 최종 분석 보고서")
                st.markdown(final_state["analysis_result"])
            
            with st.expander("리서처가 수집한 원시 데이터 확인"):
                st.text_area("Research Data", value=final_state.get("research_data", ""), height=250, disabled=True)

    elif not submit_btn:
        st.info("좌측에 과제를 입력하고 작업 시작 버튼을 누르십시오.")