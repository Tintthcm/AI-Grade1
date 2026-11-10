import re
import urllib.parse
import google.generativeai as genai
import streamlit as st

# 1. Cấu hình trang & giao diện (Chữ to, màu sắc tươi sáng cho trẻ 6 tuổi)
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


# 3. Hàm gọi Gemini với System Instruction đa dạng phong cách (Bao gồm Ảnh thực tế & Hoạt hình)
@st.cache_data(ttl=86400)  # Lưu đệm 24h giúp 30 máy chạy mượt không bị nghẽn
def get_gemini_response(prompt_text):
  system_prompt = """
    Bạn là một người bạn vui tính dành cho học sinh lớp 1. 
    Học sinh sẽ nhập từ khóa bằng tiếng Việt KHÔNG DẤU (ví dụ: 'con meo', 'trai tao') hoặc tiếng Anh (ví dụ: 'cat', 'apple').

    Nhiệm vụ của bạn:
    1. Trả lời bằng tiếng Việt CÓ DẤU ngắn gọn (1-2 câu ngắn), giọng điệu vui tươi, dễ hiểu với trẻ 6 tuổi.
    2. Cuối câu trả lời, tạo một mô tả hình ảnh bằng tiếng Anh theo đúng cú pháp: [PROMPT_ENG: <mô tả hình ảnh>]

    QUY TẮC SÁNG TẠO PHONG CÁCH HÌNH ẢNH (PROMPT_ENG):
    - Hãy SÁNG TẠO VÀ THAY ĐỔI PHONG CÁCH NGHỆ THUẬT (Art Style) ngẫu nhiên hoặc chọn style hợp nhất với từ khóa:
      + Real photograph (Ảnh chụp thực tế chân thực, sắc nét, màu sắc tươi sáng, cận cảnh)
      + Claymation / Play-Doh (Tạo hình đất nặn tròn ngộ nghĩnh)
      + Soft Watercolor illustration (Tranh màu nước nhẹ nhàng)
      + Cute Kawaii vector / Chibi cartoon (Nét vẽ hoạt hình đáng yêu)
      + Paper cut-out art (Nghệ thuật cắt dán giấy 3D)
      + Crayon drawing (Tranh vẽ màu sáp tươi sáng)
      + Plushie / Felt toy style (Thú nhồi bông/vải nỉ đáng yêu)
      + 3D Pixar / Disney animation (Hình 3D hoạt hình)
    - Cấu trúc prompt: A cute/beautiful <Art Style> of <đối tượng>, <hành động/chi tiết>, bright vivid colors, clean simple background.
    - Tuyệt đối không dùng dấu ngoặc kép hoặc ký tự đặc biệt trong PROMPT_ENG.

    Ví dụ: 
    - Bé gõ "con meo" -> Trả lời: "Con mèo là loài vật cưng đáng yêu, thích bắt chuột và kêu meo meo! [PROMPT_ENG: A cute real photograph of a fluffy baby kitten sitting on green grass, natural daylight, sharp focus]"
    - Bé gõ "trai tao" -> Trả lời: "Quả táo có màu đỏ giòn ngọt, ăn rất ngon và tốt cho sức khỏe! [PROMPT_ENG: A fresh real photograph of a shiny red apple with leaf on wooden table, bright daylight]"
    - Bé gõ "may bay" -> Trả lời: "Máy bay giúp chúng ta bay cao trên bầu trời rộng lớn! [PROMPT_ENG: A cute paper cut-out art style toy airplane flying, clear blue sky, bright vivid colors]"
    - Bé gõ "con gau" -> Trả lời: "Gấu bông ấm áp là người bạn ngủ cùng rất ngoan của em đấy! [PROMPT_ENG: A cute plushie felt toy style brown teddy bear, fluffy texture, bright vivid colors, clean background]"
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
  clean_input = user_input.strip().lower()

  with st.spinner("Đang tìm hình và câu trả lời cho bé..."):
    try:
      full_text = get_gemini_response(clean_input)

      # Tách lời giải thích và prompt tiếng Anh
      if "[PROMPT_ENG:" in full_text:
        explanation, img_prompt_part = full_text.split("[PROMPT_ENG:")
        img_prompt = img_prompt_part.replace("]", "").strip()
      else:
        explanation = full_text
        img_prompt = f"A cute photograph of {clean_input}"

      # Xóa các ký tự nhiễu (dấu ngoặc, dấu sao...)
      clean_img_prompt = re.sub(r'[*"`]', "", img_prompt).strip()

      # 1. Hiển thị lời giải thích bằng chữ to
      st.markdown(
          f'<div class="big-text">{explanation.strip()}</div>',
          unsafe_allow_html=True,
      )
      st.write("")

      # 2. Mã hóa URL Pollinations với mô hình FLUX
      encoded_prompt = urllib.parse.quote(clean_img_prompt)

      # Mô hình FLUX vẽ xuất sắc cả ảnh thực lẫn hình nghệ thuật
      image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true&model=flux"

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
