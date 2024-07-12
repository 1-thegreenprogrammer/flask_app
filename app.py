from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

uploaded_files = []

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Home</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                padding: 20px;
                font-family: 'Arial', sans-serif;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
                text-align: center;
            }
            .btn-primary {
                background-color: #007bff;
                border-color: #007bff;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0, 123, 255, 0.4);
            }
            .btn-primary:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome</h1>
            <p>Click the button below to go to the form.</p>
            <a href="/form" class="btn btn-primary">Go to Form</a>
        </div>
    </body>
    </html>
    ''')

@app.route('/form')
def form():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload PDF</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                background-color: #f8f9fa;
                padding: 20px;
                font-family: 'Arial', sans-serif;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
            }
            h1 {
                margin-bottom: 30px;
                color: #343a40;
            }
            .form-group label {
                font-weight: bold;
                color: #495057;
            }
            .form-control {
                border-radius: 8px;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            .btn-primary {
                background-color: #007bff;
                border-color: #007bff;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0, 123, 255, 0.4);
            }
            .btn-primary:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            .comment-section {
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center">Upload PDF</h1>
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="name">Name of Content:</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                <div class="form-group">
                    <label for="date">Date:</label>
                    <input type="date" class="form-control" id="date" name="date" required>
                </div>
                <div class="form-group">
                    <label for="pdf">PDF File:</label>
                    <input type="file" class="form-control-file" id="pdf" name="pdf" accept="application/pdf" required>
                </div>
                <div class="form-group">
                    <label for="commentToggle" class="d-block">Comment:</label>
                    <button type="button" id="commentToggle" class="btn btn-secondary" onclick="showCommentSection()">Add a comment</button>
                </div>
                <div class="form-group comment-section" id="commentSection">
                    <textarea class="form-control" id="comment" name="comment" rows="4" required></textarea>
                </div>
                <button type="button" class="btn btn-primary btn-block" onclick="uploadPDF()">Upload</button>
            </form>
        </div>

        <script>
            function showCommentSection() {
                document.getElementById('commentSection').style.display = 'block';
                document.getElementById('commentToggle').style.display = 'none';
                document.getElementById('comment').focus();
            }

            function uploadPDF() {
                const formData = new FormData(document.getElementById('uploadForm'));

                fetch('/upload', {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                  .then(data => {
                      if (data.message === 'File successfully uploaded') {
                          window.location.href = '/uploads';
                      } else {
                          alert('Upload failed: ' + data.message);
                      }
                  })
                  .catch(error => console.error('Error:', error));
            }
        </script>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    </body>
    </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return jsonify(message='No file part'), 400

    pdf = request.files['pdf']
    if pdf.filename == '':
        return jsonify(message='No selected file'), 400

    if pdf and pdf.filename.endswith('.pdf'):
        filename = secure_filename(pdf.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf.save(pdf_path)

        name = request.form['name']
        date = request.form['date']
        comment = request.form['comment']

        # Save the metadata and file path
        uploaded_files.append({
            'name': name,
            'date': date,
            'comment': comment,
            'file_path': pdf_path
        })

        return jsonify(message='File successfully uploaded'), 200
    else:
        return jsonify(message='Invalid file type'), 400

@app.route('/uploads')
def uploads():
    if not uploaded_files:
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>No Uploads</title>
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background-color: #f8f9fa;
                    padding: 20px;
                    font-family: 'Arial', sans-serif;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: auto;
                    text-align: center;
                }
                .btn-primary {
                    background-color: #007bff;
                    border-color: #007bff;
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-size: 16px;
                    font-weight: bold;
                    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.4);
                }
                .btn-primary:hover {
                    background-color: #0056b3;
                    border-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>No uploads yet</h1>
                <p>Please <a href="/form">upload a file</a> first.</p>
            </div>
        </body>
        </html>
        ''')

    latest_upload = uploaded_files[-1]
    return render_template_string(f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Uploaded File Details</title>
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background-color: #f8f9fa;
                padding: 20px;
                font-family: 'Arial', sans-serif;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: auto;
            }}
            h1 {{
                margin-bottom: 30px;
                color: #343a40;
            }}
            .pdf-card {{
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .pdf-card img {{
                max-width: 100%;
                border-radius: 5px;
                margin-bottom: 10px;
            }}
            .pdf-card .pdf-title {{
                font-size: 1.25rem;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .pdf-card .pdf-info {{
                font-size: 0.9rem;
                color: #6c757d;
            }}
            .pdf-card .pdf-comment {{
                margin-top: 15px;
            }}
            .pdf-card a {{
                color: #007bff;
                text-decoration: none;
            }}
            .pdf-card a:hover {{
                text-decoration: underline;
            }}
            .btn-primary {{
                background-color: #007bff;
                border-color: #007bff;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 16px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0, 123, 255, 0.4);
            }}
            .btn-primary:hover {{
                background-color: #0056b3;
                border-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center">Uploaded File Details</h1>
            <div class="pdf-card">
                <div class="pdf-title">{{latest_upload['name']}}</div>
                <div class="pdf-info">Uploaded on {{latest_upload['date']}}</div>
                <a href="{{url_for('static', filename=latest_upload['file_path'])}}" target="_blank">
                    <img src="static/placeholder.png" alt="PDF Preview">
                </a>
                <div class="pdf-comment">{{latest_upload['comment']}}</div>
            </div>
            <a href="/form" class="btn btn-primary btn-block">Upload Another File</a>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
