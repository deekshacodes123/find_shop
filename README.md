// Nearby Shops Finder Project

This project is designed to collect shop information from Google Maps
using a text-based search and store it in MongoDB.
The system also ensures that duplicate shop data is not stored.

The main goal of this project is to understand how real-world applications
work with web scraping, backend APIs, databases, and secure configuration.


// Project Overview

The user provides a search text such as:
medical shop near Gopalpura Bypass Jaipur

Based on this input, the backend automatically opens Google Maps,
extracts shop details, and stores them in MongoDB Atlas.
If the same shop already exists, it is skipped.


// Key Features

• Text-based shop search (no GPS or live location required)  
• Real-time data scraping from Google Maps using Selenium  
• MongoDB Atlas used for storing shop data  
• Duplicate shop entries are avoided using unique indexes  
• Shop location stored in GeoJSON format  
• Secure handling of MongoDB credentials using environment variables  
• Simple HTML frontend for user interaction  


// How the System Works

• User enters a search query in the HTML page  
• Flask backend receives the request  
• Selenium opens Google Maps with the given query  
• Shop information is extracted:
  • Shop name
  • Category
  • Phone number
  • Address
  • Image
  • Latitude and longitude  
• Data is stored in MongoDB Atlas  
• If a shop already exists, it is skipped automatically  


// Technologies Used

• Frontend: HTML, JavaScript  
• Backend: Python, Flask  
• Web Scraping: Selenium  
• Database: MongoDB Atlas  
• Environment Management: python-dotenv  
• Other Libraries: pymongo, flask-cors, requests  


// Project Structure

• app.py  
  Handles Flask backend logic and API routes  

• google_maps_to_mongodb.py  
  Contains Selenium scraping logic and MongoDB insertion  

• geo_utils.py  
  Helper functions related to location and geocoding  

• index.html  
  Frontend page for user input  

• requirements.txt  
  List of Python dependencies  

• .env  
  Stores MongoDB connection string (not uploaded to GitHub)  

• .gitignore  
  Prevents sensitive files from being committed  



// Environment Setup (Important)

This project uses environment variables to keep database credentials secure.

Steps to configure:

• Create a file named `.env` in the project root folder  
• Add the following line:

  MONGO_URL=your_mongodb_connection_string_here

• Example:

  MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority


// How to Run the Project

• Clone the repository  
• Install dependencies:
  pip install -r requirements.txt  

• Create `.env` file with MongoDB URL  
• Run the Flask application:
  python app.py  

• Open index.html in browser  
• Enter search text and submit  

