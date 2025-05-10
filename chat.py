import streamlit as st
import requests
import json
import uuid

# 세션 ID 관리
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Spring Boot 서버 URL
SPRING_API_URL = "http://localhost:8080/api/v1/chat/message"

st.title("요레모 챗봇")

# 이전 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("요리에 관련된 무엇이든 물어보세요!"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 챗봇 API 호출
    request_data = {
        "question": prompt,
        "session_id": st.session_state.session_id
    }

    with st.spinner("..."):
        try:
            response = requests.post(
                SPRING_API_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(request_data)
            )
            response.raise_for_status()  # 오류 확인

            # 응답 처리
            ai_response = response.json().get("answer", "응답을 생성하지 못했습니다.")

            # AI 응답 표시
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

        except requests.exceptions.RequestException as e:
            st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
