# ffmpeg 설치(윈도우)
1. https://ffmpeg.org/download.html 에서 Windows용 zip 파일 다운로드
2. 압축 해제 후 bin 폴더의 경로(예: C:\\ffmpeg\\bin)를 환경 변수 PATH에 추가
3. 명령 프롬프트에서 ffmpeg -version 명령어로 정상 설치 확인

# CUDA Toolkit 설치(윈도우)
1. https://developer.nvidia.com/cuda-downloads 에서 Windows용 CUDA Toolkit 설치 파일 다운로드
2. 설치 프로그램 실행 후 안내에 따라 기본값으로 설치 진행
3. 설치가 완료되면, 명령 프롬프트를 새로 열고 아래 명령어로 정상 설치 여부를 확인 -> nvcc --version

# NVIDIA 그래픽카드 드라이버 설치(윈도우)
1. https://www.nvidia.co.kr/Download/index.aspx?lang=kr 에서 본인 그래픽카드에 맞는 드라이버를 검색 및 다운로드
2. 다운로드한 설치 파일을 실행하여 안내에 따라 설치 진행
3. 설치가 완료되면, 컴퓨터를 재부팅
4. 명령 프롬프트에서 nvidia-smi 명령어로 정상 설치 여부를 확인 (GPU 정보가 출력되면 설치가 완료된 것입니다)