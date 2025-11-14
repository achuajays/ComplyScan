# Quick Start Guide

## Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up LongCat API (optional but recommended):**
   - Get your API key from https://api.longcat.chat
   - Create a `.env` file in the `backend` folder:
     ```
     LONGCAT_API_KEY=your_api_key_here
     ```
   - If you don't set this, the API will work but won't provide AI recommendations

3. **Start the backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`

4. **Test the API:**
   - Visit `http://localhost:8000/docs` for interactive API documentation
   - Or test with curl:
     ```bash
     curl http://localhost:8000/health
     ```

## Frontend Setup

1. **Install dependencies (if not already done):**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the frontend:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## Usage

1. Start both backend and frontend servers
2. Open `http://localhost:5173` in your browser
3. Enter a URL to scan
4. Click "Scan" - the frontend will:
   - Run axe-core scan in the browser
   - Send results to the backend API
   - Display both raw scan results and compliance analysis
   - Show AI-powered recommendations (if LongCat API key is configured)

## API Endpoint

### POST /analyze

**Request:**
```json
{
  "violations": [...],
  "incomplete": [...],
  "passes": [...],
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "score": 85.5,
  "total_checks": 10,
  "passed_checks": 8,
  "failed_checks": 2,
  "checks": [...],
  "ai_recommendations": "..."
}
```

## Troubleshooting

- **Backend not connecting:** Make sure the backend is running on port 8000
- **CORS errors:** Check that the frontend URL is in the allowed origins list in `backend/app/main.py`
- **No AI recommendations:** Check that `LONGCAT_API_KEY` is set in your `.env` file
- **Import errors:** Make sure you're running from the `backend` directory or have the correct Python path

