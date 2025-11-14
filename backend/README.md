# ComplyScan Backend API

FastAPI backend service for analyzing accessibility compliance using axe-core results and providing AI-powered recommendations.

## Features

- ✅ Analyzes axe-core scan results against 10 specific compliance checks
- ✅ Calculates compliance score
- ✅ Provides AI-powered recommendations using LongCat API
- ✅ RESTful API with clear response structure

## Compliance Checks

1. **Meaningful Sequence** - Ensure reading order makes logical sense for screen readers
2. **Sensory Characteristics** - Do not rely solely on colour, shape, or sound to convey meaning
3. **Use of Colour** - Information should not depend only on colour differences
4. **Keyboard Accessible** - All functionality should be usable via keyboard only
5. **No Keyboard Trap** - Ensure users can navigate in and out of components using the keyboard
6. **Pointer Cancellation** - Click or drag actions should be cancellable or undoable
7. **Label in Name** - Visible label should match the accessible name
8. **Timing Adjustable** - Allow users to extend or disable time limits where applicable
9. **Seizures** - Avoid flashing content exceeding 3 flashes per second
10. **Bypass Blocks** - Provide skip links or navigation mechanisms to bypass repetitive content

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable for LongCat API (optional, for AI recommendations):
```bash
export LONGCAT_API_KEY=your_api_key_here
```

Or create a `.env` file:
```
LONGCAT_API_KEY=your_api_key_here
```

3. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /analyze

Analyze axe-core results and return compliance score with AI recommendations.

**Request Body:**
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
  "checks": [
    {
      "check_id": "meaningful_sequence",
      "check_name": "Meaningful Sequence",
      "passed": true,
      "issues": [],
      "recommendation": null
    },
    ...
  ],
  "ai_recommendations": "AI-generated recommendations text..."
}
```

### GET /health

Health check endpoint.

### GET /

API information and available endpoints.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

- `LONGCAT_API_KEY` (optional): Your LongCat API key for AI recommendations. If not provided, the API will work but won't include AI recommendations.

## Development

The backend uses:
- **FastAPI** for the web framework
- **Pydantic** for data validation
- **httpx** for async HTTP requests to LongCat API
- **Uvicorn** as the ASGI server

## CORS

The API is configured to accept requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)
- `http://127.0.0.1:5173`

To add more origins, edit `app/main.py` and update the `allow_origins` list in the CORS middleware.

