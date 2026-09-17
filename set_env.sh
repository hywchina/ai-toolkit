#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-${PROJECT_DIR}/.venv}"
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
REQUIREMENTS_FILE="${PROJECT_DIR}/requirements.txt"

if ! command -v uv >/dev/null 2>&1; then
    echo "错误：未找到 uv。请先安装 uv：https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi

if [[ ! -f "${REQUIREMENTS_FILE}" ]]; then
    echo "错误：依赖文件不存在：${REQUIREMENTS_FILE}" >&2
    exit 1
fi

if [[ -e "${VENV_DIR}" && ! -f "${VENV_DIR}/pyvenv.cfg" ]]; then
    echo "错误：${VENV_DIR} 已存在，但不是 Python 虚拟环境。请检查后重试。" >&2
    exit 1
fi

if [[ ! -f "${VENV_DIR}/pyvenv.cfg" ]]; then
    echo "使用 Python ${PYTHON_VERSION} 创建虚拟环境：${VENV_DIR}"
    uv venv --python "${PYTHON_VERSION}" "${VENV_DIR}"
else
    echo "复用已有虚拟环境：${VENV_DIR}"
fi

VENV_PYTHON="${VENV_DIR}/bin/python"
if [[ ! -x "${VENV_PYTHON}" ]]; then
    echo "错误：虚拟环境 Python 不存在：${VENV_PYTHON}" >&2
    exit 1
fi

ACTUAL_VERSION="$("${VENV_PYTHON}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [[ "${ACTUAL_VERSION}" != "${PYTHON_VERSION}" ]]; then
    echo "错误：虚拟环境 Python 版本为 ${ACTUAL_VERSION}，期望 ${PYTHON_VERSION}。" >&2
    echo "如需重建，请先安全移走 ${VENV_DIR}，然后重新运行本脚本。" >&2
    exit 1
fi

echo "同步依赖：${REQUIREMENTS_FILE}"
uv pip sync --python "${VENV_PYTHON}" "${REQUIREMENTS_FILE}"

echo
echo "环境创建完成。"
echo "激活命令：source \"${VENV_DIR}/bin/activate\""
echo "Python：$("${VENV_PYTHON}" --version)"
