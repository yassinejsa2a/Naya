# NAYA Travel Journal - Frontend

This is the frontend application for NAYA Travel Journal, built with vanilla HTML, CSS, and JavaScript.

## Structure

```
Frontend/
├── index.html          # Main HTML file
├── src/
│   ├── css/           # Stylesheets
│   │   ├── style.css  # Main styles
│   │   └── auth.css   # Authentication styles
│   ├── js/            # JavaScript modules
│   │   ├── config.js  # Configuration
│   │   ├── api.js     # API communication
│   │   ├── auth.js    # Authentication
│   │   ├── main.js    # Main application logic
│   │   ├── maps.js    # Google Maps integration
│   │   ├── reviews.js # Reviews management
│   │   └── photos.js  # Photos management
│   └── assets/
│       └── images/    # Static images
└── README.md          # This file
```

## Features

### Core Features
- ✅ User authentication (login/register)
- ✅ Browse travel reviews and photos
- ✅ Create and manage reviews
- ✅ Upload and manage photos
- ✅ Interactive Google Maps integration
- ✅ Responsive design for mobile/desktop

### User Interface
- **Home Page**: Hero section with search, Google Maps, recent reviews
- **Reviews Page**: All reviews with filtering and sorting
- **Photos Page**: Photo gallery with lightbox viewing
- **Profile Page**: User profile with personal reviews and photos
- **Authentication**: Login and register forms

### JavaScript Modules

#### `config.js`
- API endpoints configuration
- Application constants
- Environment settings

#### `api.js`
- RESTful API communication
- HTTP request handling
- Error handling and response parsing

#### `auth.js`
- User authentication management
- JWT token handling
- Session persistence
- UI state management

#### `main.js`
- Application initialization
- Navigation handling
- Section management
- Data loading and display

#### `maps.js`
- Google Maps API integration
- Place search functionality
- Markers and info windows
- Location-based features

#### `reviews.js`
- Review creation and management
- Review filtering and sorting
- Review editing and deletion

#### `photos.js`
- Photo upload functionality
- Photo gallery management
- Lightbox viewing
- Photo filtering

## Setup Instructions

### 1. Backend Configuration
Make sure the backend API is running on `http://localhost:5000`

### 2. Google Maps API
1. Get a Google Maps API key from Google Cloud Console
2. Enable the following APIs:
   - Maps JavaScript API
   - Places API
3. Update the API key in `index.html`:
   ```html
   <script async defer src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places"></script>
   ```

### 3. API Configuration
Update `src/js/config.js` if needed:
```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api', // Your backend URL
    // ... other settings
};
```

### 4. Serve the Frontend
You can serve this with any web server:

#### Option 1: Python HTTP Server
```bash
cd Frontend
python -m http.server 8000
```
Then visit `http://localhost:8000`

#### Option 2: Node.js HTTP Server
```bash
cd Frontend
npx http-server -p 8000
```

#### Option 3: Live Server (VS Code Extension)
- Install Live Server extension in VS Code
- Right-click on `index.html` and select "Open with Live Server"

### 5. GitHub Pages (Production)
For production deployment:
1. Push the Frontend folder to GitHub
2. Enable GitHub Pages in repository settings
3. Update `CONFIG.API_BASE_URL` to your production backend URL

## Usage

### For Users
1. **Register/Login**: Create account or login with existing credentials
2. **Browse Content**: View reviews and photos from other travelers
3. **Search Places**: Use the search bar and Google Maps to find destinations
4. **Add Reviews**: Share your travel experiences with ratings and text
5. **Upload Photos**: Add photos with captions to share visually
6. **Profile Management**: View and manage your contributions

### For Developers
1. **Add New Features**: Create new JavaScript modules in `src/js/`
2. **Styling**: Add styles to `src/css/` files
3. **API Integration**: Extend `api.js` for new endpoints
4. **Testing**: Test with browser developer tools

## API Integration

The frontend communicates with the backend API using the following endpoints:

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update user profile

### Reviews
- `GET /api/reviews` - Get reviews (with filtering)
- `POST /api/reviews` - Create new review
- `GET /api/reviews/:id` - Get specific review
- `PUT /api/reviews/:id` - Update review
- `DELETE /api/reviews/:id` - Delete review

### Photos
- `GET /api/photos` - Get photos (with filtering)
- `POST /api/photos` - Upload photo
- `DELETE /api/photos/:id` - Delete photo

### Places
- `GET /api/places` - Get places
- `GET /api/places/search` - Search places via Google Maps
- `POST /api/places` - Create new place

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Performance Considerations

- **Lazy Loading**: Images are loaded lazily
- **API Caching**: Responses are cached where appropriate
- **Debounced Search**: Search inputs are debounced to reduce API calls
- **Responsive Images**: Images are optimized for different screen sizes

## Security Features

- **JWT Token Storage**: Secure token handling in localStorage
- **Input Validation**: Client-side validation for all forms
- **XSS Prevention**: Proper escaping of user-generated content
- **CORS Handling**: Proper cross-origin request configuration

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if backend is running on correct port
   - Verify CORS configuration in backend
   - Check browser console for detailed errors

2. **Google Maps Not Loading**
   - Verify API key is correct and active
   - Check if required APIs are enabled in Google Cloud Console
   - Ensure billing is set up for Google Cloud project

3. **Photos Not Uploading**
   - Check file size (max 5MB)
   - Verify file format (JPEG, PNG, GIF only)
   - Ensure user is logged in

4. **Authentication Issues**
   - Clear localStorage and try again
   - Check if JWT token is expired
   - Verify backend authentication endpoints

### Browser Console
Always check browser console (F12) for detailed error messages.

## Contributing

1. Follow the existing code structure
2. Add comments for complex functions
3. Test new features thoroughly
4. Ensure responsive design compatibility
5. Update this README for new features

## Future Enhancements

- [ ] Offline support with Service Workers
- [ ] Push notifications for new reviews
- [ ] Advanced photo editing features
- [ ] Social sharing integration
- [ ] Multi-language support
- [ ] Dark/light theme toggle
- [ ] Progressive Web App (PWA) features