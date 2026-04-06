import cv2 as cv
from pathlib import Path


def main():
    # 저장 폴더 생성
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    output_file = data_dir / "chessboard.avi"

    # 카메라 열기
    video = cv.VideoCapture(0)
    if not video.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    print("카메라가 작동합니다.")

    # 영상 정보 읽기
    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv.CAP_PROP_FPS)

    # FPS를 정상적으로 못 읽어온 경우 대비
    if fps <= 0.0:
        fps = 30.0

    # 저장용 VideoWriter 생성
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    target = cv.VideoWriter(str(output_file), fourcc, fps, (width, height))

    if not target.isOpened():
        print("저장용 동영상 파일을 만들 수 없습니다.")
        video.release()
        return

    is_recording = False

    print("========================================")
    print("체스보드 촬영 안내")
    print("- Space : 녹화 시작/중지")
    print("- ESC   : 종료")
    print("- 체스보드는 평평한 판에 붙여 촬영하세요.")
    print("- 정면만 찍지 말고 좌우/상하로 기울여 촬영하세요.")
    print("- 가까운 거리와 먼 거리 모두 촬영하세요.")
    print("- 화면 중앙뿐 아니라 가장자리 쪽에서도 촬영하세요.")
    print(f"- 저장 파일: {output_file}")
    print("========================================")

    while True:
        ret, frame = video.read()
        if not ret:
            print("프레임을 읽지 못했습니다.")
            break

        # 화면 출력용 프레임
        display_frame = frame.copy()

        # 하단 안내 문구: 검정색 배경 글씨 + 흰색 본문 글씨
        cv.putText(
            display_frame,
            "Space: REC ON/OFF | ESC: Quit",
            (20, height - 20),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            3,
            cv.LINE_AA
        )
        cv.putText(
            display_frame,
            "Space: REC ON/OFF | ESC: Quit",
            (20, height - 20),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv.LINE_AA
        )

        # 상단 안내 문구: 검정색 배경 글씨 + 흰색 본문 글씨
        cv.putText(
            display_frame,
            "Capture chessboard at varied angles and distances",
            (20, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            3,
            cv.LINE_AA
        )
        cv.putText(
            display_frame,
            "Capture chessboard at varied angles and distances",
            (20, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv.LINE_AA
        )

        # 녹화 중이면 파일 저장 + REC 표시
        if is_recording:
            target.write(frame)

            cv.circle(display_frame, (95, 65), 10, (0, 0, 255), -1)

            cv.putText(
                display_frame,
                "REC",
                (20, 75),
                cv.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 0),
                4,
                cv.LINE_AA
            )
            cv.putText(
                display_frame,
                "REC",
                (20, 75),
                cv.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255),
                2,
                cv.LINE_AA
            )
        else:
            cv.putText(
                display_frame,
                "PREVIEW",
                (20, 75),
                cv.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0),
                4,
                cv.LINE_AA
            )
            cv.putText(
                display_frame,
                "PREVIEW",
                (20, 75),
                cv.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
                cv.LINE_AA
            )

        cv.imshow("Chessboard Video Capture", display_frame)

        key = cv.waitKey(1)

        if key == 27:  # ESC
            break
        elif key == ord(' '):  # Space
            is_recording = not is_recording
            if is_recording:
                print("녹화 시작")
            else:
                print("녹화 중지")

    print("카메라를 종료합니다.")
    video.release()
    target.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()