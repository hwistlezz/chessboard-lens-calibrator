import cv2 as cv
import numpy as np
from pathlib import Path


def draw_outlined_text(img, text, org, color, font_scale=1.0,
                       inner_thickness=2, outer_thickness=5):
    cv.putText(
        img,
        text,
        org,
        cv.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),   # 검정 외곽선
        outer_thickness,
        cv.LINE_AA
    )
    cv.putText(
        img,
        text,
        org,
        cv.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,       # 실제 글자 색
        inner_thickness,
        cv.LINE_AA
    )

# =========================
# User Settings
# =========================
INPUT_VIDEO = "data/chessboard.avi"
CALIBRATION_FILE = "results/calibration_data.npz"
OUTPUT_IMAGE = "results/distortion_comparison.jpg"
OUTPUT_VIDEO = "results/distortion_demo.avi"


def main():
    calibration_path = Path(CALIBRATION_FILE)
    input_video_path = Path(INPUT_VIDEO)
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    # 캘리브레이션 결과 확인
    if not calibration_path.exists():
        print(f"캘리브레이션 결과 파일이 없습니다: {calibration_path}")
        print("먼저 camera_calibration.py를 실행하세요.")
        return

    # 입력 영상 확인
    if not input_video_path.exists():
        print(f"입력 영상 파일이 없습니다: {input_video_path}")
        return

    # 캘리브레이션 데이터 로드
    data = np.load(str(calibration_path))
    K = data["K"]
    dist_coeff = data["dist_coeff"]

    print("========================================")
    print("왜곡 보정 시작")
    print(f"- 입력 영상: {input_video_path}")
    print(f"- 캘리브레이션 파일: {calibration_path}")
    print("Camera Matrix (K):")
    print(K)
    print("Distortion Coefficients:")
    print(dist_coeff.ravel())
    print("========================================")

    video = cv.VideoCapture(str(input_video_path))
    if not video.isOpened():
        print(f"영상 파일을 열 수 없습니다: {input_video_path}")
        return

    fps = video.get(cv.CAP_PROP_FPS)
    if fps <= 0.0:
        fps = 30.0

    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT))

    # 왜곡 보정 맵 생성
    map1, map2 = cv.initUndistortRectifyMap(
        K,
        dist_coeff,
        None,
        K,
        (width, height),
        cv.CV_32FC1
    )

    # 비교 영상 저장용 VideoWriter
    fourcc = cv.VideoWriter_fourcc(*"XVID")
    target = cv.VideoWriter(
        OUTPUT_VIDEO,
        fourcc,
        fps,
        (width * 2, height)
    )

    if not target.isOpened():
        print("출력 동영상 파일을 만들 수 없습니다.")
        video.release()
        return

    frame_index = 0
    saved_preview = False
    show_rectified = True

    print("조작 방법:")
    print("- TAB : 원본/보정 화면 전환")
    print("- S   : 현재 비교 화면 이미지 저장")
    print("- ESC : 종료")

    while True:
        ret, frame = video.read()
        if not ret:
            break

        rectified = cv.remap(frame, map1, map2, interpolation=cv.INTER_LINEAR)

        # 표시용 텍스트 추가
        original_disp = frame.copy()
        rectified_disp = rectified.copy()

        draw_outlined_text(
            original_disp,
            "Original",
            (25, 45),
            (0, 0, 255),  # 빨강
            font_scale=1.0,
            inner_thickness=2,
            outer_thickness=5
        )

        draw_outlined_text(
            rectified_disp,
            "Rectified",
            (25, 45),
            (0, 255, 0),  # 초록
            font_scale=1.0,
            inner_thickness=2,
            outer_thickness=5
        )

        comparison = np.hstack((original_disp, rectified_disp))

        # 첫 프레임 비교 이미지 자동 저장
        if not saved_preview:
            cv.imwrite(OUTPUT_IMAGE, comparison)
            saved_preview = True

        # 비교 영상 저장
        target.write(comparison)

        if show_rectified:
            cv.imshow("Distortion Correction Demo", comparison)
        else:
            cv.imshow("Distortion Correction Demo", original_disp)

        key = cv.waitKey(1)

        if key == 27:  # ESC
            break
        elif key == ord('\t'):  # TAB
            show_rectified = not show_rectified
        elif key == ord('s') or key == ord('S'):
            manual_save_path = results_dir / f"distortion_comparison_frame_{frame_index:04d}.jpg"
            cv.imwrite(str(manual_save_path), comparison)
            print(f"이미지 저장 완료: {manual_save_path}")

        frame_index += 1

    video.release()
    target.release()
    cv.destroyAllWindows()

    print("========================================")
    print("왜곡 보정 결과 저장 완료")
    print(f"- 비교 이미지: {OUTPUT_IMAGE}")
    print(f"- 비교 동영상: {OUTPUT_VIDEO}")
    print("========================================")


if __name__ == "__main__":
    main()