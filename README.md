# 📷 chessboard-lens-calibrator

OpenCV와 체스보드 패턴을 이용하여 **카메라 캘리브레이션**을 수행하고, 계산된 내부 파라미터와 왜곡 계수를 바탕으로 **렌즈 왜곡 보정**을 수행하는 프로젝트입니다.

---

## ✨ 프로젝트 개요

이 프로젝트의 목표는 다음과 같습니다.

* 🧾 체스보드 패턴을 출력한다.
* 🎥 다양한 시점에서 체스보드 영상을 촬영한다.
* 📌 체스보드 코너를 검출한다.
* 📐 카메라 내부 파라미터와 왜곡 계수를 계산한다.
* 🪄 계산된 결과를 이용해 렌즈 왜곡을 보정한다.
* 🖼️ 보정 전후 결과를 비교한다.

---

## 📁 프로젝트 구조

```text
chessboard-lens-calibrator/
├─ capture_chessboard_video.py
├─ camera_calibration.py
├─ distortion_correction.py
├─ README.md
├─ data/
└─ results/
```

---

## 🛠️ 구현 기능

### 1) 🎥 체스보드 영상 촬영

`capture_chessboard_video.py`

* 웹캠 영상을 촬영
* `Space` 키로 녹화 시작 / 중지
* `ESC` 키로 종료
* `data/chessboard.avi` 파일로 저장
* 화면에 `PREVIEW`, `REC` 상태를 표시하여, 현재 어떤 모드인지 확인 가능

### 2) 📐 카메라 캘리브레이션

`camera_calibration.py`

* 촬영한 `data/chessboard.avi` 영상 입력
* 체스보드 내부 코너 검출
* `cv.cornerSubPix()`를 이용한 코너 정밀화
* `cv.calibrateCamera()`를 이용한 카메라 캘리브레이션 수행
* 결과를 `results/calibration_result.txt`, `results/calibration_data.npz`로 저장

### 3) 🪄 렌즈 왜곡 보정

`distortion_correction.py`

* 저장된 캘리브레이션 결과 불러오기
* `cv.initUndistortRectifyMap()`과 `cv.remap()`을 이용해 왜곡 보정 수행
* 원본 영상과 보정 영상을 나란히(좌우) 비교
* 비교 이미지를 `results/distortion_comparison.jpg`로 저장

---

## ▶️ 실행 방법

### 1. 필요한 라이브러리 설치

```bash
pip install opencv-python numpy
```

### 2. 체스보드 영상 촬영

```bash
python capture_chessboard_video.py
```

### 3. 카메라 캘리브레이션 수행

```bash
python camera_calibration.py
```

### 4. 렌즈 왜곡 보정 수행

```bash
python distortion_correction.py
```

---

## 🧩 체스보드 설정

이번 실험에서는 **종이에 출력한 체스보드**를 사용했습니다.

* 체스보드 칸 개수: `9 x 7`
* 내부 코너 개수: `8 x 6`
* 한 칸 크기: `0.025 m`

따라서 코드에서는 다음과 같이 설정했습니다.

```python
BOARD_PATTERN = (8, 6)
BOARD_CELL_SIZE = 0.025
```

---

## 📊 카메라 캘리브레이션 결과

### ✅ 기본 결과

* 입력 영상: `data/chessboard.avi`
* 체스보드 내부 코너: `(8, 6)`
* 체스보드 한 칸 크기: `0.025 m`
* 유효 프레임 수: `88`
* RMS Error (RMSE): `0.831279`

### ✅ 내부 파라미터

* `fx = 549.467417`
* `fy = 552.685040`
* `cx = 336.847376`
* `cy = 227.611013`

### ✅ Camera Matrix (K)

```text
[[549.467417   0.       336.847376]
 [  0.       552.685040 227.611013]
 [  0.         0.         1.      ]]
```

### ✅ Distortion Coefficients

```text
[ 0.238669 -1.039589 -0.007231  0.002612  1.548612]
```

---

## 🖼️ 데모 이미지

### 1) 📍 체스보드 코너 검출 결과

아래 이미지는 체스보드 내부 코너가 정상적으로 검출된 예시입니다.

![detected_corners_preview](https://github.com/user-attachments/assets/eed0057b-620c-45eb-bbae-9a1a932a1b8b)

### 2) 🔍 왜곡 보정 결과 비교

왼쪽은 원본 영상이고, 오른쪽은 왜곡 보정 후 영상입니다.

![distortion_comparison](https://github.com/user-attachments/assets/7b8be233-4fa3-4984-934c-5ccb4cef57bc)

---

## 🧠 결과 해석

* 📈 유효 프레임 수가 `88장`으로 충분히 확보되었습니다.
* 📉 RMSE가 `0.831279`로 비교적 낮게 나와 캘리브레이션 품질이 개선되었습니다.
* 📏 내부 파라미터 `fx`, `fy`, `cx`, `cy`를 추정할 수 있었습니다.
* 🌀 왜곡 계수를 이용해 원본 영상의 렌즈 왜곡을 보정할 수 있었습니다.

왜곡 보정 전후의 차이는 존재하지만, 사용한 카메라의 왜곡이 매우 강한 편은 아니어서 **극적으로 큰 변화처럼 보이지는 않았습니다**.

---

## ⚠️ 한계점

* 일반 웹캠이나 왜곡이 크지 않은 카메라는 보정 전후 차이가 크게 보이지 않을 수 있습니다.
* 왜곡은 영상 중심보다 **가장자리**에서 더 크게 나타나는 경향이 있으므로, 중심 위주의 장면에서는 차이가 작게 보일 수 있습니다.
* 체스보드가 휘어 있거나 정면에서만 촬영한 영상이 많으면 캘리브레이션 정확도가 떨어질 수 있습니다.
* 광각 카메라를 사용하면 왜곡 보정 효과가 더 뚜렷하게 보일 수 있습니다.

---

## 🔧 사용한 주요 OpenCV 함수

* `cv.VideoCapture()` : 카메라 또는 동영상 입력
* `cv.VideoWriter()` : 동영상 저장
* `cv.findChessboardCorners()` : 체스보드 코너 검출
* `cv.cornerSubPix()` : 코너 위치 정밀화
* `cv.calibrateCamera()` : 카메라 캘리브레이션 수행
* `cv.initUndistortRectifyMap()` : 왜곡 보정용 매핑 생성
* `cv.remap()` : 보정 영상 생성

---

