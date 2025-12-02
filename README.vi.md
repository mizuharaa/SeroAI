# 🔗 SeroAI — Hệ Thống Phòng Thủ Deepfake Thời Gian Thực

> **Phát hiện deepfake nâng cao được hỗ trợ bởi AI với phân tích pháp y 5 trục, xác minh watermark trực quan và lý luận toàn diện**

---

## 🎯 Tính Năng Công Nghệ Phát Hiện Deepfake Nâng Cao

Hệ thống phát hiện deepfake sẵn sàng cho sản xuất phân tích video và hình ảnh bằng cách sử dụng nhiều trục phát hiện, kết hợp phân tích chuyển động, kiểm tra tính chân thực sinh học, xác minh logic cảnh, phát hiện artifact kết cấu/tần số và xác minh watermark/nguồn gốc nâng cao. Được xây dựng cho các nhóm tin cậy & an toàn, nhà báo và nhà nghiên cứu AI cần kết quả có thể giải thích và chính xác.

---

## 🌐 Có Sẵn Bằng

[**English**](README.md) • [**한국어**](README.ko.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md) • [**Español**](README.es.md) • **Tiếng Việt** (hiện tại) • [**Français**](README.fr.md)

---

## ✨ Tính Năng Chính

### 🎯 **Hệ Thống Phát Hiện 5 Trục**
- **Ổn Định Chuyển Động/Thời Gian** (50% trọng số): Phát hiện sự không nhất quán giữa các khung hình, bất thường luồng quang học và artifact thời gian
- **Tính Chân Thực Sinh Học/Vật Lý** (20% trọng số): Phân tích điểm mốc khuôn mặt, mẫu chớp mắt, tính nhất quán giải phẫu và chuyển động cơ thể
- **Logic Cảnh & Ánh Sáng** (15% trọng số): Xác thực tính bền vững của đối tượng, tính nhất quán vật lý, tính mạch lạc ánh sáng và ranh giới cảnh quay
- **Artifact Kết Cấu & Tần Số** (10% trọng số): Xác định dấu vân tay GAN, mẫu phổ, artifact nén và sự không nhất quán kết cấu
- **Watermark & Nguồn Gốc** (5-50% trọng số): Khớp logo trực quan cho watermark mô hình AI đã xác minh (Sora, Gemini, Pika, Luma, Runway, HeyGen, D-ID)

### 🔍 **Khả Năng Phát Hiện Nâng Cao**
- **Khớp Logo Trực Quan**: Khớp mẫu, khớp tính năng ORB, so sánh biểu đồ và SSIM để phát hiện watermark đã xác minh
- **Lý Luận Toàn Diện**: Kết hợp nhiều tín hiệu yếu một cách thông minh để giảm dương tính giả và tăng độ tin cậy
- **Phát Hiện Không Thể Xảy Ra Ngữ Nghĩa**: Đánh dấu các kịch bản không thể xảy ra về mặt logic (ví dụ: người nổi tiếng đã qua đời trong cảnh quay mới)
- **Điều Chỉnh Trọng Số Động**: Tự động chuyển sang trọng số chủ đạo watermark (50%) khi phát hiện logo AI đã xác minh
- **Cổng Chất Lượng**: Lọc trước phương tiện chất lượng thấp để ngăn dương tính giả

### 🎨 **Giao Diện Web Hiện Đại**
- **React + TypeScript + Vite**: Nhanh, phản hồi và sẵn sàng cho sản xuất
- **Hoạt Hình Framer Motion**: Chuyển tiếp mượt mà và tương tác vi mô
- **Chế Độ Tối/Sáng**: Chuyển đổi chủ đề tự động với phát hiện tùy chọn hệ thống
- **Theo Dõi Tiến Độ Thời Gian Thực**: Cập nhật trực tiếp trong quá trình phân tích với chỉ báo trạng thái theo phương pháp
- **Bảng Kết Quả Chi Tiết**: Phân tích toàn diện với giải thích

### 🛡️ **Sẵn Sàng Cho Sản Xuất**
- **Local-First**: Tất cả xử lý diễn ra trên thiết bị của bạn; không tải lên đám mây
- **Xử Lý Nhanh**: Thời gian chạy điển hình 8-12 giây cho video tiêu chuẩn
- **Ngưỡng Có Thể Cấu Hình**: Ranh giới quyết định có thể điều chỉnh thông qua cấu hình JSON
- **Ghi Nhật Ký Có Cấu Trúc**: Nhật ký JSON với bản ghi phân tích chi tiết
- **Đầu Ra Terminal**: Kết quả phân tích thời gian thực được in ra console

---

## 🚀 Bắt Đầu Nhanh

### Yêu Cầu

- **Python 3.9+** (khuyến nghị 3.10+)
- **Node.js 18+** và npm
- **FFmpeg** (để xử lý video)
- **Tesseract OCR** (tùy chọn, để phát hiện watermark dựa trên văn bản)

### Cài Đặt

```bash
# 1. Clone repository
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2. Tạo và kích hoạt môi trường ảo
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Cài đặt các phụ thuộc Python
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Cài đặt các phụ thuộc frontend
cd webui
npm ci
npm run build
cd ..

# 5. Khởi động server
python app.py
```

Server sẽ khởi động tại `http://localhost:5000`

### Phụ Thuộc Hệ Thống

**Windows (PowerShell)**:
```powershell
winget install ffmpeg
winget install tesseract  # Tùy chọn
```

**macOS**:
```bash
brew install ffmpeg
brew install tesseract  # Tùy chọn
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr  # Tùy chọn
```

---

> **Lưu ý**: Tài liệu này được dịch tự động. Tài liệu đầy đủ sẽ sớm có sẵn. Hiện tại, vui lòng tham khảo phiên bản tiếng Anh: [README.md](README.md)

---

## 📄 Giấy Phép

**MIT** © 2025 Người Đóng Góp SeroAI

Xem tệp `LICENSE` để biết chi tiết.

