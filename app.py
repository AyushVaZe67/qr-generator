from flask import Flask, render_template, request, send_file, url_for
import qrcode
from io import BytesIO
import base64
import os
from datetime import datetime

app = Flask(__name__)

# Configure upload folder for saving QR codes
UPLOAD_FOLDER = 'static/qrcodes'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """Render the main page with QR code generator form"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_qr():
    """Generate QR code based on user input"""
    try:
        # Get data from form
        data = request.form.get('data', '')
        qr_size = int(request.form.get('size', 10))
        border = int(request.form.get('border', 4))
        error_correction = request.form.get('error_correction', 'M')

        if not data:
            return render_template('index.html', error="Please enter some data")

        # Map error correction levels
        error_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }

        # Create QR code instance
        qr = qrcode.QRCode(
            version=None,  # Auto-detect version
            error_correction=error_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=qr_size,
            border=border,
        )

        # Add data to QR code
        qr.add_data(data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO object for base64 encoding
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert to base64 for embedding in HTML
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        # Optional: Save to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qr_{timestamp}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img.save(filepath, 'PNG')

        return render_template('index.html',
                               qr_image=img_base64,
                               qr_filename=filename,
                               qr_data=data,
                               success=True)

    except Exception as e:
        return render_template('index.html', error=f"Error generating QR code: {str(e)}")


@app.route('/download/<filename>')
def download_qr(filename):
    """Download generated QR code"""
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    else:
        return "File not found", 404


@app.route('/generate-advanced', methods=['POST'])
def generate_advanced_qr():
    """Generate QR code with advanced customization options"""
    try:
        data = request.form.get('data', '')
        qr_size = int(request.form.get('size', 10))
        border = int(request.form.get('border', 4))
        fill_color = request.form.get('fill_color', '#000000')
        back_color = request.form.get('back_color', '#ffffff')

        if not data:
            return render_template('index.html', error="Please enter some data")

        # Create QR code
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=qr_size,
            border=border,
        )

        qr.add_data(data)
        qr.make(fit=True)

        # Create image with custom colors
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert to base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        return render_template('index.html',
                               qr_image=img_base64,
                               qr_data=data,
                               success=True,
                               custom_colors=True)

    except Exception as e:
        return render_template('index.html', error=f"Error: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)