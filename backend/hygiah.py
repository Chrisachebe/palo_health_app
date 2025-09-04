import os
from flask import Flask, jsonify, request
import mysql.connector
from openai import OpenAI
from dotenv import load_dotenv
import traceback
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
    return jsonify({"message": "Data Accessible!"})

# Gets Patient Data
@app.route("/api/patients", methods=["GET"])
def get_patient():
    # Get Date Filter
    date_filter = request.args.get("date")  # e.g., '2025-09-01'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if date_filter:
        # Filter query by date
        query = '''
                SELECT
                    g.Date,
                    g.name,
                    g.age,
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
                    w.`Deadlift Max(lbs)`,
                    w.`Leg Press (lbs)`
                FROM googlefit g
                INNER JOIN myfitnesspal m
                    ON g.Date = m.Date
                INNER JOIN weight_lifts w
                    ON g.Date = w.Date
                WHERE g.Date = %s
                '''
        cursor.execute(query, (date_filter,))
        patients = cursor.fetchall()

    else:
        # Default: return recent records
        cursor.execute('''
            SELECT 
                g.Date,
                g.name,
                g.age,
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
                w.`Deadlift Max(lbs)`,
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

    # --- Average weight per year query ---
    cursor.execute('''
        SELECT 
            YEAR(g.Date) AS year,
            AVG(g.`Weight (lbs)`) AS avg_weight
        FROM googlefit g
        GROUP BY YEAR(g.Date)
        ORDER BY year;
    ''')
    avg_weights = cursor.fetchall()

    cursor.close()
    conn.close()

    # Return both patient data + yearly averages
    return jsonify({
        "patients": patients,
        "average_weights": avg_weights
    })

# Gets AI insights based on input data
@app.route("/api/insights", methods=["GET", "POST"])
def get_insights():
    try:
        # ---------------------------
        # Extract filters
        # ---------------------------
        date_filter = None
        year_filter = None

        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            date_filter = data.get("date")
            year_filter = data.get("year")
        else:  # GET
            date_filter = request.args.get("date")
            year_filter = request.args.get("year")

        if not date_filter and not year_filter:
            return jsonify({"insight": "Awaiting date or year selection."}), 200

        # ---------------------------
        # Query MySQL
        # ---------------------------
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            if date_filter:
                query = """
                    SELECT g.Date, g.name, g.`Calories spent (Kcal)`, g.`Weight (lbs)`,
                           g.`Average heart rate (bpm)`, g.`Inactive duration (hrs)`,
                           g.`Walking Duration (hrs)`, m.`food eaten`, m.`calorie total`,
                           m.`carb(g)`, m.`fat(g)`, m.`protein(g)`, w.`Bench Max(lbs)`,
                           w.`Squat Max(lbs)`, w.`Deadlift Max(lbs)`, w.`Leg Press (lbs)`
                    FROM googlefit g
                    INNER JOIN myfitnesspal m ON g.Date = m.Date
                    INNER JOIN weight_lifts w ON g.Date = w.Date
                    WHERE g.Date = %s
                    LIMIT 1
                """
                cursor.execute(query, (date_filter,))

            elif year_filter:
                query = """
                    SELECT g.Date, g.name, g.`Calories spent (Kcal)`, g.`Weight (lbs)`,
                           g.`Average heart rate (bpm)`, g.`Inactive duration (hrs)`,
                           g.`Walking Duration (hrs)`, m.`food eaten`, m.`calorie total`,
                           m.`carb(g)`, m.`fat(g)`, m.`protein(g)`, w.`Bench Max(lbs)`,
                           w.`Squat Max(lbs)`, w.`Deadlift Max(lbs)`, w.`Leg Press (lbs)`
                    FROM googlefit g
                    INNER JOIN myfitnesspal m ON g.Date = m.Date
                    INNER JOIN weight_lifts w ON g.Date = w.Date
                    WHERE YEAR(g.Date) = %s
                    ORDER BY g.Date ASC
                    LIMIT 10
                """
                cursor.execute(query, (year_filter,))

            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if not rows:
                return jsonify({"insight": "No data found for the selected date/year."}), 200

        except Exception as db_error:
            print("Database error:", traceback.format_exc())
            return jsonify({"error": "Database error. Please try again later."}), 500

        # ---------------------------
        # Call OpenAI
        # ---------------------------
        try:
            prompt = f"""Patient data: {rows}. Start message with 'Warning: I am not a Doctor.' 
            Provide health insights. Keep insight concise and under 200 tokens. 
            Do not return raw numbers in the insight."""

            completion = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a health assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )

            insight_text = completion.choices[0].message.content
            return jsonify({"insight": insight_text}), 200

        except Exception as ai_error:
            print("AI error:", traceback.format_exc())
            return jsonify({
                "insight": "Unable to generate AI insights at this time.",
                "patient_data": rows
            }), 200

    except Exception as e:
        print("Unexpected error in /api/insights:", traceback.format_exc())
        return jsonify({"error": "Internal server error. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)