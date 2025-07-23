# 수동 설치 메뉴얼

# Python 설치
1. Python 설치 파일 다운로드
 - 공식 Python 다운로드 페이지에 접속합니다.
 - "Latest Python 3 Release" 아래의 "Windows installer (64-bit)" 링크를 클릭하여 설치 파일을 다운로드합니다.
2. Python 설치
 - 다운로드한 설치 파일(python-3.x.x-amd64.exe)을 실행합니다.
 - 설치 첫 화면에서 "Add Python 3.x to PATH" 옵션을 반드시 체크합니다.
 - "Install Now" 버튼을 클릭하여 설치를 시작합니다.
 - 설치가 완료되면 "Close"를 눌러 창을 닫습니다.
3. 설치 확인
 - 명령 프롬프트(Win + R → cmd 입력 → Enter)를 엽니다.
 - 아래 명령어를 입력하여 파이썬이 정상적으로 설치되었는지 확인합니다.
 - python --version
 - Python 버전이 출력되면 정상 설치된 것입니다.

# ffmpeg 설치
1. https://ffmpeg.org/download.html 에서 Windows용 zip 파일 다운로드
2. 압축 해제 후 bin 폴더의 경로(예: C:\\ffmpeg\\bin)를 환경 변수 PATH에 추가
3. 명령 프롬프트에서 ffmpeg -version 명령어로 정상 설치 확인

# CUDA Toolkit 설치
1. https://developer.nvidia.com/cuda-downloads 에서 Windows용 CUDA Toolkit 설치 파일 다운로드
2. 설치 프로그램 실행 후 안내에 따라 기본값으로 설치 진행
3. 설치가 완료되면, 명령 프롬프트를 새로 열고 아래 명령어로 정상 설치 여부를 확인 -> nvcc --version

# NVIDIA 그래픽카드 드라이버 설치
1. https://www.nvidia.co.kr/Download/index.aspx?lang=kr 에서 본인 그래픽카드에 맞는 드라이버를 검색 및 다운로드
2. 다운로드한 설치 파일을 실행하여 안내에 따라 설치 진행
3. 설치가 완료되면, 컴퓨터를 재부팅
4. 명령 프롬프트에서 nvidia-smi 명령어로 정상 설치 여부를 확인 (GPU 정보가 출력되면 설치가 완료된 것입니다)