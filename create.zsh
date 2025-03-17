#!/bin/zsh

# build.zsh
WORKFLOW_NAME="alfred-gitmoji"
TEMP_DIR="alfredscript"
SCRIPT_TYPE="py"  # 기본값은 py

# 커맨드 라인 인자 처리
if [[ $1 == "--py" ]]; then
    SCRIPT_TYPE="py"
    echo "📝 Using Python script version..."
elif [[ $1 == "--zsh" ]]; then
    SCRIPT_TYPE="zsh"
    echo "📝 Using Zsh script version..."
elif [[ -n $1 ]]; then
    echo "❌ Invalid argument: $1"
    echo "Usage: ./create.zsh [--py|--zsh]"
    echo "  --py  : Create workflow with Python script (default)"
    echo "  --zsh : Create workflow with Zsh script"
    exit 1
fi

echo "🚀 Building Alfred workflow..."

# 1. 임시 디렉토리 생성
echo "📁 Creating directory structure..."
mkdir -p ${TEMP_DIR}

# 2. 스크립트 파일 복사
echo "📝 Copying workflow script..."
if [[ $SCRIPT_TYPE == "py" ]]; then
    cp src/workflowscript.py ${TEMP_DIR}/workflowscript.py || {
        echo "❌ Failed to copy Python workflow script"
        exit 1
    }
else
    cp src/workflowscript.zsh ${TEMP_DIR}/workflowscript.zsh || {
        echo "❌ Failed to copy Zsh workflow script"
        exit 1
    }
fi

# 3. 아이콘 파일 복사
echo "🎨 Copying icon..."
cp src/icon.png ${TEMP_DIR}/icon.png || {
    echo "❌ Failed to copy icon"
    exit 1
}

# 4. plist 파일 복사
echo "📋 Copying info.plist..."
if [[ $SCRIPT_TYPE == "py" ]]; then
    cp src/info-py.plist ${TEMP_DIR}/info.plist || {
        echo "❌ Failed to copy info.plist"
        exit 1
    }
else
    cp src/info-zsh.plist ${TEMP_DIR}/info.plist || {
        echo "❌ Failed to copy info.plist"
        exit 1
    }
fi


# 5. 워크플로우 생성을 위해 디렉토리 이동
echo "📦 Creating workflow package..."
cd ${TEMP_DIR} || {
    echo "❌ Failed to change directory"
    exit 1
}

# 6. workflow 파일 생성
zip -r ../${WORKFLOW_NAME}.alfredworkflow . || {
    echo "❌ Failed to create workflow package"
    cd ..
    rm -rf ${TEMP_DIR}
    exit 1
}

# 7. 상위 디렉토리로 이동
cd ..

# 8. 임시 디렉토리 삭제
echo "🧹 Cleaning up..."
rm -rf ${TEMP_DIR}

echo "✅ Workflow built successfully!"
echo "📎 Created: ${WORKFLOW_NAME}.alfredworkflow"
