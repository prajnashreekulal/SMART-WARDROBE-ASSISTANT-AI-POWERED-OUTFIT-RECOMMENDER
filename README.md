
# 👗 **SMART WARDROBE ASSISTANT — AI-POWERED OUTFIT RECOMMENDER**

An **AI-powered Smart Wardrobe System** built using **Python, Flask, and Machine Learning (CNN)** that digitizes your wardrobe, classifies clothing using image recognition, and recommends the perfect outfit based on **occasion, weather, personal preferences, and usage frequency**.

This project functions as a **personal AI stylist**, helping users simplify outfit decisions, reduce fashion waste, and manage their wardrobe intelligently.

---

## 🌟 **INTRODUCTION**

Choosing an outfit can be surprisingly stressful due to the overwhelming number of choices. The Smart Wardrobe Assistant solves this by:

* Digitizing the user's wardrobe
* Automatically classifying clothes using Machine Learning
* Recommending outfits based on weather, occasion, and style
* Tracking usage to reduce wardrobe neglect and promote sustainability

It analyzes **color coordination, category matching, seasonal suitability**, and more — making fashion smarter, easier, and organized.

---

## 🚩 **PROBLEM STATEMENT**

People struggle daily with:

* Decision fatigue while choosing clothes
* Overbuying due to poor wardrobe visibility
* Underutilized clothing items
* No personalized fashion guidance
* Dressing incorrectly for the weather or event

This smart system provides **AI-powered outfit selection**, reducing stress and encouraging sustainable, data-driven fashion choices.

---

## 🧠 **ML & AI FEATURES IMPLEMENTED**

This version of the Smart Wardrobe Assistant includes:

### 🤖 **AI Clothing Classification Using CNN**

* Predicts **top / bottom / footwear / accessory**
* Predicts **occasion category** (formal / casual / party / ethnic)
* Predicts **color & pattern**
* Predicts **subtype** (t-shirt, shirt, kurti, jeans, skirt, shoes, etc.)

### 🎯 **AI-Powered Recommendations**

* Suggests outfits based on:

  * Weather (temp, humidity, condition)
  * Occasion type (casual, formal, party, ethnic)
  * Color compatibility
  * Balanced usage (least worn items suggested first)

### 🔄 **Wear Count Tracking**

* Tracks how many times each item was worn
* Recommender prioritizes underused items
* Promotes sustainable fashion

---

## 🧥 **SMART WARDROBE MANAGEMENT**

Users can:

* Upload clothing images
* Automatically classify type, color, and occasion
* Edit tags manually if needed
* Store items in digital wardrobe
* Delete or modify wardrobe items
* View wardrobe analytics & insights

---

## ☁️ **WEATHER-INTEGRATED RECOMMENDATIONS**

System fetches real-time weather and suggests:

* Light outfits for hot weather
* Layered outfits for cold weather
* Waterproof items for rainy season

(Weather API integrated for accuracy.)

---

## 🔐 **AUTHENTICATION & USER SYSTEM**

* User registration & login
* Session-based authentication
* User-specific wardrobe storage
* Secure image upload handling

---

# ⚙️ **TECH STACK USED**

| Component            | Technology                     |
| -------------------- | ------------------------------ |
| **Frontend**         | HTML, CSS, JavaScript          |
| **Backend**          | Python + Flask                 |
| **Machine Learning** | TensorFlow / Keras, CNN models |
| **Image Processing** | OpenCV, NumPy, PIL             |
| **Database**         | SQLite                         |
| **API**              | Weather API                    |
| **Deployment Ready** | Render / Railway compatible    |

---

# 📚 **METHODOLOGY**

1. **Requirement analysis**
2. **Data collection** (user-uploaded clothing images)
3. **Image preprocessing**
4. **Training CNN for clothing classification**
5. **Developing Flask application**
6. **Integrating ML with backend**
7. **Database creation (SQLite)**
8. **Weather API integration**
9. **Testing & refinement**
10. **Deployment**

---

# 🗂️ **PROJECT STRUCTURE**

```
SMART-WARDROBE-ASSISTANT/
│── app.py
│── requirements.txt
│── .gitignore
│── model/
│   ├── saved_model.pb
│   ├── variables/
│   └── training.py
│── static/
│   ├── css/
│   ├── js/
│   ├── uploads/ (ignored in Git)
│── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── wardrobe.html
│   ├── recommend.html
│── db_setup.py
│── weather_service.py
│── recognition_module.py
│── pycache/ (ignored)
│── venv/ (ignored)
```

---

# Screen shots of Project 
<img width="1920" height="1140" alt="Screenshot 2025-12-16 200450" src="https://github.com/user-attachments/assets/851bd9f3-df0f-4b10-aef4-29c1c142d112" />
<img width="1920" height="1140" alt="Screenshot 2025-12-16 200456" src="https://github.com/user-attachments/assets/9b09db98-e643-4b87-a4ec-9bc96696c0ec" />

<img width="1920" height="1140" alt="Screenshot 2025-12-16 200503" src="https://github.com/user-attachments/assets/a0c18e77-a40a-4411-94e0-3f43c6195a02" />

<img width="1920" height="1140" alt="Screenshot 2025-12-16 200517" src="https://github.com/user-attachments/assets/0c52967c-7dff-4450-8132-77ea069231c3" />

<img width="1920" height="1140" alt="Screenshot 2025-12-16 200526" src="https://github.com/user-attachments/assets/55de764d-80b6-4019-995a-8fb3be921b85" />

<img width="1920" height="1140" alt="Screenshot 2025-12-16 200540" src="https://github.com/user-attachments/assets/52b02e06-d915-4bf2-8307-05baca7b0c4f" />

<img width="1920" height="1140" alt="Screenshot 2025-12-16 200554" src="https://github.com/user-attachments/assets/dbe753cf-752e-415e-a45c-c994cadcf4c9" />

<img width="1920" height="1140" alt="Screenshot 2025-12-16 200602" src="https://github.com/user-attachments/assets/3efbe2ad-1338-4066-b59c-22c345d40faf" />

<img width="1920" height="1140" alt="Screenshot 2025-12-16 200613" src="https://github.com/user-attachments/assets/6a18c5f4-5d7e-4454-b720-b9c5ad5c8264" />

<img width="1920" height="1140" alt="image" src="https://github.com/user-attachments/assets/9a3df81d-a5fb-482f-ab4b-0e7c8c3f4c52" />

<img width="1920" height="1140" alt="image" src="https://github.com/user-attachments/assets/b6413af4-29a3-464c-9869-11fe55ce0541" />


# 🚀 **HOW TO RUN THE PROJECT**

### **1️⃣ Clone Repo**

```
git clone https://github.com/prajnashreekulal/SMART-WARDROBE-ASSISTANT-AI-POWERED-OUTFIT-RECOMMENDER.git
cd SMART-WARDROBE-ASSISTANT-AI-POWERED-OUTFIT-RECOMMENDER
```

### **2️⃣ Create virtual environment**

```
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate  # Mac/Linux
```

### **3️⃣ Install dependencies**

```
pip install -r requirements.txt
```

### **4️⃣ Initialize database**

```
python db_setup.py
```

### **5️⃣ Run Flask**

```
python app.py
```

### Open in browser:

👉 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

# 📊 **OUTCOMES**

* Saves time picking clothes
* Improves fashion confidence
* Promotes sustainable clothing habits
* Reduces wardrobe clutter
* Ensures weather-appropriate dressing
* Digitizes wardrobe for easy access

---

# 🔮 **FUTURE ENHANCEMENTS**

* Virtual Try-On using GAN
* Advanced color-matching AI
* Trend-based outfit suggestions
* E-commerce integration
* Auto-generating complete “LookBooks”
* Mobile app version

---

# 🧑‍🏫 **TEAM & GUIDE**

* **Anushka (4MW22CS027)**@
* **Gowrika (4MW22CS059)**
* **Krithika (4MW22CS083)**
* **Prajnashree (4MW22CS113)**

**Under Guidance:**
Mr. Raghavendra  I Hegde
Sr. Assistant Professor
Dept. of CSE, SMVITM, Bantakal

---

# 🙏 **ACKNOWLEDGEMENT**

We thank our guide and institution for continuous support and encouragement throughout the completion of this major project.

