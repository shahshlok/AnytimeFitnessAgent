# Anytime Fitness AI Agent - Production Deployment Guide

## Overview
This guide covers deploying the Anytime Fitness AI Agent to your VM for production use.

## Prerequisites
- VM with Python 3.8+ and Node.js 18+ installed
- Access to two ports on your VM (one for frontend, one for backend)
- OpenAI API key and Vector Store ID

## Quick Start

### 1. Backend Deployment

1. **Navigate to backend directory:**
   ```bash
   cd ai_agent/backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r ../../requirements.txt
   ```

3. **Configure environment variables:**
   Update `.env` file with your settings:
   ```bash
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   VECTOR_STORE_ID=your_vector_store_id_here
   
   # Production settings
   PORT=7479
   HOST=0.0.0.0
   ALLOWED_ORIGINS=*
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   ```

4. **Start the backend server:**
   ```bash
   python start_server.py
   ```
   
   Or use uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 7479
   ```

### 2. Frontend Deployment

1. **Navigate to frontend directory:**
   ```bash
   cd ai_agent/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment for production:**
   Update `.env.production` with your VM's IP and backend port:
   ```bash
   VITE_API_BASE_URL=http://YOUR_VM_IP:7479
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

5. **Preview the production build:**
   ```bash
   npm run preview -- --host 0.0.0.0 --port 5173
   ```

## Port Configuration

- **Frontend**: Port 5173 (accessible externally)
- **Backend**: Port 7479 (internal, accessed by frontend)

Make sure your VM firewall allows:
- Incoming connections on port 5173 (frontend)
- Internal connections on port 7479 (backend)

## Production Considerations

### Security
- Update `ALLOWED_ORIGINS` in backend `.env` to specific domains in production
- Consider using HTTPS in production
- Never commit `.env` files with real API keys

### Monitoring
- Logs are written to `/tmp/af_backend.log` and console
- Frontend logs are available in browser console
- Monitor API response times and error rates

### Performance
- Backend includes request timeouts (60s transcription, 120s chat)
- Frontend includes comprehensive error handling and retry logic
- All API calls include timeout handling

## Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Check if backend is running on correct port
   - Verify firewall settings
   - Check logs in `/tmp/af_backend.log`

2. **CORS Errors**
   - Update `ALLOWED_ORIGINS` in backend `.env`
   - Verify frontend is using correct API URL

3. **API Errors**
   - Verify OpenAI API key is valid
   - Check Vector Store ID is correct
   - Monitor backend logs for detailed error messages

### Log Locations
- **Backend**: `/tmp/af_backend.log` and console output
- **Frontend**: Browser console (F12 Developer Tools)

## Environment Variables Reference

### Backend (.env)
```bash
OPENAI_API_KEY=          # Required: Your OpenAI API key
VECTOR_STORE_ID=         # Required: Your vector store ID
PORT=7479                # Backend port
HOST=0.0.0.0            # Bind to all interfaces
ALLOWED_ORIGINS=*        # CORS origins (use specific domains in production)
LOG_LEVEL=INFO          # Logging level
ENVIRONMENT=production   # Environment indicator
```

### Frontend (.env.production)
```bash
VITE_API_BASE_URL=http://YOUR_VM_IP:7479  # Backend API URL
```

## Health Check

Once deployed, verify everything is working:

1. **Backend health check:**
   ```bash
   curl http://YOUR_VM_IP:7479/health
   ```

2. **Frontend access:**
   Open `http://YOUR_VM_IP:5173` in your browser

3. **Test chat functionality:**
   - Send a text message
   - Try voice input (if microphone permissions are granted)
   - Check browser console for any errors

## Support

If you encounter issues:
1. Check the logs in `/tmp/af_backend.log`
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure all required ports are accessible