# Swirl Video Recorder

OpenCV를 활용한 실시간 웹캠 영상 처리 및 녹화 프로그램입니다.
마우스 클릭을 통해 중심을 지정하고, 해당 지점을 기준으로 시간에 따라 동적으로 반응하는 Swirl(소용돌이) 필터를 적용하여 다이내믹한 영상을 기록할 수 있습니다.

---

## Controls

| Key / Action | Description    |
| ------------ | -------------- |
| `Space` | Preview 모드와 Record 모드 전환 |
| `ESC`        | 프로그램 종료        |
| `r`          | Swirl 모드(OFF -> 약 -> 강) 전환     |
| 마우스 클릭       | Swirl 중심 위치 지정 |

---

## Features

### 1. Recording

![recording](path/to/recording.png)

* 상태 UI 제공: 화면 우측 상단에 실시간 녹화 진행 시간(REC 00:00)과 시스템 시각이 오버레이 됩니다.
* 스마트 자동 저장: 덮어쓰기 방지를 위해 녹화 시작 시점의 타임스탬프를 기반으로 자동 파일명(record_YYYYMMDD_HHMMSS.avi)이 생성되어 실행 디렉토리에 저장됩니다.

### 2. Dynamic Swirl Filter

**Weak Mode**
![swirl\_weak](path/to/swirl_weak.png)

* 클릭 위치를 중심으로 좁은 반경에서 부드럽게 회전합니다.

**Strong Mode**
![swirl\_strong](path/to/swirl_strong.png)

* 빠른 속도와 넓은 반경으로 화면 전체를 강하게 뒤틀어버립니다.


### 3. Auto Letterboxing

[창을 가로로 길게 늘렸을 때 양옆에 검은 레터박스가 생기며 영상 원본 비율이 유지된 이미지.png]

윈도우 창 크기를 마우스로 마음대로 조절해도, 영상이 찌그러지지 않도록 자동으로 검은색 여백(Letterbox)을 생성해 원본 카메라 비율을 완벽히 유지합니다.

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

## Output

* 녹화된 영상은 실행 디렉토리에 `.avi` 파일로 저장됩니다.

---

## How It Works (Core Logic)

단순 내장 함수가 아닌, 컴퓨터 비전의 기하학적 변환 이론을 바탕으로 설계되었습니다.

**비선형 동적 매핑 (Non-linear Dynamic Mapping)**
* 마우스 클릭 위치를 중심으로 픽셀 좌표계를 직교 좌표계에서 극좌표계(Polar Coordinate)로 변환합니다. 중심으로부터의 거리($r$)에 반비례하고, 시간 경과에 비례하는 지수 함수($\exp$)를 사용하여 각도($\phi$)를 회전시킵니다.

**역방향 매핑 (Backward Mapping)을 통한 보간**
* 회전 변환 시 픽셀에 빈 구멍(Black dots)이 생기는 것을 막기 위해, OpenCV의 cv.remap() 함수를 사용하여 도착지 픽셀에서 원본 픽셀의 위치를 역추적하는 역방향 복사를 적용했습니다.

**스마트 좌표 역산 알고리즘**
* 창 크기 변경으로 레터박스(여백)가 발생할 경우, 마우스 클릭 이벤트 좌표가 실제 영상 프레임 좌표와 어긋나는 현상을 방지하기 위해 수학적 스케일링 역변환을 수행합니다.

---

## Notes / Troubleshooting

* FPS 저하 문제: 구형 웹캠이나 PC 환경에 따라 카메라의 원본 FPS가 다르게 측정될 수 있습니다. 영상 처리가 무거울 경우 해상도를 낮추어 테스트해 보세요.

* 코덱 미지원 문제: 운영체제 환경에 따라 XVID 코덱이 지원되지 않아 파일 저장이 안 될 수 있습니다. 이 경우 코드 내의 cv.VideoWriter_fourcc(*'XVID')를 (*'mp4v') 혹은 (*'MJPG') 등으로 변경해 보세요.

---

## Author

서울과학기술대학교 컴퓨터공학과
박재우

---

## License

MIT License
