import json
import uuid

import requests
import streamlit as st
from streamlit_lottie import st_lottie

# 페이지 설정 및 테마 구성
st.set_page_config(
    page_title="요레모 챗봇",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 커스텀 CSS 적용
def apply_custom_css():
    st.markdown("""
    <style>
    /* 제목 스타일링 */
    .main-title {
        font-family: 'Noto Sans KR', sans-serif;
        color: #FF6B6B;
        font-size: 3.2em;
        font-weight: 700;
        margin-bottom: 20px;
        text-align: center;
    }

    /* 챗 메시지 스타일링 */
    .user-message {
        background-color: #F0F7FF;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #4361EE;
    }

    .assistant-message {
        background-color: #FFF6F0;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #FF6B6B;
    }

    /* 입력창 스타일링 */
    .stTextInput>div>div>input {
        border-radius: 20px;
        padding: 15px;
        border: 2px solid #FF6B6B;
    }

    /* 버튼 스타일링 */
    .stButton>button {
        border-radius: 20px;
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px 25px;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        background-color: #FF8C8C;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


apply_custom_css()

# 세션 ID 관리
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Spring Boot 서버 URL
SPRING_API_URL = "http://localhost:8080/api/chat/v1/message"

# 사이드바 구성
with st.sidebar:
    st.image("./resources/yorizori.jpeg", width=300)
    st.markdown("### 요레모 챗봇 🍳")
    st.markdown("요리에 관련된 무엇이든 물어보세요!")

    st.markdown("---")
    st.markdown("### 추천 질문")

    # 추천 질문 버튼들
    if st.button("오늘 저녁 메뉴 추천해줘"):
        st.session_state.messages.append({"role": "user", "content": "오늘 저녁 메뉴 추천해줘"})

    if st.button("김치찌개 레시피 알려줘"):
        st.session_state.messages.append({"role": "user", "content": "김치찌개 레시피 알려줘"})

    if st.button("초보자도 쉽게 만들 수 있는 요리는?"):
        st.session_state.messages.append({"role": "user", "content": "초보자도 쉽게 만들 수 있는 요리는?"})

    st.markdown("---")

    # 대화 초기화 버튼
    if st.button("대화 초기화"):
        st.session_state.messages = []

    st.markdown("<div style='margin-top: 100px; text-align: center; color: #888;'>© 2025 요레모 - 모든 요리의 레시피를 모았다</div>",
                unsafe_allow_html=True)


# 로티 애니메이션 로딩
def load_lottie(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


# 메인 컨텐츠
st.markdown("<h1 class='main-title'>요레모 챗봇</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-bottom: 30px;'>맛있는 요리의 모든 것, 요레모와 함께하세요!</p>",
            unsafe_allow_html=True)

# 채팅 컨테이너
chat_container = st.container()

# 이전 메시지 표시
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"<div class='user-message'><strong>나:</strong> {message['content']}</div>",
                            unsafe_allow_html=True)
        else:
            with st.chat_message("assistant"):
                st.markdown(f"<div class='assistant-message'><strong>요레모:</strong> {message['content']}</div>",
                            unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("요리에 관련된 무엇이든 물어보세요!"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div class='user-message'><strong>나:</strong> {prompt}</div>", unsafe_allow_html=True)

    # 로딩 애니메이션
    animation_placeholder = st.empty()
    with st.spinner():
        cooking_animation = load_lottie("./resources/cooking_animation.json")
        if cooking_animation:
            with animation_placeholder:
                st_lottie(cooking_animation, speed=1, height=200, key="cooking")

        # 챗봇 API 호출
        request_data = {
            "question": prompt,
            "session_id": st.session_state.session_id
        }

        try:
            response = requests.post(
                SPRING_API_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(request_data)
            )
            response.raise_for_status()  # 오류 확인

            # 응답 처리
            ai_response = response.json().get("answer", "응답을 생성하지 못했습니다.")

            # 애니메이션 제거
            animation_placeholder.empty()

            # AI 응답 표시
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(f"<div class='assistant-message'><strong>요레모:</strong> {ai_response}</div>",
                            unsafe_allow_html=True)

        except requests.exceptions.RequestException as e:
            animation_placeholder.empty()
            st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
