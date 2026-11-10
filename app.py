import urllib.parse
import google.generativeai as genai
import streamlit as st

# 1. Cấu hình trang & giao diện (Chữ to, dễ thao tác cho trẻ 6 tuổi)
st.set_page_config(page_title="Góc Học Tập Của Bé", layout="centered")

st.markdown(
    """
    <style>
    /* Phóng to ô nhập liệu */
    .stTextInput > div > div > input {
        font-size: 26px !important;
        text-align: center;
        height: 65px;
        border-radius: 15px;
        border: 3px solid #4CAF50;
    }
    /* Khung hiển thị lời giải thích chữ siêu to */
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

# 2. Cấu hình Gemini API an toàn từ Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
  GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
  st.error(
      "Chưa cài đặt GEMINI_API_KEY trong cấu hình Secrets của Streamlit Cloud!"
  )
  st.stop()

genai.configure(api_key=GEMINI_API_KEY)


# 3. Hàm gọi Gemini có tích hợp Cache (Giúp 30 máy cùng học không bị nghẽn)
@st.cache_data(ttl=86400)  # Lưu kết quả trùng lặp trong 24h
def get_gemini_response(prompt_text):
  system_prompt = """
    Bạn là một người bạn vui tính dành cho học sinh lớp 1. 
    Học sinh sẽ nhập từ khóa bằng tiếng Việt KHÔNG DẤU (ví dụ: 'con meo', 'trai tao') hoặc tiếng Anh (ví dụ: 'cat', 'apple').

    Nhiệm vụ của bạn:
    1. Trả lời bằng tiếng Việt CÓ DẤU ngắn gọn (1-2 câu ngắn), giọng điệu vui tươi, dễ hiểu với trẻ 6 tuổi.
    2. Cuối câu trả lời, tạo một mô tả hình ảnh chi tiết bằng tiếng Anh theo đúng cú pháp: [PROMPT_ENG: <mô tả chi tiết>]

    QUY TẮC TẠO PROMPT_ENG (Mô tả hình ảnh):
    - Mở rộng từ khóa ngắn của bé thành mô tả chi tiết: Đối tượng + Cảm xúc/Hành động + Màu sắc/Đặc điểm + Phong cách.
    - Ưu tiên phong cách 3D Pixar, nhân vật hoạt hình mắt to tròn, mỉm cười, đáng yêu.
    - Đặt đối tượng ở chính giữa (centered composition), nền sạch/đơn giản để bé dễ nhìn.

    Ví dụ: 
    - Bé gõ "con meo" -> Trả lời: "Con mèo là loài vật cưng đáng yêu, thích bắt chuột và kêu meo meo! [PROMPT_ENG: a cute happy fluffy baby cat sitting, big round expressive eyes, friendly smile, 3D Pixar style, soft lighting]"
    - Bé gõ "trai tao" -> Trả lời: "Quả táo có màu đỏ giòn ngọt, ăn rất ngon và tốt cho sức khỏe! [PROMPT_ENG: a fresh shiny red apple with a green leaf, cute smiling face, 3D cartoon icon style, vibrant colors]"
    - Bé gõ "may bay" -> Trả lời: "Máy bay giúp chúng ta bay cao trên bầu trời rộng lớn! [PROMPT_ENG: a cute colorful toy airplane flying in a clear blue sky, smiling face, 3D animation style]"
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
  # Làm sạch từ khóa đầu vào
  clean_input = user_input.strip().lower()

  with st.spinner("Đang tìm hình và câu trả lời cho bé..."):
    try:
      # Lấy câu trả lời từ Gemini
      full_text = get_gemini_response(clean_input)

      # Tách lời giải thích và prompt tiếng Anh
      if "[PROMPT_ENG:" in full_text:
        explanation, img_prompt_part = full_text.split("[PROMPT_ENG:")
        img_prompt = img_prompt_part.replace("]", "").strip()
      else:
        explanation = full_text
        img_prompt = clean_input

      # 1. Hiển thị lời giải thích bằng chữ to
      st.markdown(
          f'<div class="big-text">{explanation.strip()}</div>',
          unsafe_allow_html=True,
      )
      st.write("")

      # 2. Ghép thêm chất lượng cao & Gọi Pollinations AI vẽ ảnh
      full_image_prompt = (
          f"{img_prompt}, 3D character render, Pixar style, centered"
          " composition, soft lighting, bright vivid colors, simple clean"
          " background, masterpiece, high detail"
      )
      encoded_prompt = urllib.parse.quote(full_image_prompt)
      image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"

      # Hiển thị ảnh minh họa
      st.image(
          image_url,
          caption=f"Hình minh họa: {user_input}",
          use_container_width=True,
      )

    except Exception as e:
      st.error(
          "Nhiều bạn đang gõ cùng lúc quá, em chờ 5 giây rồi gõ lại thử xem"
          " sao nhé!"
      )
