# 🚀 Hugo AI Studio

**Create beautiful websites with AI through simple chat interface**

Hugo AI Studio is a modern web application that lets users create complete websites by simply describing what they want in natural language. The AI analyzes the description and generates a fully functional Hugo website with custom content.

## ✨ Features

- **💬 Simple Chat Interface** - Just describe what website you want
- **🤖 AI-Powered Creation** - Uses Ollama LLM to understand and create
- **🌐 Instant Preview** - See your website immediately
- **📥 Download Ready** - Get complete website files as ZIP
- **💾 Database Storage** - All websites stored persistently
- **🐳 Docker Containerized** - Easy deployment and scaling

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Chat    │    │  FastAPI + AI   │    │   Ollama LLM    │
│   Port: 3001    │◄──►│   Port: 8000    │◄──►│  Port: 11434    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
         ┌─────────────────┐    ┌─────────────────┐
         │  SQLite DB      │    │     Nginx       │
         │  (Persistent)   │    │   Port: 8080    │
         └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB+ RAM (for Ollama LLM)
- Internet connection (for initial setup)

### 1. Clone Repository
```bash
git clone https://github.com/your-username/hugo-ai-studio.git
cd hugo-ai-studio
```

### 2. Start Services
```bash
docker-compose -f compose.yml up -d
```

### 3. Download AI Model
```bash
docker exec hugo-ai-studio-ollama-1 ollama pull llama3.2
```

### 4. Access Application
- **Chat Interface**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs
- **Generated Sites**: http://localhost:8080/sites/{site-id}/

## 💬 How to Use

1. **Open the chat interface** at http://localhost:3001
2. **Describe your website** in natural language:
   - "Create a tech blog about artificial intelligence"
   - "Build a portfolio website for a photographer"
   - "Make a business website for a coffee shop"
3. **Wait for AI to create** your website (30-60 seconds)
4. **Preview your site** using the provided link
5. **Download ZIP file** with all website files

## 📁 Project Structure

```
hugo-ai-studio/
├── frontend/                 # React Chat Interface
│   ├── src/
│   │   ├── App.js           # Main chat component
│   │   └── index.js         # React entry point
│   ├── public/
│   │   └── index.html       # HTML template
│   ├── package.json         # Dependencies
│   └── Dockerfile           # Frontend container
├── backend/                  # FastAPI Backend
│   ├── main.py              # API endpoints & AI logic
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container
├── compose.yml              # Docker Compose configuration
├── nginx.conf               # Nginx configuration
├── data/                    # SQLite database storage
├── generated-sites/         # Generated website files
└── ollama-data/            # LLM model storage
```

## 🔧 Configuration

### Environment Variables
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)
- `OLLAMA_URL`: Ollama service URL (default: http://ollama:11434)
- `DATABASE_PATH`: SQLite database path (default: /app/data/sites.db)

### Port Configuration
- **3001**: React Frontend (Chat Interface)
- **8000**: FastAPI Backend (API)
- **8080**: Nginx (Generated Sites)
- **11434**: Ollama (LLM Service)

## 🛠️ Development

### Local Development Setup
```bash
# Frontend
cd frontend
npm install
npm start

# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Ollama (separate terminal)
ollama serve
ollama pull llama3.2
```

### API Endpoints
- `GET /health` - Health check
- `POST /api/create-website` - Create website from description
- `GET /api/download/{site_id}` - Download website ZIP

## 🎯 Example Requests

### Tech Blog
```
"Create a tech blog about artificial intelligence and machine learning with posts about recent developments"
```

### Portfolio Website
```
"Build a portfolio website for a graphic designer showcasing creative work and client testimonials"
```

### Business Website
```
"Make a professional website for a local coffee shop with menu, location, and contact information"
```

## 🔍 Troubleshooting

### Services Not Starting
```bash
# Check service status
docker-compose -f compose.yml ps

# View logs
docker-compose -f compose.yml logs frontend
docker-compose -f compose.yml logs backend
```

### AI Model Issues
```bash
# Verify model is downloaded
docker exec hugo-ai-studio-ollama-1 ollama list

# Re-download model
docker exec hugo-ai-studio-ollama-1 ollama pull llama3.2
```

### Port Conflicts
```bash
# Stop all services
docker-compose -f compose.yml down

# Check port usage
netstat -tulpn | grep :3001
```

## 📊 System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB for models and generated sites
- **Network**: Internet connection for initial setup

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugo** - Static site generator
- **Ollama** - Local LLM inference
- **React** - Frontend framework
- **FastAPI** - Backend framework
- **Docker** - Containerization

---

**Made with ❤️ for easy website creation**