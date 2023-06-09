import re
from flask import Flask, render_template, request, redirect, url_for
from jinja2 import Environment, PackageLoader, select_autoescape

app = Flask(__name__)

# Jinja2 Environment setup
env = Environment(
    loader=PackageLoader(__name__, 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def convert_sml_to_jinja2(template_content):
    # SML to Jinja2 patterns
    sml_patterns = {
        r'%%\[\s*': r'{% ',  # Convert %%[ to {%
        r'\s*\]%%': r' %}',  # Convert ]%% to %}
        r'%%=\s*': r'{{ ',  # Convert %%= to {{
        r'\s*=%%': r' }}',  # Convert =%% to }}
        r'then\s*': r'',  # Remove 'then' with whitespace
        r'not\s*Empty\s*': r'',  # Remove 'not Empty' with space
        # Replace 'set' at the beginning of the line
        r'^\s*set\s+': r'{% set ',
        r'\s*$': r' %}',  # Replace end of line with '%}'
        r'%%(.*?)%%': r'{{ \1 }}',  # Convert %%any_text%% to {{ any_text }}
        r'set @([a-zA-Z_][a-zA-Z0-9_]*) = "(.*)"' : r'{% set \1 = "\2" %}'
        # r'set\s+([^=]+)\s*': r'{% set \1 %}',
        # Add more patterns as needed for other SML to Jinja2 conversions
    }

    # Perform the conversion using regular expressions
    converted_content = template_content
    for pattern, replacement in sml_patterns.items():
        converted_content = re.sub(pattern, replacement, converted_content)

    return converted_content


@app.route('/')
def index():
    return render_template('convert.html')


@app.route('/convert', methods=['POST'])
def convert_template():
    # Get the uploaded file
    uploaded_file = request.files['template']

    # Read the contents of the uploaded file as bytes
    template_content_bytes = uploaded_file.read()

    # Convert the bytes to string
    template_content = template_content_bytes.decode('utf-8')

    # Perform the SML to Jinja2 conversion
    converted_template_content = convert_sml_to_jinja2(template_content)

    # Save the converted template as a file
    with open('static/converted_template.html', 'w') as file:
        file.write(converted_template_content)

    return redirect(url_for('download_template'))


@app.route('/download')
def download_template():
    return redirect(url_for('static', filename='converted_template.html'))


if __name__ == '__main__':
    app.run(debug=True)
