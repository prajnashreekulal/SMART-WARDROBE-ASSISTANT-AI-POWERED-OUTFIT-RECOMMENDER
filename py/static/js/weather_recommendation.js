// static/js/weather_recommendation.js

async function getLocationAndLoadRecommendations() {
    // Check if weather section exists (user is logged in)
    const weatherSection = document.getElementById('weather-info');
    if (!weatherSection) {
        console.log('Weather section not found - user probably not logged in');
        return;
    }
    
    try {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    console.log(`Got location: lat=${lat}, lon=${lon}`);
                    await loadRecommendations(lat, lon);
                },
                (error) => {
                    console.warn("Location access denied. Using default city.");
                    loadRecommendations(null, null, 'New York');
                }
            );
        } else {
            console.warn("Geolocation not supported.");
            loadRecommendations(null, null, 'New York');
        }
    } catch (error) {
        console.error('Error in getLocationAndLoadRecommendations:', error);
    }
}

async function loadRecommendations(lat, lon, city = null) {
    try {
        let url = '/api/auto-recommend?';
        
        if (lat && lon) {
            url += `lat=${lat}&lon=${lon}`;
            console.log(`Fetching with coordinates: ${url}`);
        } else if (city) {
            url += `city=${city}`;
            console.log(`Fetching with city: ${url}`);
        }
        
        const response = await fetch(url);
        
        // Handle 401 (not logged in)
        if (response.status === 401) {
            console.log('User not logged in - skipping weather recommendations');
            document.getElementById('weather-info').innerHTML = `
                <div class="weather-card" style="background: #f0f0f0; color: #666;">
                    <p>🔒 Please <a href="/login" style="color: #667eea;">login</a> to see personalized weather recommendations</p>
                </div>
            `;
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            document.getElementById('weather-info').innerHTML = `
                <div class="weather-card" style="color: red;">
                    <p>❌ Error: ${errorData.error || 'Could not fetch weather'}</p>
                </div>
            `;
            return;
        }
        
        const data = await response.json();
        console.log('Recommendations data:', data);
        
        displayWeatherAndOutfits(data);
    } catch (error) {
        console.error('Error loading recommendations:', error);
        document.getElementById('weather-info').innerHTML = `
            <div class="weather-card" style="color: red;">
                <p>❌ Error: ${error.message}</p>
            </div>
        `;
    }
}

function displayWeatherAndOutfits(data) {
    // Check if season exists
    if (!data.season) {
        console.error('Season is undefined in data:', data);
        document.getElementById('weather-info').innerHTML = `
            <div class="weather-card" style="color: red;">
                <p>❌ Error: Season data missing</p>
            </div>
        `;
        return;
    }

    const seasonEmoji = {
        'Summer': '☀️',
        'Winter': '❄️',
        'Spring': '🌸',
        'Autumn': '🍂',
        'Rainy': '🌧️'
    };
    
    const emoji = seasonEmoji[data.season] || '🌤️';
    
    // Display weather card
    const weatherHTML = `
        <div class="weather-card">
            <h3>${emoji} ${data.season.toUpperCase()} WEATHER</h3>
            <p>🌡️ Temperature: ${data.temperature}°C</p>
            <p>💧 Humidity: ${data.humidity}%</p>
        </div>
    `;
    document.getElementById('weather-info').innerHTML = weatherHTML;
    
    // Display outfit recommendations
    displayOutfits(data.outfits);
}

function displayOutfits(outfits) {
    if (!outfits || outfits.length === 0) {
        document.getElementById('weather-section').innerHTML = `
            <p style="color: #666; text-align: center;">No outfits available for this weather</p>
        `;
        document.getElementById('occasion-section').innerHTML = '';
        return;
    }
    
    // Separate outfits by occasion
    const casualOutfit = outfits.find(o => o.occasion === 'Casual');
    const sportsOutfit = outfits.find(o => o.occasion === 'Sports');
    const partyOutfit = outfits.find(o => o.occasion === 'Party');
    
    // Display weather-based (casual) outfit in main section
    if (casualOutfit) {
        const weatherHTML = `
            <h3>☀️ Recommended for Today's Weather</h3>
            <div class="outfit-display">
                ${createCompleteOutfitCard(casualOutfit)}
            </div>
        `;
        document.getElementById('weather-section').innerHTML = weatherHTML;
    } else {
        document.getElementById('weather-section').innerHTML = `
            <h3>☀️ Recommended for Today's Weather</h3>
            <p style="color: #666; text-align: center;">No casual outfit available for this weather</p>
        `;
    }
    
    // Display sports and party outfits in occasion section
    const occasionOutfits = [sportsOutfit, partyOutfit].filter(o => o !== undefined);
    
    if (occasionOutfits.length > 0) {
        const occasionHTML = `
            <h3>🎯 Occasion-Based Outfits</h3>
            <div class="outfits-grid-horizontal">
                ${occasionOutfits.map(outfit => createCompleteOutfitCard(outfit)).join('')}
            </div>
        `;
        document.getElementById('occasion-section').innerHTML = occasionHTML;
    } else {
        document.getElementById('occasion-section').innerHTML = `
            <h3>🎯 Occasion-Based Outfits</h3>
            <p style="color: #666; text-align: center;">No sports or party outfits available</p>
        `;
    }
}

function createCompleteOutfitCard(outfit) {
    return `
        <div class="outfit-complete-card">
            <h4>${outfit.name}</h4>
            <p class="outfit-description">${outfit.description}</p>
            
            <div class="outfit-items">
                <div class="outfit-item">
                    <img src="${outfit.top_image}" alt="Top" onerror="this.src='/static/placeholder.png'">
                    <span class="item-label">👕 Top (worn ${outfit.top_wear_count}x)</span>
                </div>
                
                <div class="outfit-item">
                    <img src="${outfit.bottom_image}" alt="Bottom" onerror="this.src='/static/placeholder.png'">
                    <span class="item-label">👖 Bottom (worn ${outfit.bottom_wear_count}x)</span>
                </div>
                
                <div class="outfit-item">
                    <img src="${outfit.shoe_image}" alt="Shoes" onerror="this.src='/static/placeholder.png'">
                    <span class="item-label">👟 Shoes (worn ${outfit.shoe_wear_count}x)</span>
                </div>
            </div>
            
            <button class="mark-worn-btn" onclick="markAsWorn(${outfit.top_id}, ${outfit.bottom_id}, ${outfit.shoe_id})">
                ✓ Mark as Worn
            </button>
        </div>
    `;
}

async function markAsWorn(topId, bottomId, shoeId) {
    try {
        const response = await fetch('/mark_outfit_worn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                top_id: topId,
                bottom_id: bottomId,
                shoe_id: shoeId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Outfit marked as worn! Wear counts updated.');
            // Reload recommendations to show updated wear counts
            window.location.reload();
        } else {
            alert('❌ Error: ' + (result.error || 'Failed to mark outfit as worn'));
        }
    } catch (error) {
        console.error('Error marking outfit as worn:', error);
        alert('❌ Failed to mark outfit as worn');
    }
}

// Load on page load
document.addEventListener('DOMContentLoaded', getLocationAndLoadRecommendations);
