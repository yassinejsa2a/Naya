// Google Maps Integration for NAYA

let map = null;
let placesService = null;
let markers = [];

// Initialize Google Maps
function initializeMap() {
    // Default location (Paris, France)
    const defaultLocation = { lat: 48.8566, lng: 2.3522 };
    
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;
    
    // Create map
    map = new google.maps.Map(mapContainer, {
        zoom: 10,
        center: defaultLocation,
        styles: [
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{ visibility: 'on' }]
            }
        ]
    });
    
    // Initialize Places service
    placesService = new google.maps.places.PlacesService(map);
    
    // Setup search functionality
    setupMapSearch();
    
    // Load places with reviews
    loadPlacesOnMap();
}

// Setup search functionality
function setupMapSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    if (!searchInput || !searchBtn) return;
    
    // Create autocomplete
    const autocomplete = new google.maps.places.Autocomplete(searchInput);
    autocomplete.bindTo('bounds', map);
    
    // Handle place selection
    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        
        if (!place.geometry) {
            console.log("No details available for input: '" + place.name + "'");
            return;
        }
        
        // Center map on selected place
        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);
        }
        
        // Add marker for selected place
        addPlaceMarker(place);
        
        // Search for reviews in this area
        searchNearbyReviews(place.geometry.location);
    });
    
    // Handle search button
    searchBtn.addEventListener('click', function() {
        const query = searchInput.value.trim();
        if (query) {
            searchPlaces(query);
        }
    });
    
    // Handle enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                searchPlaces(query);
            }
        }
    });
}

// Search for places using Google Places API
function searchPlaces(query) {
    const request = {
        query: query,
        fields: ['name', 'geometry', 'formatted_address', 'rating', 'photos']
    };
    
    placesService.textSearch(request, function(results, status) {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            clearMarkers();
            
            // Add markers for all results
            results.forEach(place => {
                addPlaceMarker(place);
            });
            
            // Fit map to show all results
            if (results.length > 0) {
                const bounds = new google.maps.LatLngBounds();
                results.forEach(place => {
                    bounds.extend(place.geometry.location);
                });
                map.fitBounds(bounds);
            }
        } else {
            console.error('Places search failed:', status);
        }
    });
}

// Add marker to map
function addPlaceMarker(place) {
    const marker = new google.maps.Marker({
        position: place.geometry.location,
        map: map,
        title: place.name,
        icon: {
            url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        }
    });
    
    // Create info window
    const infoWindow = new google.maps.InfoWindow({
        content: createInfoWindowContent(place)
    });
    
    // Show info window on marker click
    marker.addListener('click', function() {
        // Close all other info windows
        markers.forEach(m => {
            if (m.infoWindow) {
                m.infoWindow.close();
            }
        });
        
        infoWindow.open(map, marker);
    });
    
    // Store info window reference
    marker.infoWindow = infoWindow;
    markers.push(marker);
    
    return marker;
}

// Create content for info window
function createInfoWindowContent(place) {
    let content = `
        <div class="info-window">
            <h3>${place.name}</h3>
            <p>${place.formatted_address || ''}</p>
    `;
    
    if (place.rating) {
        content += `<p>Rating: ${place.rating} ⭐</p>`;
    }
    
    if (auth.isLoggedIn()) {
        content += `
            <div class="info-actions">
                <button onclick="addReviewForPlace('${place.place_id}', '${place.name}')" class="btn-small">
                    Add Review
                </button>
                <button onclick="addPhotoForPlace('${place.place_id}', '${place.name}')" class="btn-small">
                    Add Photo
                </button>
            </div>
        `;
    }
    
    content += '</div>';
    return content;
}

// Load places that have reviews on the map
async function loadPlacesOnMap() {
    try {
        const response = await api.getPlaces({ limit: 50 });
        
        response.places.forEach(place => {
            if (place.latitude && place.longitude) {
                const marker = new google.maps.Marker({
                    position: { lat: place.latitude, lng: place.longitude },
                    map: map,
                    title: place.name,
                    icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                        scaledSize: new google.maps.Size(28, 28)
                    }
                });
                
                // Create info window for places with reviews
                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div class="info-window">
                            <h3>${place.name}</h3>
                            <p>${place.city}, ${place.country}</p>
                            <p>${place.description || ''}</p>
                            <p><strong>Reviews:</strong> ${place.reviews_count || 0}</p>
                            <p><strong>Photos:</strong> ${place.photos_count || 0}</p>
                            <button onclick="viewPlaceDetails('${place.id}')" class="btn-small">
                                View Details
                            </button>
                        </div>
                    `
                });
                
                marker.addListener('click', function() {
                    infoWindow.open(map, marker);
                });
                
                markers.push(marker);
            }
        });
        
    } catch (error) {
        console.error('Error loading places on map:', error);
    }
}

// Search for reviews near a location
async function searchNearbyReviews(location) {
    try {
        // This would require backend support for geolocation-based search
        // For now, we'll just log the location
        console.log('Searching for reviews near:', location.lat(), location.lng());
        
        // You could implement this by sending lat/lng to backend
        // const response = await api.getReviews({
        //     latitude: location.lat(),
        //     longitude: location.lng(),
        //     radius: 10000 // 10km radius
        // });
        
    } catch (error) {
        console.error('Error searching nearby reviews:', error);
    }
}

// Clear all markers from map
function clearMarkers() {
    markers.forEach(marker => {
        marker.setMap(null);
    });
    markers = [];
}

// Add review for a specific place
function addReviewForPlace(placeId, placeName) {
    // Pre-fill the review form with place information
    document.getElementById('reviewPlace').value = placeName;
    document.getElementById('reviewModal').style.display = 'block';
    
    // Store place ID for when form is submitted
    document.getElementById('addReviewForm').dataset.placeId = placeId;
}

// Add photo for a specific place
function addPhotoForPlace(placeId, placeName) {
    // Pre-fill the photo form with place information
    document.getElementById('photoPlace').value = placeName;
    document.getElementById('photoModal').style.display = 'block';
    
    // Store place ID for when form is submitted
    document.getElementById('addPhotoForm').dataset.placeId = placeId;
}

// View place details
function viewPlaceDetails(placeId) {
    // This could show a detailed view of the place with all reviews and photos
    console.log('View details for place:', placeId);
    // Implementation depends on your UI design
}

// Get user's current location
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                map.setCenter(userLocation);
                map.setZoom(15);
                
                // Add marker for user location
                new google.maps.Marker({
                    position: userLocation,
                    map: map,
                    title: 'Your Location',
                    icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                        scaledSize: new google.maps.Size(32, 32)
                    }
                });
                
                // Search for nearby places
                searchNearbyReviews(new google.maps.LatLng(userLocation.lat, userLocation.lng));
            },
            function(error) {
                console.error('Error getting user location:', error);
            }
        );
    } else {
        console.error('Geolocation is not supported by this browser');
    }
}

// Initialize map when Google Maps API is loaded
function initMap() {
    initializeMap();
}

// Export functions for global access
window.initMap = initMap;
window.addReviewForPlace = addReviewForPlace;
window.addPhotoForPlace = addPhotoForPlace;
window.viewPlaceDetails = viewPlaceDetails;