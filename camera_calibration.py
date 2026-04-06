import cv2 as cv
import numpy as np
from pathlib import Path


# =========================
# User Settings
# =========================
VIDEO_FILE = "data/chessboard.avi"

# 체스보드 "내부 코너" 개수 (가로, 세로)
# 예: 체스보드 칸이 9 x 7 이면 내부 코너는 8 x 6
BOARD_PATTERN = (8, 6)

# 체스보드 한 칸의 실제 크기 [meter]
# 예: 2.5 cm = 0.025 m
BOARD_CELL_SIZE = 0.025

# 몇 프레임마다 한 번씩 검사할지
FRAME_STEP = 10

# 최소 성공 프레임 수
MIN_VALID_FRAMES = 8

# 코너 정밀화(cornerSubPix) 종료 조건
SUBPIX_CRITERIA = (
    cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER,
    30,
    0.001,
)


def build_object_points(board_pattern: tuple[int, int], cell_size: float) -> np.ndarray:
    """
    체스보드 평면의 3D 기준점 생성.
    Z=0 평면 위에 있는 점들로 설정.
    """
    objp = np.zeros((board_pattern[0] * board_pattern[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_pattern[0], 0:board_pattern[1]].T.reshape(-1, 2)
    objp *= cell_size
    return objp


def main():
    video_path = Path(VIDEO_FILE)
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    if not video_path.exists():
        print(f"동영상 파일이 존재하지 않습니다: {video_path}")
        return

    video = cv.VideoCapture(str(video_path))
    if not video.isOpened():
        print(f"동영상 파일을 열 수 없습니다: {video_path}")
        return

    objp = build_object_points(BOARD_PATTERN, BOARD_CELL_SIZE)

    obj_points = []   # 3D points in real world
    img_points = []   # 2D points in image plane

    frame_index = 0
    success_count = 0
    image_size = None
    preview_saved = False

    print("========================================")
    print("카메라 캘리브레이션 시작")
    print(f"- 입력 영상: {video_path}")
    print(f"- 체스보드 내부 코너: {BOARD_PATTERN}")
    print(f"- 체스보드 한 칸 크기: {BOARD_CELL_SIZE} m")
    print(f"- 프레임 샘플 간격: {FRAME_STEP}")
    print("========================================")

    while True:
        ret, frame = video.read()
        if not ret:
            break

        if frame_index % FRAME_STEP != 0:
            frame_index += 1
            continue

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        image_size = gray.shape[::-1]  # (width, height)

        found, corners = cv.findChessboardCorners(gray, BOARD_PATTERN, None)

        if found:
            # 코너 위치 정밀화
            corners_refined = cv.cornerSubPix(
                gray,
                corners,
                winSize=(11, 11),
                zeroZone=(-1, -1),
                criteria=SUBPIX_CRITERIA,
            )

            obj_points.append(objp.copy())
            img_points.append(corners_refined)
            success_count += 1

            # 검출 결과 그리기
            preview = frame.copy()
            cv.drawChessboardCorners(preview, BOARD_PATTERN, corners_refined, found)

            # 첫 성공 프레임 미리보기 저장
            if not preview_saved:
                preview_path = results_dir / "detected_corners_preview.jpg"
                cv.imwrite(str(preview_path), preview)
                preview_saved = True

            print(f"[성공] frame {frame_index:04d} -> 누적 성공 프레임 수: {success_count}")

        frame_index += 1

    video.release()

    print("========================================")
    print(f"총 성공 프레임 수: {success_count}")
    print("========================================")

    if success_count < MIN_VALID_FRAMES:
        print("유효한 체스보드 프레임 수가 너무 적습니다.")
        print(f"최소 {MIN_VALID_FRAMES}장 이상 필요합니다.")
        print("다음을 확인하세요:")
        print("1. BOARD_PATTERN이 실제 체스보드 내부 코너 수와 맞는지")
        print("2. 체스보드가 영상에서 너무 작거나 흐리지 않은지")
        print("3. 정면뿐 아니라 다양한 각도로 촬영했는지")
        return

    # 캘리브레이션 수행
    rms, K, dist_coeff, rvecs, tvecs = cv.calibrateCamera(
        obj_points,
        img_points,
        image_size,
        None,
        None
    )

    fx = K[0, 0]
    fy = K[1, 1]
    cx = K[0, 2]
    cy = K[1, 2]

    print("\n========== Calibration Result ==========")
    print(f"RMS Error (RMSE): {rms:.6f}")
    print(f"fx = {fx:.6f}")
    print(f"fy = {fy:.6f}")
    print(f"cx = {cx:.6f}")
    print(f"cy = {cy:.6f}")
    print("Camera Matrix (K):")
    print(K)
    print("Distortion Coefficients:")
    print(dist_coeff.ravel())
    print("========================================")

    # npz 파일로 저장 (다음 distortion_correction.py에서 사용)
    npz_path = results_dir / "calibration_data.npz"
    np.savez(
        npz_path,
        rms=rms,
        K=K,
        dist_coeff=dist_coeff,
        image_width=image_size[0],
        image_height=image_size[1],
        board_pattern=np.array(BOARD_PATTERN),
        board_cell_size=BOARD_CELL_SIZE,
    )

    # txt 파일로도 저장 (README 작성용 복붙 편하게)
    txt_path = results_dir / "calibration_result.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=== Camera Calibration Results ===\n")
        f.write(f"Input video: {video_path}\n")
        f.write(f"Board pattern (inner corners): {BOARD_PATTERN}\n")
        f.write(f"Board cell size: {BOARD_CELL_SIZE} m\n")
        f.write(f"Valid frames: {success_count}\n")
        f.write(f"RMS Error (RMSE): {rms:.6f}\n\n")

        f.write("Camera Matrix (K):\n")
        f.write(np.array2string(K, precision=6, suppress_small=False))
        f.write("\n\n")

        f.write("Distortion Coefficients:\n")
        f.write(np.array2string(dist_coeff.ravel(), precision=6, suppress_small=False))
        f.write("\n\n")

        f.write(f"fx: {fx:.6f}\n")
        f.write(f"fy: {fy:.6f}\n")
        f.write(f"cx: {cx:.6f}\n")
        f.write(f"cy: {cy:.6f}\n")

    print(f"캘리브레이션 결과 저장 완료:")
    print(f"- {npz_path}")
    print(f"- {txt_path}")
    if preview_saved:
        print(f"- results/detected_corners_preview.jpg")


if __name__ == "__main__":
    main()