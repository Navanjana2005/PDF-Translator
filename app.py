import os
import tempfile
from flask import Flask, render_template_string, request
import PyPDF2
from googletrans import Translator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
         <!DOCTYPE html>
<html>
<head>
    <title>PDF Translator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-image: url(https://img.freepik.com/premium-vector/dark-yellow-background-with-abstract-shape-design_573652-199.jpg?w=1060);
            background-size: cover;
            background-position: center center;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 1000px;
            width: 60%;
            height: auto;
            margin: 0 auto;
            padding: 40px;
            background-color: rgba(255, 255, 255, 0.164);
            border: 10px solid #ffffff;
            border-radius: 30px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            animation: fade-in 2s ease-in-out;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 26px;
        }

        .submit-button {
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            background-color: #ffbb00;
            color: #fff;
            border: none;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: background-color 0.3s ease;
        }

        .submit-button:active {
            background-color: #855b00;
        }

        .submit-button:active::after {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #fff;
            border-top-color: transparent;
            animation: loading 1s infinite linear;
        }

        @keyframes loading {
            0% {
                transform: translate(-50%, -50%) rotate(0deg);
            }
            100% {
                transform: translate(-50%, -50%) rotate(360deg);
            }
        }

        @keyframes fade-in {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
            color: #FF9800;
            animation: slide-up 2s ease-in-out;
        }

        @keyframes slide-up {
            from {
                transform: translateY(50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        form {
            text-align: center;
            margin-bottom: 20px;
        }

        label {
            font-weight: bold;
            display: block;
            margin-bottom: 10px;
            color: #f8e36c;
        }

        input[type="text"],
        input[type="file"] {
            padding: 10px;
            width: 100%;
            max-width: 300px;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #ccc;
            animation: slide-left 2s ease-in-out;
        }

        @keyframes slide-left {
            from {
                transform: translateX(50px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        button[type="submit"] {
            padding: 10px 20px;
            font-size: 30px;
            border-radius: 5px;
            background-color: #FF9800;
            color: #fff;
            border: none;
            cursor: pointer;
            animation: scale-in 2s ease-in-out;
        }

        @keyframes scale-in {
            from {
                transform: scale(0);
            }
            to {
                transform: scale(1);
            }
        }

        .translation {
            background-color: #ff0000;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            animation: fade-in 0.5s ease-in-out;
        }

        h3 {
            margin-top: 0;
            color: #FF9800;
        }

        p {
            margin-bottom: 5px;
        }

        .marquee {
            width: 100%;
            overflow: hidden;
        }

        .marquee p {
            display: inline-block;
            white-space: nowrap;
            font-size: 25px;
            animation: marquee 30s linear infinite;
            color: #fff;
            position: fixed;
            bottom: 0;
            width: 100%;
        }

        @keyframes marquee {
            0% {
                transform: translateX(100%);
            }
            100% {
                transform: translateX(-100%);
            }
        }

        /* Media queries for responsiveness */

        @media only screen and (max-width: 768px) {
            .container {
                width: 90%;
                padding: 20px;
                font-size: 20px;
            }

            input[type="text"],
            input[type="file"] {
                max-width: 100%;
                width: 100%;
                font-size: 14px;
            }

            button[type="submit"] {
                font-size: 24px;
            }

            .marquee p {
                font-size: 20px;
            }
        }

        @media only screen and (max-width: 320px) {
            .container {
                
                width: 70%;
                height: 750px;
                font-size: 40px;
            }

            input[type="text"],
            input[type="file"] {
                max-width: 100%;
                width: 100%;
                font-size: 12px;
            }

            button[type="submit"] {
                font-size: 20px;
            }

            .marquee p {
                font-size: 30px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PDF Translator</h1>
        <form action="/translate" method="POST" enctype="multipart/form-data">
            <label for="language">Target Language:</label>
            <input type="text" id="language" name="language" placeholder="Enter target language">
            <br><br>
            <label for="pdf">PDF File:</label>
            <input type="file" id="pdf" name="pdf">
            <br><br>
            <button type="submit" class="submit-button">Translate</button>
        </form>
    </div>
    <div class="marquee">
        <p>Notice : If there are images in your PDF file, The PDF translator did not work.</p>
    </div>
</body>
</html>

    ''')

@app.route('/translate', methods=['POST'])
def translate():
    trans_lang = request.form['language']
    pdf_file = request.files['pdf']

    # Save the uploaded PDF file to a temporary location
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        pdf_file.save(temp_pdf.name)

    # Open the temporary PDF file in read-binary mode
    with open(temp_pdf.name, 'rb') as file:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)

        # Get the number of pages in the PDF
        num_pages = len(pdf_reader.pages)

        translations = []

        # Iterate over each page and extract the text
        for page_number in range(num_pages):
            # Get the page object
            page = pdf_reader.pages[page_number]

            # Extract text from the page
            text = page.extract_text()

            if text is not None:
                # Define the text you want to translate
                text1 = text

                # Create an instance of the Translator class
                translator = Translator()

                # Detect the source language of the text
                detected_lang = translator.detect(text1).lang

                # Translate the text to the target language
                translated = translator.translate(text1, dest=trans_lang)

                translations.append({
                    'page_number': page_number + 1,
                    'detected_lang': detected_lang,
                    'translated_text': translated.text
                })

    # Remove the temporary PDF file
    os.remove(temp_pdf.name)

    translation_result = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Translation Result</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
            }

            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }

            h1 {
                text-align: center;
                margin-bottom: 30px;
            }

            .translation {
                background-color: #f9f9f9;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                position: relative;
            }

            h3 {
                margin-top: 0;
            }

            p {
                margin-bottom: 5px;
            }

            .copy-button {
                position: absolute;
                top: 10px;
                right: 10px;
                padding: 5px 10px;
                background-color: #FF9800;
                color: #fff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Translation Result</h1>
            '''

    for translation in translations:
        translation_result += '''
            <div class="translation">
                <h3>Page {}</h3>
                <p>Detected Language: {}</p>
                <p>Translated Text: {}</p>
                <button class="copy-button" onclick="copyText(this)">Copy Text</button>
            </div>
        '''.format(translation['page_number'], translation['detected_lang'], translation['translated_text'])

    translation_result += '''
        </div>

        <script>
            function copyText(button) {
                var translationText = button.previousElementSibling.innerHTML;
                var tempTextArea = document.createElement('textarea');
                tempTextArea.value = translationText;
                document.body.appendChild(tempTextArea);
                tempTextArea.select();
                document.execCommand('copy');
                document.body.removeChild(tempTextArea);
                alert('Copied the text: ' + translationText);
            }
        </script>
    </body>
    </html>

    '''

    return render_template_string(translation_result)

if __name__ == '__main__':
    app.run(debug=True)
