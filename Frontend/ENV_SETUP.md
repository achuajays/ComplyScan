# Environment Variables Setup

This project uses environment variables to configure the API endpoint for different environments.

## Setup

### For Development (Local)

Create a `.env` file in the `Frontend` directory with:

```
VITE_API_URL=http://localhost:8000
```

### For Production

Create a `.env.production` file in the `Frontend` directory with:

```
VITE_API_URL=https://complyscan-production-23b6.up.railway.app
```

Or set the environment variable when building:

```bash
VITE_API_URL=https://complyscan-production-23b6.up.railway.app npm run build
```

## How It Works

- In **development mode** (`npm run dev): Uses `.env` file → `http://localhost:8000`
- In **production build** (`npm run build`): Uses `.env.production` file → Railway URL
- If no environment variable is set, it defaults to `http://localhost:8000`

## Vite Environment Variables

Note: In Vite, environment variables must be prefixed with `VITE_` to be accessible in the frontend code.

The variable `VITE_API_URL` is used in `src/App.jsx` to determine which API endpoint to use.

## Files

- `.env` - Development environment (not committed to git)
- `.env.production` - Production environment (not committed to git)
- `.env.example` - Example file (committed to git as a template)

