# ✦ Gemini Cowork

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI](https://img.shields.io/badge/Powered%20By-Google%20Gemini-blue)](https://aistudio.google.com/)

**Gemini Cowork** is a professional, native Windows AI coding assistant that integrates Google's powerful Gemini models directly into your development workflow. It features a stunning Google Material Design 3 interface and deep system integration for file management and command execution.

![Gemini Cowork Screenshot](https://raw.githubusercontent.com/yourusername/GeminiCowork/main/screenshot.png) *(Add your screenshot here)*

## ✨ Key Features

*   🤖 **Intelligent Chat Interface** - Real-time streaming conversations with Google Gemini models.
*   🎨 **Material Design 3 UI** - A premium, modern dark-themed interface inspired by Google's latest design language.
*   📁 **Workspace Awareness** - Add project folders as workspaces so the AI understands your local context.
*   🛠️ **Autonomous Tools** - AI can read, write, search files, and create directories within your workspaces.
*   ⚡ **Smart Shell Integration** - Execute PowerShell commands directly from the chat with a secure approval workflow.
*   🛡️ **Autonomy Modes** - Switch between **Supervised** (ask for every step) and **Autonomous** (auto-run safe actions).
*   💾 **Session Management** - Automatically saves your chat history and configuration.

## 🚀 Installation

### 1. Automatic Install (Recommended)
1. Ensure you have [Python 3.10+](https://www.python.org/downloads/) installed.
2. Download the project and double-click `install.bat`.
3. Launch the app from the created Desktop shortcut.

### 2. Manual Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/GeminiCowork.git
cd GeminiCowork

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## ⚙️ Configuration

1. Obtain your API key from [Google AI Studio](https://aistudio.google.com/).
2. Open the **Settings** dialog in the application.
3. Paste your API key and click **Connect** to fetch available models.
4. Select your preferred model (e.g., `gemini-2.0-flash`) and **Save**.

## 🛡️ Security & Privacy
*   **Approval Workflow**: All destructive actions (file deletion, command execution) require explicit user approval.
*   **Sandboxed Access**: The AI is restricted to the workspace folders you explicitly add.
*   **Local Config**: Your API key is stored securely in your local `%LOCALAPPDATA%` folder, never in the project directory.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
