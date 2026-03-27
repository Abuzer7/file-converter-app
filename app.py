from flask import Flask, request, render_template
from PIL import Image
import os

app = Flask(__name__)

# -------- FOLDERS --------
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = os.path.join(
    os.path.expanduser("~"),
    "OneDrive",
    "Desktop",
    "Converted_PDFs"
)

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


# -------- TEXT → PDF --------
def convert_txt_to_pdf(input_path, output_path):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(output_path, pagesize=letter)

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    y = 750
    for line in lines:
        c.drawString(50, y, line.strip())
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    c.save()


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

                elif ext == "txt":
                    convert_txt_to_pdf(input_path, output_path)
                    output_files.append(output_path)

                elif ext == "pdf":
                    output_files.append(input_path)

                elif ext in ["docx", "pptx", "xlsx"]:
                    print(f"Office file detected (not converted): {filename}")
                    # future upgrade needed
                    output_files.append(input_path)

                else:
                    print(f"Unsupported: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

        return f"{len(output_files)} files processed. Check folder:\n{OUTPUT_FOLDER}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)