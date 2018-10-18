
import time
import os
import face_recognition
from flask import Flask, jsonify, request, redirect, g, render_template
from flask_basicauth import BasicAuth
import psycopg2 

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_url_path='/static')

app.config['BASIC_AUTH_USERNAME'] = 'root'
app.config['BASIC_AUTH_PASSWORD'] = 'toor'

basic_auth = BasicAuth(app)


@app.before_request
def before_request():
	g.request_start_time = time.time()
	g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/first', methods=['GET', 'POST'])
#@basic_auth.required
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Fissss</title>
    <h1>reutn face 128d</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''


def detect_faces_in_image(file_stream):
    
    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    face_encodings = face_recognition.face_encodings(img)

    face_found = False
  


    # Return the result as json
    result = {
        "encoding": str(face_encodings),
		"r.time": g.request_time()
    }
    return jsonify(result)
	
def dbin(file_stream, filename):
	file_name = filename
	# Load the uploaded image file
	img = face_recognition.load_image_file(file_stream)
	# Get face encodings for any faces in the uploaded image
	encodings = face_recognition.face_encodings(img)
	if len(encodings) > 1:
		return "Multiple faces not allowed"
	DATABASE_URL = os.environ['DATABASE_URL']
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	db = conn.cursor()
	if len(encodings) > 0:
		query = "INSERT INTO vectors (file, vec_low, vec_high) VALUES ('{}', CUBE(array[{}]), CUBE(array[{}]))".format( file_name, ','.join(str(s) for s in encodings[0][0:64]), ','.join(str(s) for s in encodings[0][64:128]),)
		db.execute(query)
		conn.commit()
		db.close()
		conn.close()
		return "Added into databse"
@app.route('/addface', methods=['GET', 'POST'])
@basic_auth.required
def addface():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
			
        if 'firstname' not in request.form:
            return redirect(request.url)

        file = request.files['file']
        filename = request.form['firstname']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return dbin(file,filename)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Fissss</title>
    <h1>Addd Face (only one face in picture</h1>
    <form method="POST" enctype="multipart/form-data" action="/addface" >
	  <input type="text" name="firstname">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''



# =================================== find face strt V ====================


def dbout(file_stream):

	# Load the uploaded image file
	img = face_recognition.load_image_file(file_stream)
	# Get face encodings for any faces in the uploaded image
	encodings = face_recognition.face_encodings(img)
	if len(encodings) > 1:
		return "Multiple faces not allowed"
	DATABASE_URL = os.environ['DATABASE_URL']
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	db = conn.cursor()
	threshold = 0.6
	if len(encodings) > 0:
		query = "SELECT file FROM vectors WHERE sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) <= {} ".format(
			','.join(str(s) for s in encodings[0][0:64]),
			','.join(str(s) for s in encodings[0][64:128]),
			threshold,
		) + \
				"ORDER BY sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) ASC LIMIT 1".format(
					','.join(str(s) for s in encodings[0][0:64]),
					','.join(str(s) for s in encodings[0][64:128]),
				)
		db.execute(query)
		res = db.fetchone()
		db.close()
		conn.close()
		return res
		
		
		
@app.route('/findface', methods=['GET', 'POST'])
@basic_auth.required
def findface():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
			

        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return dbout(file)

    # If no valid image file was uploaded, show the file upload form:
    return render_template('imgup.html') #render_template('findface.html')


# ===================================find face end==================

@app.route('/', methods=['GET', 'POST'])
def webcam():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'webcam' not in request.files:
            return redirect(request.url)
			

        file = request.files['webcam']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return dbout(file)

    # If no valid image file was uploaded, show the file upload form:
    return render_template('webcambt2.html')
	
	

@app.route('/phone', methods=['GET', 'POST'])
def phone():
	return render_template('phone.html')



if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)