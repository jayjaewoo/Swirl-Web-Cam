"""
[Video Recorder with Swirl Filter]
OpenCV를 활용한 웹캠 영상 녹화 및 실시간 기하학적 변환(Swirl) 프로그램

Features:
- 웹캠 실시간 렌더링 및 동영상(AVI) 녹화 기능
- 마우스 콜백 및 역방향 매핑을 활용한 동적 소용돌이(Swirl) 필터 구현
- 창 크기 조절 시 원본 비율을 강제로 유지하는 Letterboxing 알고리즘 적용
- 객체 지향(OOP) 설계를 통한 모듈화 및 상태 관리 최적화
"""

import cv2 as cv
import numpy as np
from datetime import datetime
import time


class SwirlVideoRecorder:
    def __init__(self, cam_index=0):
        """카메라 초기화 및 프로그램 상태 변수 설정"""
        self.cap = cv.VideoCapture(cam_index)
        if not self.cap.isOpened():
            raise RuntimeError("카메라를 열 수 없습니다. 웹캠 연결을 확인해주세요.")

        # 카메라 원본 해상도 및 FPS
        self.w = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.h = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        if self.fps <= 0 or np.isnan(self.fps):
            self.fps = 30.0

        self.win_name = 'Video Recorder - Swirl Filter'

        # 녹화 관련 상태
        self.is_recording = False
        self.out = None
        self.recording_start_time = 0

        # 필터 관련 상태
        self.mode = 0  # 0: OFF, 1: Weak, 2: Strong
        self.swirl_active = False  # 클릭되어 활성화된 상태인지 여부
        self.cx = self.w // 2
        self.cy = self.h // 2
        self.filter_start_time = 0

        # 필터 연산 최적화를 위한 맵핑 캐시
        self.r_map = None
        self.phi_map = None
        self.update_needed = False

        # 화면 전체 픽셀 좌표 그리드 사전 생성 (연산 속도 향상)
        self.X_grid, self.Y_grid = np.meshgrid(np.arange(self.w), np.arange(self.h))

        # 윈도우 크기 상태 (비율 유지 계산용)
        self.win_w = self.w
        self.win_h = self.h

        # 윈도우 생성 및 마우스 콜백 등록
        cv.namedWindow(self.win_name, cv.WINDOW_NORMAL)
        cv.setMouseCallback(self.win_name, self._mouse_handler)

    def _mouse_handler(self, event, x, y, flags, param):
        """마우스 클릭 이벤트 처리 및 좌표 역변환 (Letterbox 보정)"""
        if event == cv.EVENT_LBUTTONDOWN and self.mode > 0:
            aspect_ratio = self.w / self.h

            # 창 크기 변경에 따른 클릭 좌표를 원본 해상도 비율로 역변환
            if self.win_w > 0 and self.win_h > 0:
                if self.win_w / self.win_h > aspect_ratio:
                    new_h = self.win_h
                    new_w = int(new_h * aspect_ratio)
                else:
                    new_w = self.win_w
                    new_h = int(new_w / aspect_ratio)

                x_off = (self.win_w - new_w) // 2
                y_off = (self.win_h - new_h) // 2

                mapped_x = int((x - x_off) * (self.w / new_w))
                mapped_y = int((y - y_off) * (self.h / new_h))

                self.cx = max(0, min(self.w - 1, mapped_x))
                self.cy = max(0, min(self.h - 1, mapped_y))
            else:
                self.cx = x
                self.cy = y

            # 클릭 시점부터 소용돌이 활성화
            self.swirl_active = True
            self.filter_start_time = time.time()
            self.update_needed = True

    def _apply_swirl_filter(self, frame):
        """역방향 매핑(Backward Mapping)을 활용한 기하학적 소용돌이 필터 적용"""
        if not (self.swirl_active and self.mode > 0):
            return frame

        # 클릭 위치가 갱신되었을 때만 반경 및 각도 맵을 다시 계산
        if self.update_needed:
            dX = self.X_grid - self.cx
            dY = self.Y_grid - self.cy
            self.r_map = np.sqrt(dX ** 2 + dY ** 2)
            self.phi_map = np.arctan2(dY, dX)
            self.update_needed = False

        elapsed = time.time() - self.filter_start_time

        # 모드별 파라미터 차별화
        if self.mode == 1:
            radius = max(1.0, elapsed * 150.0)
            strength = elapsed * 4.0
        else:
            radius = max(1.0, elapsed * 350.0)
            strength = elapsed * 12.0

        # 비선형 함수를 적용하여 중심일수록 꼬임이 강해지도록 각도 계산
        theta_offset = strength * np.exp(-self.r_map / radius)
        new_phi = self.phi_map + theta_offset

        # 극좌표를 직교좌표로 재변환
        map_x = (self.cx + self.r_map * np.cos(new_phi)).astype(np.float32)
        map_y = (self.cy + self.r_map * np.sin(new_phi)).astype(np.float32)

        # 빈 공간 없이 리매핑
        return cv.remap(frame, map_x, map_y, cv.INTER_LINEAR)

    def _draw_overlay_ui(self, frame):
        """화면에 출력될 UI 텍스트 및 오버레이 렌더링"""
        now = datetime.now()

        # 1. 필터 모드 표시
        if self.mode > 0:
            mode_str = "Weak" if self.mode == 1 else "Strong"
            text = f"@ Swirl Mode ({mode_str} - Click!)"
            color = (0, 255, 255) if self.mode == 1 else (0, 100, 255)

            # 그림자 효과 (검은 텍스트 위에 덮어쓰기)
            cv.putText(frame, text, (20, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3)
            cv.putText(frame, text, (20, 40), cv.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # 2. 녹화 상태 및 경과 시간 표시
        if self.is_recording:
            cv.circle(frame, (self.w - 50, 50), 15, (0, 0, 255), -1)

            elapsed_time = time.time() - self.recording_start_time
            m, s = divmod(int(elapsed_time), 60)
            rec_str = f"REC {m:02d}:{s:02d}"

            cv.putText(frame, rec_str, (self.w - 180, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv.putText(frame, rec_str, (self.w - 180, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # 3. 현재 시간 표시
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        cv.putText(frame, time_str, (self.w - 220, 90), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        cv.putText(frame, time_str, (self.w - 220, 90), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    def _apply_letterbox(self, frame):
        """창 크기가 원본 비율과 다를 때 검은색 여백(Letterbox)을 추가하여 비율 강제 유지"""
        try:
            rect = cv.getWindowImageRect(self.win_name)
            if rect is not None and len(rect) == 4:
                win_x, win_y, win_w, win_h = rect
                if win_w > 0 and win_h > 0:
                    self.win_w, self.win_h = win_w, win_h
                    aspect_ratio = self.w / self.h

                    if win_w / win_h > aspect_ratio:
                        new_h = win_h
                        new_w = int(new_h * aspect_ratio)
                    else:
                        new_w = win_w
                        new_h = int(new_w / aspect_ratio)

                    if new_w != self.w or new_h != self.h:
                        resized = cv.resize(frame, (new_w, new_h))
                        letterbox = np.zeros((win_h, win_w, 3), dtype=np.uint8)

                        x_off = (win_w - new_w) // 2
                        y_off = (win_h - new_h) // 2

                        letterbox[y_off:y_off + new_h, x_off:x_off + new_w] = resized
                        return letterbox
        except Exception:
            pass
        return frame

    def toggle_recording(self):
        """녹화 상태 전환 및 VideoWriter 제어"""
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.recording_start_time = time.time()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"record_{timestamp}.avi"
            fourcc = cv.VideoWriter_fourcc(*'XVID')

            self.out = cv.VideoWriter(filename, fourcc, self.fps, (self.w, self.h))
            print(f"[알림] 동영상 녹화 시작: {filename}")
        else:
            if self.out is not None:
                self.out.release()
                self.out = None
            print("[알림] 녹화 중지 및 파일 저장 완료")

    def toggle_mode(self):
        """소용돌이 필터 모드 전환"""
        self.mode = (self.mode + 1) % 3
        if self.mode == 0:
            self.swirl_active = False
            print("[필터] 소용돌이 모드: OFF")
        elif self.mode == 1:
            print("[필터] 소용돌이 모드: Weak (약한 회전)")
        elif self.mode == 2:
            print("[필터] 소용돌이 모드: Strong (강한 회전)")

    def run(self):
        """메인 프로그램 실행 루프"""
        print("=" * 50)
        print(" OpenCV Video Recorder ".center(50, "="))
        print("=" * 50)
        print(" [Space] : 녹화 시작 / 중지")
        print(" [R 키]  : 소용돌이 모드 변경 (OFF -> Weak -> Strong)")
        print(" [좌클릭]: 소용돌이 발생 (필터 활성화 시)")
        print(" [ESC]   : 프로그램 종료")
        print("=" * 50)

        while True:
            valid, frame = self.cap.read()
            if not valid:
                break

            # 창 닫기 버튼 클릭 확인
            if cv.getWindowProperty(self.win_name, cv.WND_PROP_VISIBLE) < 1:
                break

            # 1. 기하학적 필터 적용
            frame = self._apply_swirl_filter(frame)

            # 2. 동영상 저장용 원본 비율 프레임 기록
            if self.is_recording and self.out is not None:
                self.out.write(frame)

            # 3. 화면 표시용 UI 오버레이
            display_frame = frame.copy()
            display_frame = self._draw_overlay_ui(display_frame)

            # 4. 비율 유지(Letterbox) 적용 후 최종 화면 출력
            display_frame = self._apply_letterbox(display_frame)
            cv.imshow(self.win_name, display_frame)

            # 5. 키보드 이벤트 처리
            wait_msec = int(1 / self.fps * 1000)
            key = cv.waitKey(wait_msec)

            if key == 27:  # ESC
                break
            elif key == ord(' '):
                self.toggle_recording()
            elif key == ord('r') or key == ord('R'):
                self.toggle_mode()

        self.cleanup()

    def cleanup(self):
        """프로그램 종료 시 자원 안전 해제"""
        self.cap.release()
        if self.out is not None:
            self.out.release()
        cv.destroyAllWindows()
        print("[알림] 프로그램을 정상적으로 종료합니다.")


if __name__ == "__main__":
    try:
        recorder = SwirlVideoRecorder()
        recorder.run()
    except Exception as e:
        print(f"오류 발생: {e}")
