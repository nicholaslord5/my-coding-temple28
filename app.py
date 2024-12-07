from flask import Flask, request, jsonify, abort
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

# MySQL database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="fitness_center_db"
    )

# Member class to define the structure of the members table
class Member:
    def __init__(self, id, name, email, phone):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone

# Member schema to serialize data
class MemberSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "email", "phone")

# WorkoutSession class to define the structure of workout sessions
class WorkoutSession:
    def __init__(self, id, member_id, date, duration, workout_type):
        self.id = id
        self.member_id = member_id
        self.date = date
        self.duration = duration
        self.workout_type = workout_type

# WorkoutSession schema to serialize data
class WorkoutSessionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ("id", "member_id", "date", "duration", "workout_type")

# Create the Members table in MySQL
def create_members_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(15)
        )
    ''')
    connection.commit()
    connection.close()

# Create the WorkoutSessions table in MySQL
def create_workout_sessions_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS WorkoutSessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            member_id INT,
            date DATE,
            duration INT,
            workout_type VARCHAR(50),
            FOREIGN KEY (member_id) REFERENCES Members(id)
        )
    ''')
    connection.commit()
    connection.close()

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    if not name or not email or not phone:
        return jsonify({"error": "Missing data"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Members (name, email, phone) VALUES (%s, %s, %s)",
                   (name, email, phone))
    connection.commit()
    connection.close()

    return jsonify({"message": "Member added successfully!"}), 201

@app.route('/members', methods=['GET'])
def get_members():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Members")
    members = cursor.fetchall()
    connection.close()

    return jsonify(members)

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Members WHERE id = %s", (id,))
    member = cursor.fetchone()
    connection.close()

    if member:
        return jsonify(member)
    else:
        return jsonify({"error": "Member not found"}), 404

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    if not name or not email or not phone:
        return jsonify({"error": "Missing data"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE Members SET name = %s, email = %s, phone = %s WHERE id = %s",
                   (name, email, phone, id))
    connection.commit()
    connection.close()

    return jsonify({"message": "Member updated successfully!"})

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Members WHERE id = %s", (id,))
    connection.commit()
    connection.close()

    return jsonify({"message": "Member deleted successfully!"})

@app.route('/workouts', methods=['POST'])
def add_workout_session():
    data = request.get_json()
    member_id = data.get('member_id')
    date = data.get('date')
    duration = data.get('duration')
    workout_type = data.get('workout_type')

    if not member_id or not date or not duration or not workout_type:
        return jsonify({"error": "Missing data"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO WorkoutSessions (member_id, date, duration, workout_type) VALUES (%s, %s, %s, %s)",
                   (member_id, date, duration, workout_type))
    connection.commit()
    connection.close()

    return jsonify({"message": "Workout session added successfully!"}), 201

@app.route('/workouts/<int:member_id>', methods=['GET'])
def get_workout_sessions(member_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM WorkoutSessions WHERE member_id = %s", (member_id,))
    sessions = cursor.fetchall()
    connection.close()

    if sessions:
        return jsonify(sessions)
    else:
        return jsonify({"error": "No workout sessions found for this member"}), 404

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout_session(id):
    data = request.get_json()
    date = data.get('date')
    duration = data.get('duration')
    workout_type = data.get('workout_type')

    if not date or not duration or not workout_type:
        return jsonify({"error": "Missing data"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE WorkoutSessions SET date = %s, duration = %s, workout_type = %s WHERE id = %s",
                   (date, duration, workout_type, id))
    connection.commit()
    connection.close()

    return jsonify({"message": "Workout session updated successfully!"})

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout_session(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM WorkoutSessions WHERE id = %s", (id,))
    connection.commit()
    connection.close()

    return jsonify({"message": "Workout session deleted successfully!"})

if __name__ == '__main__':
    create_members_table()
    create_workout_sessions_table()
    app.run(debug=True)
