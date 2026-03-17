# Swirl Video Recorder

OpenCV를 활용한 실시간 웹캠 영상 처리 및 녹화 프로그램입니다.
마우스 클릭을 통해 중심을 지정하고, 해당 지점을 기준으로 Swirl(소용돌이) 필터를 적용합니다.

---

## Features

### 1. Recording

![recording](path/to/recording.png)

* 실시간 녹화 상태 표시 (시간 포함)
* 녹화 파일 자동 생성 및 저장

### 2. Swirl (Weak)

![swirl\_weak](path/to/swirl_weak.png)

* 클릭 위치를 중심으로 부드러운 회전 효과
* 시간에 따라 점진적으로 증가하는 회전 강도

### 3. Swirl (Strong)

![swirl\_strong](path/to/swirl_strong.png)

* 더 빠르고 강한 소용돌이 효과
* 확대된 반경과 높은 회전 속도

---

## Tech Stack

* Python 3
* OpenCV (`cv2`)
* NumPy

---

## Installation

```bash
pip install opencv-python numpy
```

---

## Usage

```bash
python swirl_video_recorder.py
```

---

## Controls

![feature\_image](path/to/image.png)

| Key / Action | Description    |
| ------------ | -------------- |
| `r`          | 녹화 시작 / 종료     |
| `ESC`        | 프로그램 종료        |
| 마우스 클릭       | Swirl 중심 위치 지정 |

---

## Output

* 녹화된 영상은 실행 디렉토리에 `.avi` 파일로 저장됩니다.

---

## How It Works

* 마우스 클릭 위치를 중심으로 좌표계를 극좌표계로 변환
* 각 픽셀의 각도(phi)를 시간 기반으로 회전시켜 Swirl 효과 생성
* OpenCV의 `cv.remap()`을 사용한 역방향 매핑 적용
* Letterboxing을 통해 창 크기 변경 시 원본 비율 유지

---

## Notes

* 카메라 FPS는 환경에 따라 다르게 측정될 수 있습니다.
* 일부 코덱(XVID 등)은 시스템에 따라 동작하지 않을 수 있습니다.

---

## Author

서울과학기술대학교 컴퓨터공학과
박재우

---

## License

MIT License
