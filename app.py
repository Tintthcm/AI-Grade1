import os
import urllib.parse
import google.generativeai as genai
import streamlit as st

# 1. Cấu hình trang & giao diện
st.set_page_config(page_title="Góc Học Tập Của Bé", layout="centered")

st.markdown(
    """
    <style>
    .stTextInput > div > div > input {
        font-size: 26px !important;
        text-align: center;
        height: 65px;
        border-radius: 15px;
        border: 3px solid #4CAF50;
    }
    .big-text {
        font-size: 28px !important;
        font-weight: bold;
        color: #0D47A1;
        text-align: center;
        line-height: 1.5;
        background-color: #E3F2FD;
        padding: 20px;
        border-radius: 15px;
        margin-top: 15px;
        border: 2px dashed #2196F3;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🐱 BẠN NHỎ THÔNG MINH 🐶")
st.write("### Em hãy gõ tên con vật hoặc đồ vật vào ô bên dưới nhé!")

# 2. Kiểm tra API Key
if "GEMINI_API_KEY" in st.secrets:
  GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
  st.error("Chưa cài đặt GEMINI_API_KEY trong cấu hình Streamlit!")
  st.stop()

genai.configure(api_key=GEMINI_API_KEY)


# 3. Hàm gọi Gemini có tích hợp Cache (Lưu kết quả trùng lặp)
@st.cache_data(ttl=86400)  # Lưu kết quả trong 24 giờ
def get_gemini_response(prompt_text):
  system_prompt = """
    Bạn là một người bạn vui tính dành cho học sinh lớp 1. 
    Học sinh sẽ nhập từ khóa bằng tiếng Việt KHÔNG DẤU (ví dụ: 'con meo', 'trai tao') hoặc tiếng Anh (ví dụ: 'cat', 'apple').

    Nhiệm vụ của bạn:
    1. Trả lời bằng tiếng Việt CÓ DẤU ngắn gọn (chỉ 1 đến 2 câu ngắn), giọng điệu vui tươi, dễ hiểu với trẻ 6 tuổi.
    2. Cuối câu trả lời, ghi chính xác cú pháp: [PROMPT_ENG: <từ tiếng Anh để tạo ảnh>]

    Ví dụ: 
    Bé gõ "con meo" -> Trả lời: "Con mèo là loài vật cưng đáng yêu, thích bắt chuột và kêu meo meo! [PROMPT_ENG: cute cat cartoon]"
    """
  model = genai.GenerativeModel(
      model_name="gemini-2.5-flash", system_instruction=system_prompt
  )
  response = model.generate_content(prompt_text)
  return response.text


# 4. Ô nhập liệu cho học sinh
user_input = st.text_input(
    "", placeholder="Gõ vào đây (Ví dụ: con meo, trai tao, dog)..."
)

if user_input:
  # Chuẩn hóa từ khóa nhập vào (viết thường, xóa khoảng trắng thừa) để tăng tỉ lệ dùng Cache
  clean_input = user_input.strip().lower()

  with st.spinner("Đang tìm hình và câu trả lời cho bé..."):
    try:
      # Gọi hàm đã có Cache
      full_text = get_gemini_response(clean_input)

      if "[PROMPT_ENG:" in full_text:
        explanation, img_prompt_part = full_text.split("[PROMPT_ENG:")
        img_prompt = img_prompt_part.replace("]", "").strip()
      else:
        explanation = full_text
        img_prompt = clean_input

      st.markdown(
          f'<div class="big-text">{explanation.strip()}</div>',
          unsafe_allow_html=True,
      )
      st.write("")

      # Link ảnh Pollinations AI
      encoded_prompt = urllib.parse.quote(
          f"cute cartoon style, {img_prompt}, bright colors, white background,"
          " for kids"
      )
      image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"

      st.image(
          image_url,
          caption=f"Hình minh họa: {user_input}",
          use_container_width=True,
      )

    except Exception as e:
      st.error(
          "Nhiều bé đang gõ cùng lúc quá, em chờ vài giây rồi gõ lại nhé!"
      )
