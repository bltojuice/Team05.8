import google.generativeai as genai
from screen_img import capture_image_bytes
import asyncio

GOOGLE_API_KEY = "AIzaSyB3SvfNCUQdCX9wbrjFJQddWbSqgLT86S0"
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_with_gemini(image_bytes, prompt=(
    "너는 IT 기기에 익숙하지 않은 사람을 돕는 안내 도우미야. "
    "사용자는 키오스크 화면을 사진으로 캡처해서 너에게 보여줄 거야. "
    "너는 이 이미지를 보고 사용자가 어떤 버튼을 누를 건지 하나의 질문을 해줘. "
    "사용자가 눌러야 할 버튼이 하나뿐이라면 질문 대신 가이드를 해주고, 그 가이드 앞 뒤에 '/'를 달아줘."
    "다만 이때 주어진 이미지에 대해서만 분석하고 절대 다음 상태를 예상, 예측하지마."
    "너 사용자에게 한 질문 앞 뒤에 '*'을 달아줘. "
    "절대로 이 규칙을 잊지 마."
)):
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    response = model.generate_content(
        [prompt, {'mime_type': 'image/jpeg', 'data': image_bytes}]
    )
    return response.text

def main():
    print("카메라로 이미지 캡처 중...")
    image_bytes = capture_image_bytes()
    if image_bytes is None:
        print("이미지 캡처 실패 또는 종료됨")
        return

    print("Gemini 분석 중...")
    result = analyze_with_gemini(image_bytes)
    # 음성으로 질문하기
    question, text_res = result.split('!!,')
    print(result)
    if(question == '1'):
        print("\n🗣️ 질문:")
        print(question)#-----------------------해당 부분 핸들링 필요
    print("\n🧠 키오스크 분석 결과:")
    print(text_res)

if __name__ == "__main__":
    main()