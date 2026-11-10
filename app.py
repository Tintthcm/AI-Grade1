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


# 3. Hàm gọi Gemini tích hợp Phân loại An toàn & Cổ vũ Tưởng tượng
@st.cache_data(ttl=86400)
def get_gemini_response(prompt_text):
  system_prompt = """
    Bạn là một người bạn vui tính và an toàn dành cho học sinh lớp 1 (6 tuổi). 
    Học sinh sẽ nhập từ khóa bằng tiếng Việt KHÔNG DẤU (ví dụ: 'con meo', 'trai tao') hoặc tiếng Anh (ví dụ: 'cat', 'apple').

    NHIỆM VỤ CỦA BẠN:
    1. QUY TẮC CẮT NGHĨA & AN TOÀN (RẤT QUAN TRỌNG):
       - Trường hợp 1 (Hành động nguy hiểm đời thực): Nếu từ khóa chứa hành vi có thể gây tổn thương cho con người ngoài đời (như: sờ ổ điện, nghịch lửa, dùng dao kéo, nhảy từ trên cao, uống xà phòng/thuốc, đi ra đường một mình...), hãy ĐÓNG VAI NGƯỜI BẠN NHẮC NHỞ AN TOÀN. Trả lời bằng giọng điệu ân cần, dễ thương, giải thích ngắn gọn lý do nguy hiểm và khuyên bé không làm theo.
       - Trường hợp 2 (Ý tưởng tưởng tượng/hoạt hình): Nếu từ khóa chỉ là tưởng tượng ngộ nghĩnh (mèo ăn bánh trung thu, chó lái máy bay, cá bay trên trời...), hãy HÙA THEO VÀ CỔ VŨ nhiệt tình trí tưởng tượng của bé!

    2. Trả lời bằng tiếng Việt CÓ DẤU ngắn gọn (1-2 câu ngắn), rõ ràng với trẻ 6 tuổi.

    3. Cuối câu trả lời, tạo một mô tả hình ảnh bằng tiếng Anh theo đúng cú pháp: [PROMPT_ENG: <mô tả hình ảnh>]

    QUY TẮC SÁNG TẠO PHONG CÁCH HÌNH ẢNH (PROMPT_ENG):
    - Đa dạng các phong cách: Real photograph, Claymation/Play-Doh, Soft Watercolor, Cute Kawaii/Chibi, Paper cut-out, Crayon drawing, Plushie/Felt toy, 3D Pixar.
    - Cấu trúc: A cute/beautiful <Art Style> of <đối tượng/hành động>, bright vivid colors, clean simple background.
    - Tuyệt đối không dùng dấu ngoặc kép hoặc ký tự đặc biệt trong PROMPT_ENG.

    Ví dụ: 
    - Bé gõ "cat eat mooncake" -> Trả lời: "Trời ơi, chú mèo này sành ăn quá! Mèo đang vui vẻ ôm chiếc bánh trung thu siêu to để phá cỗ cùng em đấy! [PROMPT_ENG: A cute Play-Doh claymation style kitten eating a big mooncake, happy expression, bright colors]"
    - Bé gõ "so o dien" -> Trả lời: "Ôi nguy hiểm lắm bé ơi! Ổ điện có điện giật rất đau, em tuyệt đối không được chạm tay vào nhé! [PROMPT_ENG: A friendly 3D cartoon safety bear warning symbol next to wall socket, educational style for kids]"
    - Bé gõ "nghich lua" -> Trả lời: "Bé ơi, lửa rất nóng và dễ gây bỏng đấy! Chúng mình tuyệt đối không được tự ý chơi với lửa nha! [PROMPT_ENG: A cute 3D Pixar style firefighter puppy wearing a helmet, educational safety concept]"
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

      # Xóa các ký tự nhiễu
      clean_img_prompt = re.sub(r'[*"`]', "", img_prompt).strip()

      # 1. Hiển thị lời giải thích bằng chữ to
      st.markdown(
          f'<div class="big-text">{explanation.strip()}</div>',
          unsafe_allow_html=True,
      )
      st.write("")

      # 2. Mã hóa URL Pollinations với mô hình FLUX
      encoded_prompt = urllib.parse.quote(clean_img_prompt)
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
