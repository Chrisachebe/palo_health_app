import os
from flask import Flask, jsonify, request
import mysql.connector
from openai import OpenAI
from dotenv import load_dotenv

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load environment variables
load_dotenv()


# creates app instance in Flask
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallbacksecret")


# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        port=os.getenv("MYSQL_PORT"), 
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )
    return conn

# Home page to display
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Health App Backend!"})

# Gets Patient Data
@app.route("/api/patients", methods=["GET"])
def get_patient():
    # Get Date Filter
    date_filter = request.args.get("date")  # e.g., '2025-09-01'

    # Returning Queries
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if date_filter:
        # Filter query by date
        query = '''
                SELECT
                    g.Date,
                    g.name,
                    g.`Calories spent (Kcal)`,
                    g.`Weight (lbs)`,
                    g.`Average heart rate (bpm)`,
                    g.`Inactive duration (hrs)`,
                    g.`Walking Duration (hrs)`,
                    m.`food eaten`,
                    m.`calorie total`,
                    m.`carb(g)`,
                    m.`fat(g)`,
                    m.`protein(g)`,
                    w.`Bench Max(lbs)`,
                    w.`Squat Max(lbs)`,
                    w.`Deadlit Max(lbs)`,
                    w.`Leg Press (lbs)`
                FROM googlefit g
                INNER JOIN myfitnesspal m
                    ON g.Date = m.Date
                INNER JOIN weight_lifts w
                    ON g.Date = w.Date
                WHERE g.Date = %s
                '''
        
        cursor.execute(query, (date_filter,))

    else:
        # regular return of data
        cursor.execute('''
                        SELECT 
                        g.Date,
                        g.name,
                        g.`Calories spent (Kcal)`,
                        g.`Weight (lbs)`,
                        g.`Average heart rate (bpm)`,
                        g.`Inactive duration (hrs)`,
                        g.`Walking Duration (hrs)`,
                        m.`food eaten`,
                        m.`calorie total`,
                        m.`carb(g)`,
                        m.`fat(g)`,
                        m.`protein(g)`,
                        w.`Bench Max(lbs)`,
                        w.`Squat Max(lbs)`,
                        w.`Deadlit Max(lbs)`,
                        w.`Leg Press (lbs)`
                        
                    FROM googlefit g

                    INNER JOIN myfitnesspal m
                        ON g.Date = m.Date
                    INNER JOIN weight_lifts w
                        ON g.Date = w.Date

                    ORDER BY g.Date
                    LIMIT 10;
                       ''')

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(patients)

# Gets AI insights based on input data
@app.route("/api/insights", methods=["GET", "POST"])
def get_insights():
    if request.method == "GET":
        return jsonify({"message": "Send a POST with patient data here."})
    
    elif request.method == "POST":
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        try:
            prompt = f"Patient data: {data}. Provide health insights."
            
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # or gpt-3.5-turbo if you prefer
                messages=[
                    {"role": "system", "content": "You are a health assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            
            insight_text = completion.choices[0].message.content
            return jsonify({"insight": insight_text}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
if __name__ == "__main__":
    app.run(debug=True, port=5000)