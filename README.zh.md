# 🔗 SeroAI — 实时深度伪造防御系统

> **具有5轴取证分析、视觉水印验证和整体推理的高级AI驱动深度伪造检测**

---

## 🎯 高级深度伪造检测技术特点

一个生产就绪的深度伪造检测系统，使用多个检测轴分析视频和图像，结合运动分析、生物真实性检查、场景逻辑验证、纹理/频率伪影检测和高级水印/来源验证。专为需要可解释、准确结果的信任与安全团队、记者和AI研究人员构建。

---

## 🌐 可用语言

[**English**](README.md) • [**한국어**](README.ko.md) • [**日本語**](README.ja.md) • **中文** (当前) • [**Español**](README.es.md) • [**Tiếng Việt**](README.vi.md) • [**Français**](README.fr.md)

---

## ✨ 主要功能

### 🎯 **5轴检测系统**
- **运动/时间稳定性** (50%权重): 检测帧间不一致、光流异常和时间伪影
- **生物/物理真实性** (20%权重): 分析面部 landmarks、眨眼模式、解剖一致性和身体运动
- **场景和光照逻辑** (15%权重): 验证对象持久性、物理一致性、光照一致性和镜头边界
- **纹理和频率伪影** (10%权重): 识别GAN指纹、频谱模式、压缩伪影和纹理不一致
- **水印和来源** (5-50%权重): 用于验证AI模型水印的视觉徽标匹配 (Sora, Gemini, Pika, Luma, Runway, HeyGen, D-ID)

### 🔍 **高级检测功能**
- **视觉徽标匹配**: 用于验证水印检测的模板匹配、ORB特征匹配、直方图比较和SSIM
- **整体推理**: 智能组合多个弱信号以减少误报并提高置信度
- **语义不可能性检测**: 标记逻辑上不可能的场景 (例如，新镜头中已故名人)
- **动态权重调整**: 检测到验证的AI徽标时自动切换到水印主导权重(50%)
- **质量门控**: 预过滤低质量媒体以防止误报

### 🎨 **现代Web界面**
- **React + TypeScript + Vite**: 快速、响应式且生产就绪
- **Framer Motion动画**: 流畅的过渡和微交互
- **深色/浅色模式**: 通过系统偏好检测自动切换主题
- **实时进度跟踪**: 分析期间具有每种方法状态指示器的实时更新
- **详细结果仪表板**: 带有解释的全面分析分解

### 🛡️ **生产就绪**
- **本地优先**: 所有处理都在您的设备上进行；无云上传
- **快速处理**: 标准视频的典型运行时间为8-12秒
- **可配置阈值**: 通过JSON配置可调整的决策边界
- **结构化日志**: 带有详细分析记录的JSON日志
- **终端输出**: 打印到控制台的实时分析结果

---

## 🚀 快速开始

### 先决条件

- **Python 3.9+** (推荐3.10+)
- **Node.js 18+** 和 npm
- **FFmpeg** (用于视频处理)
- **Tesseract OCR** (可选，用于基于文本的水印检测)

### 安装

```bash
# 1. 克隆存储库
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2. 创建并激活虚拟环境
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. 安装Python依赖项
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. 安装前端依赖项
cd webui
npm ci
npm run build
cd ..

# 5. 启动服务器
python app.py
```

服务器将在 `http://localhost:5000` 上启动

### 系统依赖项

**Windows (PowerShell)**:
```powershell
winget install ffmpeg
winget install tesseract  # 可选
```

**macOS**:
```bash
brew install ffmpeg
brew install tesseract  # 可选
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr  # 可选
```

---

> **注意**: 本文档是自动翻译的。完整文档即将推出。目前请参考英文版: [README.md](README.md)

---

## 📄 许可证

**MIT** © 2025 SeroAI贡献者

有关详细信息，请参阅 `LICENSE` 文件。

