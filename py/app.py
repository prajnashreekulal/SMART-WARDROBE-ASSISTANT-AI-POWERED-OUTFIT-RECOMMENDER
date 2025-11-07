from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, random, sqlite3
from recognition_module import single_classification  # your ML model
from weather_service import WeatherService  # NEW: Import weather service


app = Flask(__name__)
app.secret_key = "your_secret_key_here_change_in_production"


# ==========================================
# Weather Service Initialization (NEW)
# ==========================================
try:
    weather_service = WeatherService()
    print("✅ Weather service initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Weather service initialization failed: {e}")
    weather_service = None


# ==========================================
# Upload folder
# ==========================================
BASE_UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)


# ==========================================
# Database Configuration
# ==========================================
DB_PATH = os.path.join(os.path.dirname(__file__), "wardrobe.db")


def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# Smart Recommendation Function (Balanced by Wear Count)
# ==========================================


def get_smart_recommendations_balanced(user_id, season, occasion):
    """
    Get outfit recommendations filtered by season and occasion
    Prioritizes items that have been worn LESS frequently
    This balances wardrobe usage without changing ML models
    FIXED: Case-insensitive matching
    """
    conn = get_db_connection()
    
    # Query for matching tops - ORDER BY wear_count (lowest first)
    # FIXED: Using LOWER() for case-insensitive comparison
    tops = conn.execute('''
        SELECT * FROM clothes 
        WHERE user_id = ? 
        AND subtype = 'top' 
        AND LOWER(season) = LOWER(?)
        AND LOWER(occasion) = LOWER(?)
        ORDER BY wear_count ASC
    ''', (user_id, season, occasion)).fetchall()
    
    # Query for matching bottoms - ORDER BY wear_count (lowest first)
    bottoms = conn.execute('''
        SELECT * FROM clothes 
        WHERE user_id = ? 
        AND subtype = 'bottom' 
        AND LOWER(season) = LOWER(?)
        AND LOWER(occasion) = LOWER(?)
        ORDER BY wear_count ASC
    ''', (user_id, season, occasion)).fetchall()
    
    # Query for matching shoes - ORDER BY wear_count (lowest first)
    shoes = conn.execute('''
        SELECT * FROM clothes 
        WHERE user_id = ? 
        AND subtype = 'foot' 
        AND LOWER(season) = LOWER(?)
        AND LOWER(occasion) = LOWER(?)
        ORDER BY wear_count ASC
    ''', (user_id, season, occasion)).fetchall()
    
    conn.close()
    
    # Check if we have items for all categories
    if not tops or not bottoms or not shoes:
        missing = []
        if not tops: missing.append('tops')
        if not bottoms: missing.append('bottoms')
        if not shoes: missing.append('shoes')
        
        return {
            'success': False,
            'message': f'Not enough {season} {occasion} items ({", ".join(missing)}). Please upload more clothes!'
        }
    
    # Pick items with lowest wear_count (they're already sorted)
    selected_top = tops[0]
    selected_bottom = bottoms[0]
    selected_shoe = shoes[0]
    
    return {
        'success': True,
        'outfit': {
            'top': dict(selected_top),
            'bottom': dict(selected_bottom),
            'shoe': dict(selected_shoe)
        }
    }


# ==========================================
# Routes
# ==========================================


@app.route("/")
def index():
    """Home page"""
    return render_template("index.html", user=session.get("user_id"))


# ==========================================
# Login/Register
# ==========================================


@app.route("/login", methods=["GET","POST"])
def login():
    """User login"""
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password)).fetchone()
        conn.close()
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    """User registration"""
    if request.method=="POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)", (username,email,password))
            conn.commit()
            user_id = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()["id"]
        except:
            conn.close()
            return render_template("register.html", error="Username or email already exists")
        conn.close()
        session["user_id"] = user_id
        session["username"] = username
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    """User logout"""
    session.clear()
    return redirect(url_for("index"))


# ==========================================
# Upload route (FIXED - SAVE AS LOWERCASE)
# ==========================================


@app.route("/upload", methods=["POST"])
def upload():
    """Upload and classify clothing item"""
    user_id = session.get("user_id", "guest")
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    file = request.files["file"]
    filepath = os.path.join(user_folder, file.filename)
    file.save(filepath)

    # Use ML model to classify clothing
    subtype, info_str, details = single_classification(filepath)

    # FIXED: Convert season and occasion to lowercase for consistency
    season = details[3].lower()  # "Spring" -> "spring"
    occasion = details[4].lower()  # "Casual" -> "casual"

    print(f"📥 Upload: season={season}, occasion={occasion}")

    # Save to database with wear_count=0 by default
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO clothes (user_id, file_path, subtype, color, season, occasion, wear_count) 
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (user_id, filepath, subtype, details[2], season, occasion))
    conn.commit()
    conn.close()

    return jsonify({
        "file_url": f"/static/uploads/{user_id}/{file.filename}",
        "subtype": subtype,
        "season": season,
        "occasion": occasion,
        "info": info_str
    })


# ==========================================
# Recommendation Page
# ==========================================


@app.route("/recommend")
def recommend():
    """Render the recommendation page with season/occasion filters"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("recommend.html", user=session.get("user_id"))


# ==========================================
# Generate Outfit API (With Wear Balancing)
# ==========================================


@app.route("/generate_outfit", methods=["POST"])
def generate_outfit():
    """
    Generate outfit based on season and occasion preferences
    Prioritizes less-worn items
    """
    if "user_id" not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    user_id = session["user_id"]
    season = request.form.get('season', 'Summer')
    occasion = request.form.get('occasion', 'Casual')
    
    # Get balanced recommendations (prioritizes less-worn items)
    result = get_smart_recommendations_balanced(user_id, season, occasion)
    
    if result['success']:
        outfit = result['outfit']
        top_filename = os.path.basename(outfit['top']['file_path'])
        bottom_filename = os.path.basename(outfit['bottom']['file_path'])
        shoe_filename = os.path.basename(outfit['shoe']['file_path'])
        
        return jsonify({
            'top_image': f'static/uploads/{user_id}/{top_filename}',
            'bottom_image': f'static/uploads/{user_id}/{bottom_filename}',
            'shoe_image': f'static/uploads/{user_id}/{shoe_filename}',
            'season': season,
            'occasion': occasion,
            'top_id': outfit['top']['id'],
            'bottom_id': outfit['bottom']['id'],
            'shoe_id': outfit['shoe']['id'],
            'top_wear_count': outfit['top']['wear_count'],
            'bottom_wear_count': outfit['bottom']['wear_count'],
            'shoe_wear_count': outfit['shoe']['wear_count']
        })
    else:
        return jsonify({'error': result['message']}), 404


# ==========================================
# NEW: Auto Recommendation Route (Weather-Based) - USING YOUR ML MODEL
# ==========================================


@app.route('/api/auto-recommend', methods=['GET'])
def auto_recommend():
    """
    Auto-recommend outfit based on user's location and weather
    Uses your existing get_smart_recommendations_balanced() function
    which already handles ML model recommendations and wear count balancing
    """
    if "user_id" not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    try:
        user_id = session["user_id"]
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        print(f"\n🔍 AUTO-RECOMMEND REQUEST")
        print(f"User ID: {user_id}")
        print(f"Latitude: {lat}, Longitude: {lon}")
        
        # Check if weather service is available
        if weather_service is None:
            print("⚠️ Weather service not available")
            return jsonify({"error": "Weather service not available"}), 500
        
        # Method 1: Use coordinates from browser geolocation
        if lat and lon:
            try:
                weather_data = weather_service.get_weather_by_coordinates(float(lat), float(lon))
                print(f"✅ Got weather data from coordinates")
            except Exception as e:
                print(f"❌ Error fetching weather by coordinates: {e}")
                return jsonify({"error": f"Failed to fetch weather: {str(e)}"}), 400
        else:
            # Method 2: Fall back to city name
            city = request.args.get('city', 'New York')
            print(f"📍 Using city fallback: {city}")
            try:
                weather_data = weather_service.get_weather_by_city(city)
                print(f"✅ Got weather data from city")
            except Exception as e:
                print(f"❌ Error fetching weather by city: {e}")
                return jsonify({"error": f"Failed to fetch weather for {city}: {str(e)}"}), 400
        
        # Validate weather data
        if not weather_data:
            print("❌ Weather data is None")
            return jsonify({"error": "Could not fetch weather data"}), 400
        
        if 'current' not in weather_data:
            print(f"❌ Missing 'current' key in weather_data: {weather_data.keys()}")
            return jsonify({"error": "Invalid weather data format"}), 400
        
        current = weather_data['current']
        print(f"📊 Weather Data: temp={current.get('temperature_2m')}, code={current.get('weather_code')}")
        
        # Safely extract weather values with defaults
        temp = current.get('temperature_2m', 20)
        weather_code = current.get('weather_code', 0)
        
        # Convert to season using weather API
        try:
            season = weather_service.get_season_category(temp, weather_code)
            print(f"🌡️ Detected Season: {season}")
        except Exception as e:
            print(f"❌ Error detecting season: {e}")
            return jsonify({"error": f"Failed to detect season: {str(e)}"}), 400
        
        if not season:
            print("❌ Season is None or empty")
            return jsonify({"error": "Could not determine season"}), 400
        
        # Convert season to match your database format (capitalize first letter)
        season_formatted = season.capitalize()
        
        # NOW USE YOUR ORIGINAL MODEL FOR RECOMMENDATIONS
        print(f"\n🎯 Using your ML model for recommendations...")
        
        # Get 3 different outfit recommendations for different occasions
        occasions = ['casual', 'sports', 'party']
        outfit_recommendations = []
        
        for occasion in occasions:
            print(f"\n📦 Getting {season_formatted} + {occasion.capitalize()} outfit...")
            
            # USE YOUR EXISTING FUNCTION that handles ML model and wear balancing
            result = get_smart_recommendations_balanced(user_id, season_formatted, occasion.capitalize())
            
            if result['success']:
                outfit = result['outfit']
                
                # Extract filenames for frontend
                top_filename = os.path.basename(outfit['top']['file_path'])
                bottom_filename = os.path.basename(outfit['bottom']['file_path'])
                shoe_filename = os.path.basename(outfit['shoe']['file_path'])
                
                outfit_recommendations.append({
                    'occasion': occasion.capitalize(),
                    'season': season_formatted,
                    'name': f"{season_formatted} {occasion.capitalize()} Outfit",
                    'description': f"Perfect {season_formatted.lower()} outfit for {occasion} occasions",
                    'top_image': f"/static/uploads/{user_id}/{top_filename}",
                    'bottom_image': f"/static/uploads/{user_id}/{bottom_filename}",
                    'shoe_image': f"/static/uploads/{user_id}/{shoe_filename}",
                    'top_id': outfit['top']['id'],
                    'bottom_id': outfit['bottom']['id'],
                    'shoe_id': outfit['shoe']['id'],
                    'top_wear_count': outfit['top']['wear_count'],
                    'bottom_wear_count': outfit['bottom']['wear_count'],
                    'shoe_wear_count': outfit['shoe']['wear_count']
                })
                
                print(f"   ✅ Found outfit: {occasion}")
                print(f"      Top: {top_filename} (worn {outfit['top']['wear_count']} times)")
                print(f"      Bottom: {bottom_filename} (worn {outfit['bottom']['wear_count']} times)")
                print(f"      Shoe: {shoe_filename} (worn {outfit['shoe']['wear_count']} times)")
            else:
                print(f"   ⚠️ No {season_formatted} {occasion} outfit available")
                print(f"      Reason: {result['message']}")
        
        # Check if we got any recommendations
        if not outfit_recommendations:
            print(f"\n❌ No outfits found for {season_formatted} season")
            return jsonify({
                "error": f"No {season_formatted} outfits in your wardrobe. Please upload more {season_formatted.lower()} clothes!",
                "season": season_formatted,
                "temperature": temp,
                "humidity": current.get('humidity_2m', 'N/A'),
                "wind_speed": current.get('wind_speed_10m', 'N/A'),
                "outfits": []
            }), 200
        
        print(f"\n✅ Successfully generated {len(outfit_recommendations)} outfit recommendations using your ML model!")
        
        response = {
            "season": season_formatted,
            "temperature": temp,
            "weather_code": weather_code,
            "humidity": current.get('humidity_2m', 'N/A'),
            "wind_speed": current.get('wind_speed_10m', 'N/A'),
            "outfits": outfit_recommendations,
            "total_outfits": len(outfit_recommendations)
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR in auto_recommend: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ==========================================
# Mark Outfit as Worn (Wear Tracking)
# ==========================================


@app.route("/mark_outfit_worn", methods=["POST"])
def mark_outfit_worn():
    """
    Mark an outfit as worn and increment wear counts for all items
    """
    if "user_id" not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session["user_id"]
    data = request.get_json()
    
    top_id = data.get('top_id')
    bottom_id = data.get('bottom_id')
    shoe_id = data.get('shoe_id')
    
    conn = get_db_connection()
    
    try:
        # Increment wear count for each item
        for item_id in [top_id, bottom_id, shoe_id]:
            if item_id:
                conn.execute("""
                    UPDATE clothes 
                    SET wear_count = wear_count + 1 
                    WHERE id = ? AND user_id = ?
                """, (item_id, user_id))
        
        # Also record in outfit_history table
        conn.execute("""
            INSERT INTO outfit_history (user_id, top_id, bottom_id, shoe_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, top_id, bottom_id, shoe_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Outfit marked as worn!'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)})


# ==========================================
# Wardrobe page (With wear counts)
# ==========================================


@app.route("/wardrobe")
def wardrobe():
    """Display user's wardrobe with wear counts"""
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    clothes = conn.execute("SELECT * FROM clothes WHERE user_id=?", (user_id,)).fetchall()
    conn.close()

    # Organize clothes by subtype with all metadata
    wardrobe = {"top": [], "bottom": [], "foot": []}
    for c in clothes:
        wardrobe[c["subtype"]].append({
            "id": c["id"],
            "file_name": os.path.basename(c["file_path"]),
            "url": f"/static/uploads/{user_id}/{os.path.basename(c['file_path'])}",
            "subtype": c["subtype"],
            "season": c["season"],
            "occasion": c["occasion"],
            "wear_count": c["wear_count"]
        })

    return render_template("wardrobe.html", wardrobe=wardrobe, user=user_id)


# ==========================================
# Update Item (Manual Season/Occasion Editing)
# ==========================================


@app.route("/update_item", methods=["POST"])
def update_item():
    """Update season and occasion for an existing wardrobe item"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"})
    
    user_id = session["user_id"]
    data = request.get_json()
    file_name = data.get("file_name")
    new_season = data.get("season").lower()  # FIXED: Convert to lowercase
    new_occasion = data.get("occasion").lower()  # FIXED: Convert to lowercase
    
    # Construct full file path
    file_path = os.path.join(BASE_UPLOAD_FOLDER, str(user_id), file_name)
    
    # Update database
    conn = get_db_connection()
    try:
        conn.execute("""
            UPDATE clothes 
            SET season = ?, occasion = ? 
            WHERE user_id = ? AND file_path = ?
        """, (new_season, new_occasion, user_id, file_path))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Item updated successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "error": str(e)})


# ==========================================
# Delete wardrobe item
# ==========================================


@app.route("/delete_item", methods=["POST"])
def delete_item():
    """Delete a wardrobe item"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"})

    user_id = session["user_id"]
    data = request.get_json()
    file_name = data.get("file")
    file_path = os.path.join(BASE_UPLOAD_FOLDER, str(user_id), file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        # Remove from DB
        conn = get_db_connection()
        conn.execute("DELETE FROM clothes WHERE user_id=? AND file_path=?", (user_id, file_path))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "File not found"})


# ==========================================
# Wardrobe Statistics
# ==========================================


@app.route("/wardrobe_stats")
def wardrobe_stats():
    """Get statistics about wardrobe usage"""
    if "user_id" not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session["user_id"]
    conn = get_db_connection()
    
    stats = conn.execute("""
        SELECT 
            COUNT(*) as total_items,
            SUM(wear_count) as total_wears,
            AVG(wear_count) as avg_wears,
            MIN(wear_count) as min_wears,
            MAX(wear_count) as max_wears
        FROM clothes
        WHERE user_id = ?
    """, (user_id,)).fetchone()
    
    # Get most worn items
    most_worn = conn.execute("""
        SELECT id, file_path, subtype, wear_count 
        FROM clothes 
        WHERE user_id = ? 
        ORDER BY wear_count DESC 
        LIMIT 3
    """, (user_id,)).fetchall()
    
    # Get least worn items
    least_worn = conn.execute("""
        SELECT id, file_path, subtype, wear_count 
        FROM clothes 
        WHERE user_id = ? 
        ORDER BY wear_count ASC 
        LIMIT 3
    """, (user_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'total_items': stats['total_items'] or 0,
        'total_wears': stats['total_wears'] or 0,
        'avg_wears': round(stats['avg_wears'], 2) if stats['avg_wears'] else 0,
        'most_worn': [{'id': m['id'], 'path': m['file_path'], 'type': m['subtype'], 'count': m['wear_count']} for m in most_worn],
        'least_worn': [{'id': l['id'], 'path': l['file_path'], 'type': l['subtype'], 'count': l['wear_count']} for l in least_worn]
    })


# ==========================================
# Outfit History
# ==========================================


@app.route("/outfit_history")
def outfit_history():
    """Display outfit wear history"""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    conn = get_db_connection()
    
    history = conn.execute("""
        SELECT oh.*, 
               c1.file_path as top_path,
               c2.file_path as bottom_path,
               c3.file_path as shoe_path
        FROM outfit_history oh
        LEFT JOIN clothes c1 ON oh.top_id = c1.id
        LEFT JOIN clothes c2 ON oh.bottom_id = c2.id
        LEFT JOIN clothes c3 ON oh.shoe_id = c3.id
        WHERE oh.user_id = ?
        ORDER BY oh.date_worn DESC
        LIMIT 20
    """, (user_id,)).fetchall()
    
    conn.close()
    
    return render_template("outfit_history.html", history=history, user=user_id)


# ==========================================
# Run Application
# ==========================================


if __name__=="__main__":
    app.run(debug=True, port=5000)
