# 🎯 MacBook Touch Bar Coding Assistant

A powerful coding assistant that integrates directly with your MacBook Pro Touch Bar, allowing you to ask coding questions and get instant answers from Azure OpenAI.

## ✨ Features

- **🔍 Touch Bar Integration**: Buttons appear directly on your Touch Bar
- **📝 Multiple Input Methods**: Ask, Input, and Quick modes
- **🤖 Azure OpenAI**: Powered by Azure OpenAI for intelligent coding answers
- **💬 Native Dialogs**: Uses macOS native dialogs for seamless experience
- **📋 Copy Functionality**: Easy copying of answers to clipboard
- **⚡ Instant Access**: Click Touch Bar button → Type question → Get answer

## 🚀 Quick Start

### 1. Install MTMR
```bash
# Download MTMR from https://mtmr.app
# Or install via Homebrew
brew install --cask mtmr
```

### 2. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env with your Azure OpenAI credentials
nano .env
```

### 3. Run the Integration
```bash
# Clone the repository
git clone https://github.com/ankushtagore/macbook-touchar.git
cd macbook-touchar

# Install dependencies
pip install -r requirements.txt

# Run Touch Bar integration
python run_touchbar_input.py
```

## 🎯 How to Use

### Touch Bar Buttons

Once running, you'll see these buttons on your Touch Bar:

#### 🔍 Ask Button
- **Click "🔍 Ask"** on Touch Bar
- **Input dialog opens** with text field
- **Type your question** (e.g., "How do I implement a binary search tree?")
- **Click "Ask"** to get answer

#### 📝 Input Button
- **Click "📝 Input"** on Touch Bar
- **Quick input field opens**
- **Type your question**
- **Click "Go"** to get answer

#### 💡 Quick Button
- **Click "💡 Quick"** on Touch Bar
- **Question menu opens** with pre-defined options:
  - "What is a binary search tree?"
  - "How do I implement quicksort?"
  - "Explain dynamic programming"
  - "What is Big O notation?"
  - "How do I reverse a linked list?"
- **Select a question** from the list
- **Get instant answer**

## 🔧 Configuration

### Environment Variables
Create a `.env` file with your Azure OpenAI credentials:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### MTMR Configuration
The integration automatically configures MTMR with the following buttons:
- **🔍 Ask**: Full input dialog
- **📝 Input**: Quick input field
- **💡 Quick**: Pre-defined questions

## 📁 Project Structure

```
macbook-touchar/
├── app/
│   ├── advanced_input_handler.py    # Advanced Touch Bar input handler
│   ├── touchbar_input_handler.py    # Basic Touch Bar input handler
│   ├── azure_service.py             # Azure OpenAI integration
│   ├── config.py                    # Configuration management
│   └── ...                          # Other Touch Bar implementations
├── run_touchbar_input.py            # Main runner script
├── requirements.txt                 # Python dependencies
├── env.example                      # Environment template
└── README.md                        # This file
```

## 🛠️ Available Commands

### Run Everything (Recommended)
```bash
python run_touchbar_input.py
```

### Run Advanced Input (3 Buttons)
```bash
python app/mtmr_advanced_input.py
```

### Run Basic Input (1 Button)
```bash
python app/mtmr_touchbar_input.py
```

### Run Original Integration
```bash
python app/mtmr_integration.py
```

## 🔧 Troubleshooting

### If Buttons Don't Appear:
1. **Right-click Touch Bar** → **Customize Touch Bar**
2. **Look for**: 🔍 Ask, 📝 Input, 💡 Quick
3. **Drag them** to your Touch Bar
4. **Click "Done"**

### If MTMR Not Running:
```bash
open -a MTMR
```

### If Scripts Have Errors:
```bash
# Fix permissions
chmod +x app/*_handler.py

# Test handlers
python app/advanced_input_handler.py quick
```

## 🎯 What You Get

- ✅ **Input Fields**: Appear directly on Touch Bar click
- ✅ **Azure OpenAI**: Integrated for intelligent answers
- ✅ **Multiple Methods**: Ask, Input, and Quick modes
- ✅ **Copy Functionality**: Easy answer copying
- ✅ **Native Experience**: Uses macOS native dialogs
- ✅ **Error Handling**: Robust error handling and recovery

## 🌐 Links

- **MTMR Website**: https://mtmr.app
- **MTMR GitHub**: https://github.com/Toxblh/MTMR
- **Azure OpenAI**: https://azure.microsoft.com/en-us/products/ai-services/openai-service

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⭐ Star This Repository

If you found this project helpful, please give it a star! ⭐

---

**🎉 Your Touch Bar now has a coding assistant! Just run `python run_touchbar_input.py` and start asking coding questions directly from your Touch Bar!** 🎯
