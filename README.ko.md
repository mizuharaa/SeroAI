# 🔗 SeroAI — 실시간 딥페이크 방어 시스템

> **5축 포렌식 분석, 시각적 워터마크 검증, 통합 추론을 갖춘 고급 AI 기반 딥페이크 탐지**

---

## 🎯 고급 딥페이크 탐지 기술 특징

다중 탐지 축을 사용하여 비디오와 이미지를 분석하는 프로덕션 준비 딥페이크 탐지 시스템으로, 모션 분석, 생물학적 현실성 검사, 장면 논리 검증, 텍스처/주파수 아티팩트 탐지, 고급 워터마크/출처 검증을 결합합니다. 설명 가능하고 정확한 결과가 필요한 신뢰 및 안전 팀, 언론인, AI 연구자를 위해 구축되었습니다.

---

## 🌐 사용 가능한 언어

[**English**](README.md) • **한국어** (현재) • [**日本語**](README.ja.md) • [**中文**](README.zh.md) • [**Español**](README.es.md) • [**Tiếng Việt**](README.vi.md) • [**Français**](README.fr.md)

---

## ✨ 주요 기능

### 🎯 **5축 탐지 시스템**
- **모션/시간적 안정성** (50% 가중치): 프레임 간 불일치, 광학 흐름 이상, 시간적 아티팩트 탐지
- **생물학적/물리적 현실성** (20% 가중치): 얼굴 랜드마크, 깜빡임 패턴, 해부학적 일관성, 신체 움직임 분석
- **장면 및 조명 논리** (15% 가중치): 객체 지속성, 물리 일관성, 조명 일관성, 촬영 경계 검증
- **텍스처 및 주파수 아티팩트** (10% 가중치): GAN 지문, 스펙트럼 패턴, 압축 아티팩트, 텍스처 불일치 식별
- **워터마크 및 출처** (5-50% 가중치): 검증된 AI 모델 워터마크를 위한 시각적 로고 매칭 (Sora, Gemini, Pika, Luma, Runway, HeyGen, D-ID)

### 🔍 **고급 탐지 기능**
- **시각적 로고 매칭**: 검증된 워터마크 탐지를 위한 템플릿 매칭, ORB 기능 매칭, 히스토그램 비교, SSIM
- **통합 추론**: 여러 약한 신호를 지능적으로 결합하여 오탐을 줄이고 신뢰도 향상
- **의미론적 불가능성 탐지**: 논리적으로 불가능한 시나리오 플래그 (예: 새로운 영상에서 사망한 유명인)
- **동적 가중치 조정**: 검증된 AI 로고가 탐지되면 워터마크 중심 가중치(50%)로 자동 전환
- **품질 게이트**: 오탐을 방지하기 위해 저품질 미디어를 사전 필터링

### 🎨 **현대적인 웹 인터페이스**
- **React + TypeScript + Vite**: 빠르고 반응형이며 프로덕션 준비 완료
- **Framer Motion 애니메이션**: 부드러운 전환 및 마이크로 인터랙션
- **다크/라이트 모드**: 시스템 기본 설정 감지로 자동 테마 전환
- **실시간 진행 추적**: 방법별 상태 표시기가 있는 분석 중 라이브 업데이트
- **상세 결과 대시보드**: 설명이 포함된 포괄적인 분석 분석

### 🛡️ **프로덕션 준비 완료**
- **로컬 우선**: 모든 처리가 기기에서 수행됩니다. 클라우드 업로드 없음
- **빠른 처리**: 표준 비디오의 경우 일반적으로 8-12초 실행 시간
- **구성 가능한 임계값**: JSON 구성으로 조정 가능한 결정 경계
- **구조화된 로깅**: 상세 분석 기록이 있는 JSON 로그
- **터미널 출력**: 콘솔에 인쇄되는 실시간 분석 결과

---

## 🚀 빠른 시작

### 사전 요구 사항

- **Python 3.9+** (3.10+ 권장)
- **Node.js 18+** 및 npm
- **FFmpeg** (비디오 처리용)
- **Tesseract OCR** (선택 사항, 텍스트 기반 워터마크 탐지용)

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2. 가상 환경 생성 및 활성화
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Python 종속성 설치
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. 프론트엔드 종속성 설치
cd webui
npm ci
npm run build
cd ..

# 5. 서버 시작
python app.py
```

서버는 `http://localhost:5000`에서 시작됩니다.

### 시스템 종속성

**Windows (PowerShell)**:
```powershell
winget install ffmpeg
winget install tesseract  # 선택 사항
```

**macOS**:
```bash
brew install ffmpeg
brew install tesseract  # 선택 사항
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr  # 선택 사항
```

---

> **참고**: 이 문서는 자동 번역되었습니다. 전체 문서는 곧 제공될 예정입니다. 현재는 영어 버전을 참조하세요: [README.md](README.md)

---

## 📄 라이선스

**MIT** © 2025 SeroAI 기여자

자세한 내용은 `LICENSE` 파일을 참조하세요.

