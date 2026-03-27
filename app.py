from flask import Flask, request, render_template, send_file
from PIL import Image
import os
import zipfile

app = Flask(__name__)

# -------- FOLDERS --------
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# -------- IMAGE → PDF --------
def convert_image_to_pdf(input_path, output_path):
    image = Image.open(input_path)
    images = []

    try:
        while True:
            images.append(image.convert("RGB"))
            image.seek(image.tell() + 1)
    except EOFError:
        pass

    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:])


# -------- MAIN ROUTE --------
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":

        files = request.files.getlist("file")
        output_files = []

        for file in files:
            if file.filename == "":
                continue

            filename = file.filename

            # Save uploaded file
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_path)

            ext = filename.lower().split('.')[-1]

            output_path = os.path.join(
                OUTPUT_FOLDER,
                filename.rsplit('.', 1)[0] + ".pdf"
            )

            print("Processing:", filename)

            try:
                if ext in ["tif", "tiff", "png", "jpg", "jpeg"]:
                    convert_image_to_pdf(input_path, output_path)
                    output_files.append(output_path)

                elif ext == "pdf":
                    output_files.append(input_path)

                else:
                    print(f"Skipped: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

        # -------- CREATE ZIP --------
        zip_path = os.path.join(OUTPUT_FOLDER, "converted_files.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in output_files:
                if os.path.exists(file):
                    zipf.write(file, os.path.basename(file))

        return send_file(zip_path, as_attachment=True)

    return render_template("index.html")


# -------- RUN FOR RENDER --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
