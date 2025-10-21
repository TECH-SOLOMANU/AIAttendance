from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import cv2
import numpy as np
import os
from datetime import datetime, timedelta
import base64
import pickle
import json
import pandas as pd
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get environment variables
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'ai_attendance')
PORT = int(os.environ.get('PORT', 5000))

# MongoDB setup - make it optional for testing
try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    db = client[DATABASE_NAME]
    students_col = db['students']
    attendance_col = db['attendance']
    print("✅ MongoDB connected successfully")
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("📝 Will store data in local files for testing")
    client = None
    db = None
    students_col = None
    attendance_col = None

# Create uploads directory for storing reference images
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize OpenCV face detector
try:
    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    print(f"🔍 Loading face cascade from: {face_cascade_path}")
    
    if os.path.exists(face_cascade_path):
        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        print("✅ Face cascade loaded successfully")
    else:
        print("❌ Face cascade file not found")
        face_cascade = None
except Exception as e:
    print(f"❌ Error loading face cascade: {e}")
    face_cascade = None

def extract_face_features(image_path):
    """Extract face features from an image"""
    try:
        print(f"🔍 Loading image: {image_path}")
        
        if face_cascade is None:
            print("❌ Face cascade not loaded")
            return None
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return None
            
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Could not read image: {image_path}")
            return None
            
        print(f"✅ Image loaded: {img.shape}")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print(f"✅ Converted to grayscale: {gray.shape}")
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        print(f"🔍 Detected {len(faces)} faces")
        
        if len(faces) > 0:
            (x, y, w, h) = faces[0]  # Take the first detected face
            print(f"👤 Face found at: x={x}, y={y}, w={w}, h={h}")
            
            face_roi = gray[y:y+h, x:x+w]
            # Resize to standard size for comparison
            face_roi = cv2.resize(face_roi, (100, 100))
            print(f"✅ Face ROI resized to: {face_roi.shape}")
            
            return face_roi.flatten()
        else:
            print("❌ No faces detected in image")
            return None
            
    except Exception as e:
        print(f"💥 Error in extract_face_features: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_faces(face1_features, face2_features, threshold=0.7):
    """Compare two face feature vectors"""
    if face1_features is None or face2_features is None:
        return False
    
    # Convert to numpy arrays if they're lists
    if isinstance(face1_features, list):
        face1_features = np.array(face1_features)
    if isinstance(face2_features, list):
        face2_features = np.array(face2_features)
    
    # Calculate similarity using normalized correlation
    correlation = np.corrcoef(face1_features, face2_features)[0, 1]
    return correlation > threshold

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'status': 'Server is working!', 'message': 'API is accessible'})

@app.route('/test-register', methods=['POST'])
def test_register():
    """Simple test endpoint for registration without face processing"""
    try:
        print("🧪 Test registration endpoint called")
        data = request.json
        print(f"📝 Received data: {data}")
        return jsonify({'success': True, 'message': 'Test registration endpoint working', 'data': data})
    except Exception as e:
        print(f"❌ Test registration error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/register', methods=['POST'])
def register_student():
    """Register a new student with face image"""
    try:
        print("=== Registration request received ===")
        
        # Check if request has JSON data
        if not request.is_json:
            print("❌ Request is not JSON")
            return jsonify({'success': False, 'error': 'Request must be JSON'})
        
        data = request.json
        print(f"📝 Received data keys: {list(data.keys()) if data else 'None'}")
        
        if not data:
            print("❌ No data received")
            return jsonify({'success': False, 'error': 'No data received'})
            
        student_name = data.get('name')
        roll_number = data.get('roll')
        image_data = data.get('image')
        
        print(f"👤 Name: {student_name}")
        print(f"🎫 Roll: {roll_number}")
        print(f"📷 Image data length: {len(image_data) if image_data else 0}")
        
        if not all([student_name, roll_number, image_data]):
            missing = []
            if not student_name: missing.append('name')
            if not roll_number: missing.append('roll')
            if not image_data: missing.append('image')
            print(f"❌ Missing fields: {missing}")
            return jsonify({'success': False, 'error': f'Missing required fields: {missing}'})
        
        # Check if student is already registered
        print(f"🔍 Checking if roll number {roll_number} already exists...")
        if students_col is not None:
            existing_student = students_col.find_one({'roll': roll_number})
            if existing_student:
                print(f"❌ Student {roll_number} already registered")
                return jsonify({'success': False, 'error': f'Student with roll number {roll_number} is already registered!'})
        else:
            # Check local file for duplicates
            local_db_path = 'local_students.json'
            if os.path.exists(local_db_path):
                with open(local_db_path, 'r') as f:
                    students = json.load(f)
                    for student in students:
                        if student.get('roll') == roll_number:
                            print(f"❌ Student {roll_number} already registered (local)")
                            return jsonify({'success': False, 'error': f'Student with roll number {roll_number} is already registered!'})
        
        print(f"✅ Roll number {roll_number} is available")
        
        # Check if this face is already registered with a different roll number
        print(f"🔍 Checking if this face is already registered...")
        captured_features = None
        
        # Save temp image first to extract features for comparison
        temp_image_path = os.path.join(UPLOAD_FOLDER, f"temp_{roll_number}.jpg")
        try:
            image_bytes = base64.b64decode(image_data.split(',')[1])
            with open(temp_image_path, 'wb') as f:
                f.write(image_bytes)
            
            captured_features = extract_face_features(temp_image_path)
            if captured_features is None:
                os.remove(temp_image_path) if os.path.exists(temp_image_path) else None
                return jsonify({'success': False, 'error': 'No face detected in the image'})
        except Exception as img_error:
            print(f"❌ Temp image error: {img_error}")
            return jsonify({'success': False, 'error': f'Failed to process image: {str(img_error)}'})
        
        # Check against existing faces
        if students_col is not None:
            existing_students = list(students_col.find())
        else:
            local_db_path = 'local_students.json'
            existing_students = []
            if os.path.exists(local_db_path):
                with open(local_db_path, 'r') as f:
                    existing_students = json.load(f)
        
        for existing_student in existing_students:
            try:
                if 'encodings' in existing_student and existing_student['encodings']:
                    stored_encodings = existing_student['encodings'][0]  # Get first encoding
                    
                    # Compare faces
                    if compare_faces(captured_features, stored_encodings, threshold=0.8):  # High threshold for registration
                        os.remove(temp_image_path) if os.path.exists(temp_image_path) else None
                        print(f"❌ Face already registered with roll {existing_student['roll']}")
                        return jsonify({
                            'success': False, 
                            'error': f'This face is already registered with roll number {existing_student["roll"]} ({existing_student["name"]})'
                        })
            except Exception as e:
                print(f"⚠️ Error comparing with student {existing_student.get('roll', 'unknown')}: {e}")
                continue
        
        print(f"✅ Face is unique - proceeding with registration")
        
        # Clean up temp file and proceed with normal registration
        os.remove(temp_image_path) if os.path.exists(temp_image_path) else None
        
        # Check if image_data has proper format
        if ',' not in image_data:
            print("❌ Invalid image format - no comma separator")
            return jsonify({'success': False, 'error': 'Invalid image format'})
        
        # Save the reference image
        image_path = os.path.join(UPLOAD_FOLDER, f"{roll_number}.jpg")
        print(f"💾 Saving image to: {image_path}")
        
        try:
            # Decode base64 image and save
            image_bytes = base64.b64decode(image_data.split(',')[1])
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            print(f"✅ Image saved successfully ({len(image_bytes)} bytes)")
        except Exception as img_error:
            print(f"❌ Image save error: {img_error}")
            return jsonify({'success': False, 'error': f'Failed to save image: {str(img_error)}'})
        
        # Extract face features and save them as encodings
        print("🔍 Extracting face features for storage...")
        try:
            # We already extracted features for comparison, now save the image properly
            image_path = os.path.join(UPLOAD_FOLDER, f"{roll_number}.jpg")
            image_bytes = base64.b64decode(image_data.split(',')[1])
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            # Use the already extracted features
            face_features = captured_features
            print(f"✅ Face features ready: {len(face_features)} features")
        except Exception as face_error:
            print(f"❌ Face storage error: {face_error}")
            return jsonify({'success': False, 'error': f'Face processing failed: {str(face_error)}'})
        
        # Convert numpy array to list for JSON storage
        encodings = [face_features.tolist()]
        print(f"📊 Encodings prepared: {len(encodings[0])} values")
        
        # Store student info in MongoDB with your specified format
        student_data = {
            'roll': roll_number,
            'name': student_name,
            'encodings': encodings,
            'registered_at': datetime.now().isoformat() + 'Z'
        }
        
        print(f"💾 Storing to database...")
        
        # Store in MongoDB if available, otherwise store locally
        if students_col is not None:
            try:
                students_col.insert_one(student_data)
                print("✅ Stored in MongoDB")
            except Exception as db_error:
                print(f"❌ MongoDB error: {db_error}")
                return jsonify({'success': False, 'error': f'Database error: {str(db_error)}'})
        else:
            try:
                # Store in local JSON file as fallback
                local_db_path = 'local_students.json'
                students = []
                
                if os.path.exists(local_db_path):
                    with open(local_db_path, 'r') as f:
                        students = json.load(f)
                
                students.append(student_data)
                
                with open(local_db_path, 'w') as f:
                    json.dump(students, f, indent=2)
                
                print("✅ Stored in local file")
            except Exception as file_error:
                print(f"❌ File storage error: {file_error}")
                return jsonify({'success': False, 'error': f'Storage error: {str(file_error)}'})
        
        print("🎉 Registration completed successfully")
        return jsonify({'success': True, 'message': 'Student registered successfully'})
        
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/check-registration', methods=['POST'])
def check_registration():
    """Check if a student is already registered"""
    try:
        data = request.json
        roll_number = data.get('roll')
        
        if not roll_number:
            return jsonify({'success': False, 'error': 'Roll number is required'})
        
        # Check if student exists
        if students_col is not None:
            existing_student = students_col.find_one({'roll': roll_number})
            if existing_student:
                return jsonify({
                    'success': True, 
                    'exists': True, 
                    'student': {
                        'name': existing_student['name'],
                        'roll': existing_student['roll'],
                        'registered_at': existing_student['registered_at']
                    }
                })
        else:
            # Check local file
            local_db_path = 'local_students.json'
            if os.path.exists(local_db_path):
                with open(local_db_path, 'r') as f:
                    students = json.load(f)
                    for student in students:
                        if student.get('roll') == roll_number:
                            return jsonify({
                                'success': True, 
                                'exists': True, 
                                'student': {
                                    'name': student['name'],
                                    'roll': student['roll'],
                                    'registered_at': student['registered_at']
                                }
                            })
        
        return jsonify({'success': True, 'exists': False})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/recognize', methods=['POST'])
def recognize_face():
    """Recognize face and mark attendance"""
    try:
        data = request.json
        image_data = data.get('image')  # Base64 encoded image
        
        # Save captured image temporarily
        temp_image_path = 'temp_capture.jpg'
        image_bytes = base64.b64decode(image_data.split(',')[1])
        with open(temp_image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Extract features from captured image
        captured_features = extract_face_features(temp_image_path)
        if captured_features is None:
            return jsonify({'success': False, 'message': 'No face detected in captured image'})
        
        # Get all registered students
        if students_col is not None:
            students = list(students_col.find())
            print(f"Found {len(students)} students in MongoDB")
        else:
            # Load from local file
            local_db_path = 'local_students.json'
            if os.path.exists(local_db_path):
                with open(local_db_path, 'r') as f:
                    students = json.load(f)
                print(f"Found {len(students)} students in local file")
            else:
                students = []
                print("No students found - database empty")
        
        recognized_student = None
        for student in students:
            try:
                # Get stored encodings (first encoding from the array)
                stored_encodings = student['encodings'][0]  # Get first encoding
                
                # Compare faces using OpenCV
                if compare_faces(captured_features, stored_encodings):
                    recognized_student = student
                    break
                    
            except Exception as e:
                continue  # Skip if encodings not found or corrupted
        
        # Clean up temp file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        if recognized_student:
            # Mark attendance
            attendance_data = {
                'roll': recognized_student['roll'],  # Changed from student_id to roll
                'name': recognized_student['name'],
                'timestamp': datetime.now().isoformat() + 'Z',  # ISO format
                'status': 'present'
            }
            
            # Store attendance
            if attendance_col is not None:
                attendance_col.insert_one(attendance_data)
                print("✅ Attendance stored in MongoDB")
            else:
                # Store in local file
                local_attendance_path = 'local_attendance.json'
                attendance_records = []
                
                if os.path.exists(local_attendance_path):
                    with open(local_attendance_path, 'r') as f:
                        attendance_records = json.load(f)
                
                attendance_records.append(attendance_data)
                
                with open(local_attendance_path, 'w') as f:
                    json.dump(attendance_records, f, indent=2)
                
                print("✅ Attendance stored in local file")
            
            return jsonify({
                'success': True, 
                'student_name': recognized_student['name'],
                'roll': recognized_student['roll'],  # Changed from student_id to roll
                'message': 'Attendance marked successfully'
            })
        else:
            return jsonify({'success': False, 'message': 'Student not recognized'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attendance_report')
def attendance_report():
    """Get attendance report for today"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's attendance records
        attendance_records = list(attendance_col.find({
            'timestamp': {
                '$gte': datetime.strptime(today, '%Y-%m-%d'),
                '$lt': datetime.strptime(today, '%Y-%m-%d') + timedelta(days=1)
            }
        }))
        
        return jsonify({'success': True, 'records': attendance_records})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export/students/<format>')
def export_students(format):
    """Export students data to Excel or CSV"""
    try:
        print(f"📊 Exporting students data to {format.upper()}")
        
        # Get all students data
        if students_col is not None:
            students = list(students_col.find({}, {'_id': 0}))  # Exclude MongoDB _id field
            print(f"Found {len(students)} students in MongoDB")
        else:
            # Load from local file
            local_db_path = 'local_students.json'
            if os.path.exists(local_db_path):
                with open(local_db_path, 'r') as f:
                    students = json.load(f)
                print(f"Found {len(students)} students in local file")
            else:
                students = []
                print("No students found")
        
        if not students:
            return jsonify({'success': False, 'error': 'No student data to export'})
        
        # Prepare data for export (exclude encodings for readability)
        export_data = []
        for student in students:
            export_data.append({
                'Roll Number': student.get('roll', ''),
                'Name': student.get('name', ''),
                'Registration Date': student.get('registered_at', ''),
                'Encodings Count': len(student.get('encodings', [[]])[0]) if student.get('encodings') else 0
            })
        
        # Create DataFrame
        df = pd.DataFrame(export_data)
        
        if format.lower() == 'excel':
            # Export to Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Students', index=False)
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=f'students_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        elif format.lower() == 'csv':
            # Export to CSV
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=f'students_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mimetype='text/csv'
            )
        
        else:
            return jsonify({'success': False, 'error': 'Invalid format. Use "excel" or "csv"'})
    
    except Exception as e:
        print(f"❌ Export error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export/attendance/<format>')
def export_attendance(format):
    """Export attendance data to Excel or CSV"""
    try:
        print(f"📊 Exporting attendance data to {format.upper()}")
        
        # Get all attendance data
        if attendance_col is not None:
            attendance_records = list(attendance_col.find({}, {'_id': 0}))  # Exclude MongoDB _id field
            print(f"Found {len(attendance_records)} attendance records in MongoDB")
        else:
            # Load from local file
            local_attendance_path = 'local_attendance.json'
            if os.path.exists(local_attendance_path):
                with open(local_attendance_path, 'r') as f:
                    attendance_records = json.load(f)
                print(f"Found {len(attendance_records)} attendance records in local file")
            else:
                attendance_records = []
                print("No attendance records found")
        
        if not attendance_records:
            return jsonify({'success': False, 'error': 'No attendance data to export'})
        
        # Prepare data for export
        export_data = []
        for record in attendance_records:
            # Parse timestamp
            timestamp = record.get('timestamp', '')
            if timestamp:
                try:
                    # Convert ISO format to readable format
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date = dt.strftime('%Y-%m-%d')
                    time = dt.strftime('%H:%M:%S')
                except:
                    date = timestamp
                    time = ''
            else:
                date = ''
                time = ''
            
            export_data.append({
                'Roll Number': record.get('roll', ''),
                'Name': record.get('name', ''),
                'Date': date,
                'Time': time,
                'Status': record.get('status', 'present').title()
            })
        
        # Create DataFrame
        df = pd.DataFrame(export_data)
        
        # Sort by date and time
        df = df.sort_values(['Date', 'Time'], ascending=[False, False])
        
        if format.lower() == 'excel':
            # Export to Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Attendance', index=False)
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=f'attendance_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        elif format.lower() == 'csv':
            # Export to CSV
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name=f'attendance_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mimetype='text/csv'
            )
        
        else:
            return jsonify({'success': False, 'error': 'Invalid format. Use "excel" or "csv"'})
    
    except Exception as e:
        print(f"❌ Export error: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ...existing code for registration, recognition, attendance marking...

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=PORT)
