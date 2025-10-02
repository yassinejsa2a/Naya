# NAYA Travel Journal

A web application that allows travelers to discover local activities, read and share verified reviews, and build a personalized travel diary.

## Team

- **Yassine Bouyanfif**: Front-end Developer, Project Manager & Communication/Documentation
- **Nawfel Laklit**: Back-end Developer & Technical Management

## Project Overview

NAYA is a travel journal platform where users can:
- Create an account and log in securely
- Choose countries they want to visit
- Browse reviews and photos shared by other travelers
- Discover places and activities using Google Maps integration
- Post their own reviews with photos
- Build a personalized travel experience

## Technical Stack

### Backend
- **Python Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT authentication
- **SQLite** - Database (can be upgraded to PostgreSQL)
- **Google Maps API** - Places and location services

### Frontend
- **HTML/CSS/JavaScript** - User interface
- **Google Maps Integration** - Interactive maps
- **Responsive Design** - Mobile-friendly

## Project Structure

```
/
├── README.md           # This file
├── .gitignore         # Git ignore rules
├── Backend/           # Backend API (Flask)
│   ├── app.py         # Main Flask application
│   ├── config.py      # Configuration settings
│   ├── models.py      # Database models (User, Place, Review, Photo)
│   ├── requirements.txt # Python dependencies
│   ├── .env.example   # Environment variables template
│   ├── api/
│   │   ├── auth.py    # Authentication endpoints
│   │   ├── reviews.py # Reviews management
│   │   ├── photos.py  # Photo upload and management
│   │   └── places.py  # Places and Google Maps integration
│   ├── uploads/       # Photo storage
│   ├── tests/         # Unit tests
│   └── README.md      # Backend documentation
└── Frontend/          # Frontend application
    ├── index.html     # Main HTML file
    ├── src/
    │   ├── css/       # Stylesheets
    │   ├── js/        # JavaScript modules
    │   └── assets/    # Static assets
    └── README.md      # Frontend documentation
```

## API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - User login
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

### Reviews
- `GET /api/reviews` - Get reviews (with filtering)
- `POST /api/reviews` - Create new review
- `GET /api/reviews/<id>` - Get specific review
- `PUT /api/reviews/<id>` - Update review
- `DELETE /api/reviews/<id>` - Delete review

### Photos
- `GET /api/photos` - Get photos (with filtering)
- `POST /api/photos` - Upload photo
- `GET /api/photos/<id>` - Get specific photo
- `PUT /api/photos/<id>` - Update photo caption
- `DELETE /api/photos/<id>` - Delete photo

### Places
- `GET /api/places` - Get places from database
- `GET /api/places/search` - Search places via Google Maps API
- `POST /api/places` - Create new place
- `GET /api/places/<id>` - Get specific place
- `PUT /api/places/<id>` - Update place

## Database Schema

### User
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- created_at, updated_at

### Place
- id (Primary Key)
- name
- country
- city
- description
- latitude, longitude
- google_place_id
- created_at, updated_at

### Review
- id (Primary Key)
- user_id (Foreign Key)
- place_id (Foreign Key)
- title
- text
- rating (1-5)
- created_at, updated_at

### Photo
- id (Primary Key)
- user_id (Foreign Key)
- place_id (Foreign Key)
- filename
- url
- caption
- created_at

## Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd Naya
```

### 2. Backend Setup
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python app.py
```

### 3. Frontend Setup
```bash
cd ../Frontend
# Update Google Maps API key in index.html
# Serve with any web server:
python -m http.server 8000
# or use Live Server in VS Code
```

### 4. Access Application
- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:8000

For detailed setup instructions, see the README files in Backend/ and Frontend/ directories.

## Development Workflow

### Branching Strategy
- `main` - Production-ready code
- `development` - Integration branch  
- `feature/*` - Feature branches (e.g., `feature/user-profile`)

### Team Workflow
1. **Yassine (Frontend)**: 
   - Work on `feature/frontend-*` branches
   - Focus on UI/UX and frontend functionality
   - Integrate with backend APIs

2. **Nawfel (Backend)**:
   - Work on `feature/backend-*` branches  
   - Develop API endpoints and business logic
   - Manage database and authentication

### Code Review Process
1. Create feature branch from `development`
2. Implement feature with tests
3. Create Pull Request to `development`
4. Peer review and testing
5. Merge to `development`
6. Regular merges to `main` for releases

## Testing

### Run Tests
```bash
python -m pytest tests/
```

### Test Coverage
```bash
python -m pytest --cov=. tests/
```

## Deployment

### Development
- Backend: Local Flask server
- Frontend: Local development server

### Production
- Backend: Flask on cloud platform (Heroku, AWS, etc.)
- Frontend: GitHub Pages
- Database: PostgreSQL
- File Storage: Cloud storage (AWS S3, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## License

This project is part of a Holberton School portfolio project.

## Contact

- **Yassine Bouyanfif** - Frontend & Project Management
- **Nawfel Laklit** - Backend & Technical Management

---

**NAYA** - Bringing travelers together through authentic experiences and community-driven content.
