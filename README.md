# 🎯 POC Outreach Workflow

A complete B2B outreach automation system that discovers ideal companies, finds decision makers, and sends personalized emails using AI.

## ✨ Features

- **🔍 ICP-Based Company Discovery**: Find companies matching your Ideal Customer Profile using Crust Data
- **👥 Decision Maker Identification**: Automatically discover top 5 decision makers for each company
- **📧 AI-Powered Personalized Emails**: Generate and send personalized outreach emails using Claude AI
- **🎯 Smart Scoring**: Rank companies by ICP fit score
- **💡 Custom Product Vision**: Personalize emails with your specific product/service offering

## 🏗️ Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ Crust Data API
                          ↓
              Claude AI + SendGrid Email Delivery
```

## 🚀 Quick Start

### Prerequisites

- Python 3.13+ 
- Node.js 18+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/Viren-55/crust-c.git
cd crust-c
```

### 2. Environment Setup

Create `.env` file in the root directory:

```bash
# Crust Data API Credentials
CRUST_EMAIL=your_crust_email@example.com
CRUST_PASSWORD=your_crust_password
CRUST_API_TOKEN=your_crust_api_token
CRUST_API_BASE_URL=https://api.crustdata.com

# AI & Email Configuration
CLAUDE_API_KEY=your_claude_api_key
SENDER_EMAIL=your_sender_email@example.com
SENDGRID_API_KEY=your_sendgrid_api_key
```

### 3. Quick Start (Recommended)

Use the automated startup script:

```bash
# Make script executable and run
chmod +x start_servers.sh
./start_servers.sh
```

This will:
- Create virtual environment if needed
- Install all dependencies
- Start both backend and frontend servers
- Show you the URLs to access

**Or manual setup:**

### 4. Manual Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r poc-backend/requirements.txt

# Start backend server
cd poc-backend
python main.py
```

Backend will start at: **http://localhost:8000**

### 5. Manual Frontend Setup

Open a new terminal:

```bash
cd poc-frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will start at: **http://localhost:3000**

## 🎮 Usage

### Step 1: Define Product Vision
- Enter what you're selling (e.g., "HR management software", "Healthcare diagnostic tools")
- This will be used to personalize your outreach emails

### Step 2: Set ICP Criteria
- **Industries**: Select target industries
- **Revenue Range**: Set minimum and maximum annual revenue
- **Headcount Range**: Define employee count range

### Step 3: Discover Companies
- Click "🔍 Find Companies"
- System searches Crust Data and returns ranked results

### Step 4: Find Decision Makers
- Click "👥 View Decision Makers" on any company
- System finds top 5 decision makers with contact details

### Step 5: Send Personalized Emails
- Click "📧 Send Email" for any decision maker
- AI generates personalized email content
- Email sent via SendGrid

## 📁 Project Structure

```
crust-c/
├── README.md                          # This file
├── start_servers.sh                   # Automated startup script
├── .env                               # Environment variables
├── personlized_email_sender.py        # Email generation script
├── poc-backend/                       # FastAPI backend
│   ├── main.py                        # Main API server
│   ├── models.py                      # Data models
│   ├── crust_service.py               # Crust Data integration
│   ├── people_service.py              # People search service
│   ├── scoring_service.py             # Company scoring logic
│   └── requirements.txt               # Python dependencies
├── poc-frontend/                      # React frontend
│   ├── src/
│   │   ├── SimpleApp.tsx              # Main app component
│   │   ├── api.ts                     # API client
│   │   └── ...
│   └── package.json                   # Node dependencies
├── docs/                              # Documentation files
├── data/                              # API response samples
└── venv/                              # Python virtual environment
```

## 🔧 API Endpoints

### Company Discovery
- `POST /search-companies` - Search companies by ICP criteria
- `GET /company/{domain}` - Get company details
- `GET /company/{domain}/people` - Get decision makers

### Email Outreach
- `POST /send-email` - Send personalized email

### Health Check
- `GET /health` - API health status

## 🧪 Testing

### Test Email Functionality
```bash
curl -X POST http://localhost:8000/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "test@example.com",
    "recipient_name": "Test User",
    "recipient_title": "CEO", 
    "company_name": "Test Company",
    "product_vision": "Revolutionary HR software"
  }'
```

### Test Company Search
```bash
curl -X POST http://localhost:8000/search-companies \
  -H "Content-Type: application/json" \
  -d '{
    "industries": ["Technology"],
    "revenue_min": 1000000,
    "revenue_max": 100000000,
    "headcount_min": 50,
    "headcount_max": 1000
  }'
```

## 🛠️ Troubleshooting

### Backend Issues
- **Import errors**: Make sure virtual environment is activated
- **API key errors**: Check `.env` file configuration
- **Port conflicts**: Change port in `main.py` if needed

### Frontend Issues
- **Connection refused**: Ensure backend is running on port 8000
- **Module not found**: Run `npm install` in poc-frontend directory

### Email Issues
- **SendGrid 401**: Verify SendGrid API key is valid
- **Email not delivered**: Check SendGrid dashboard for delivery status

## 🔑 Required API Keys

1. **Crust Data**: Sign up at [crustdata.com](https://crustdata.com)
2. **Claude AI**: Get API key from [console.anthropic.com](https://console.anthropic.com)
3. **SendGrid**: Create account at [sendgrid.com](https://sendgrid.com)

## 📊 Monitoring

Backend logs show:
- Company discovery results
- Decision maker search results  
- Generated email content
- Email delivery status

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Open GitHub issue
- Check backend logs at `http://localhost:8000/docs` for API documentation

---

🚀 **Ready to transform your B2B outreach process!** Start by setting up your environment variables and running both servers.