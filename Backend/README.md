# NAYA Travel Journal - Backend

This is the backend API for NAYA Travel Journal, built with Python Flask.

## Structure

```
Backend/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables example
├── api/
│   ├── auth.py         # Authentication endpoints
│   ├── reviews.py      # Reviews management
│   ├── photos.py       # Photo upload and management
│   └── places.py       # Places and Google Maps integration
├── uploads/            # Photo storage directory
├── tests/              # Unit tests
│   └── test_auth.py    # Authentication tests
└── README.md           # This file
```

## Features

### Core API Features
- ✅ RESTful API design
- ✅ JWT authentication
- ✅ User management (register, login, profile)
- ✅ Reviews CRUD operations
- ✅ Photo upload and management
- ✅ Places management with Google Maps integration
- ✅ Input validation and error handling
- ✅ CORS support for frontend integration

### Database Models
- **User**: Authentication and profile management
- **Place**: Travel destinations and locations
- **Review**: User reviews with ratings
- **Photo**: User-uploaded photos with metadata

### Security Features
- Password hashing with Werkzeug
- JWT token authentication
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy ORM
- File upload security

## API Endpoints

### Authentication
```
POST /api/register    - Register new user
POST /api/login       - User login
GET  /api/profile     - Get user profile (requires auth)
PUT  /api/profile     - Update user profile (requires auth)
```

### Reviews
```
GET    /api/reviews     - Get reviews (with filtering)
POST   /api/reviews     - Create new review (requires auth)
GET    /api/reviews/:id - Get specific review
PUT    /api/reviews/:id - Update review (requires auth, owner only)
DELETE /api/reviews/:id - Delete review (requires auth, owner only)
```

### Photos
```
GET    /api/photos     - Get photos (with filtering)
POST   /api/photos     - Upload photo (requires auth)
GET    /api/photos/:id - Get specific photo
PUT    /api/photos/:id - Update photo caption (requires auth, owner only)
DELETE /api/photos/:id - Delete photo (requires auth, owner only)
```

### Places
```
GET  /api/places         - Get places from database
GET  /api/places/search  - Search places via Google Maps API
POST /api/places         - Create new place (requires auth)
GET  /api/places/:id     - Get specific place
PUT  /api/places/:id     - Update place (requires auth)
```

## Setup Instructions

### 1. Environment Setup
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
DATABASE_URL=sqlite:///naya.db
FLASK_DEBUG=True
```

### 4. Database Initialization
The database will be created automatically when you first run the app:
```bash
python app.py
```

### 5. Run the Application
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Required |
| `JWT_SECRET_KEY` | JWT token signing key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///naya.db` |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | Optional |
| `FLASK_DEBUG` | Enable debug mode | `False` |

### Google Maps API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Places API
   - Maps JavaScript API
   - Geocoding API
4. Create API credentials (API Key)
5. Add the API key to your `.env` file

## Database Schema

### User Model
```python
id (String, Primary Key)
username (String, Unique)
email (String, Unique)
password_hash (String)
created_at (DateTime)
updated_at (DateTime)
```

### Place Model
```python
id (String, Primary Key)
name (String)
country (String)
city (String, Optional)
description (Text, Optional)
latitude (Float, Optional)
longitude (Float, Optional)
google_place_id (String, Optional)
created_at (DateTime)
updated_at (DateTime)
```

### Review Model
```python
id (String, Primary Key)
user_id (String, Foreign Key)
place_id (String, Foreign Key)
title (String, Optional)
text (Text)
rating (Integer, 1-5, Optional)
created_at (DateTime)
updated_at (DateTime)
```

### Photo Model
```python
id (String, Primary Key)
user_id (String, Foreign Key)
place_id (String, Foreign Key)
filename (String)
url (String)
caption (Text, Optional)
created_at (DateTime)
```

## API Usage Examples

### Authentication
```bash
# Register
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Reviews
```bash
# Get reviews
curl http://localhost:5000/api/reviews

# Create review (requires auth token)
curl -X POST http://localhost:5000/api/reviews \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"place_id":"place123","text":"Great place!","rating":5}'
```

### Photos
```bash
# Upload photo (requires auth token)
curl -X POST http://localhost:5000/api/photos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@photo.jpg" \
  -F "place_id=place123" \
  -F "caption=Beautiful sunset"
```

## Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=. tests/
```

### Test Structure
- `tests/test_auth.py` - Authentication endpoint tests
- Additional test files can be added for other modules

## Error Handling

The API returns consistent error responses:
```json
{
  "error": "Error message description"
}
```

HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate data)
- `500` - Internal Server Error

## File Upload

### Supported Formats
- PNG, JPG, JPEG, GIF
- Maximum file size: 16MB
- Files are stored in `uploads/` directory

### File Naming
- Files are renamed with UUID to prevent conflicts
- Original extension is preserved
- File paths are stored in database

## Security Considerations

### Authentication
- Passwords are hashed using Werkzeug's security functions
- JWT tokens expire after 7 days (configurable)
- Tokens are required for all authenticated endpoints

### Input Validation
- All inputs are validated and sanitized
- SQL injection protection via SQLAlchemy ORM
- File upload validation (type, size)

### CORS Configuration
- CORS is enabled for frontend integration
- Configure allowed origins for production

## Production Deployment

### Database Migration
For production, consider using PostgreSQL:
```bash
pip install psycopg2-binary
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost/naya
```

### Environment Configuration
```bash
FLASK_DEBUG=False
SECRET_KEY=strong-production-secret
JWT_SECRET_KEY=strong-jwt-secret
DATABASE_URL=postgresql://...
```

### Web Server
Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### File Storage
For production, consider cloud storage (AWS S3, etc.) instead of local file storage.

## Performance Optimization

### Database
- Add database indexes for frequently queried fields
- Use database connection pooling
- Consider caching for frequent queries

### File Handling
- Implement file compression for images
- Use CDN for static file serving
- Add file cleanup routines

## Monitoring and Logging

### Logging
- Flask logs are written to console by default
- Configure file logging for production
- Log API errors and authentication events

### Health Check
Access `http://localhost:5000/` for basic health check.

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints where appropriate
3. Write tests for new features
4. Update API documentation
5. Ensure proper error handling

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

2. **Database Errors**
   - Check if database file has write permissions
   - Verify DATABASE_URL format

3. **Google Maps API Errors**
   - Verify API key is correct
   - Check if required APIs are enabled
   - Ensure billing is set up

4. **File Upload Issues**
   - Check uploads directory permissions
   - Verify file size limits
   - Ensure proper file types

### Debug Mode
Run with debug mode for detailed error messages:
```bash
export FLASK_DEBUG=True
python app.py
```

## Future Enhancements

- [ ] Rate limiting for API endpoints
- [ ] Email verification for user registration
- [ ] Advanced search with Elasticsearch
- [ ] Caching with Redis
- [ ] Automated database migrations
- [ ] API documentation with Swagger
- [ ] Admin panel for content management
- [ ] Backup and restore functionality