import streamlit as st
from together import Together
import base64
import os
import imghdr
from pdf2image import convert_from_bytes
import pandas as pd
from PIL import Image
import tempfile

# Initialize Together API key
api_key = "0e4bf9de4a44967c7b8704363b972acff4bf52047782c0411e27d7ade8333c52"

# Class to process files
class FileProcessor:
    def __init__(self, api_key):
        self.client = Together(api_key=api_key)
        self.prompt = (
            "Convert the provided image into Markdown format.\n"
            "Ensure that all page content is included, such as headers, footers, subtexts, images (with alt text if possible), tables, and any other elements.\n\n"
            "Requirements:\n"
            "- Markdown only output: return only the Markdown content without any additional explanations or comments.\n"
            "- No Delimiters: Do not use code boundaries or delimiters like ```markdown.\n"
            "- Complete Content: Do not omit any part of the page, including headers, footers, and subtext.\n"
        )
        self.model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"

    def get_mime_type(self, image_path):
        img_type = imghdr.what(image_path)
        if img_type:
            return f'image/{img_type}'
        ext = os.path.splitext(image_path)[1].lower()
        return {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')

    def encode_image(self, image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def analyze_image(self, image_path):
        base64_image = self.encode_image(image_path)
        mime_type = self.get_mime_type(image_path)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"}}
                    ]
                }
            ],
            stream=True,
        )

        response_text = ""
        for chunk in stream:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    response_text += delta.content
        return response_text 

# UI
st.title("Document Processing Automation:NLP and OCR to extract data from invoices, contract")

uploaded_file = st.file_uploader("Upload Image / PDF / Excel", type=["png", "jpg", "jpeg", "gif", "webp", "pdf", "xlsx", "xls"])

if api_key and uploaded_file:
    with st.spinner("Processing..."):
        try:
            processor = FileProcessor(api_key)

            suffix = os.path.splitext(uploaded_file.name)[1].lower()

            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            result_markdown = ""

            if suffix in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                result_markdown = processor.analyze_image(temp_path)

            elif suffix == ".pdf":
                images = convert_from_bytes(open(temp_path, "rb").read())
                for idx, img in enumerate(images):
                    img_path = f"page_{idx}.jpg"
                    img.save(img_path, "JPEG")
                    result_markdown += f"\n\n### Page {idx + 1}\n"
                    result_markdown += processor.analyze_image(img_path)
                    os.remove(img_path)

            elif suffix in [".xlsx", ".xls"]:
                df_dict = pd.read_excel(temp_path, sheet_name=None)
                for sheet_name, df in df_dict.items():
                    result_markdown += f"\n\n### Sheet: {sheet_name}\n"
                    result_markdown += df.to_markdown(index=False)

            st.success("Processing complete!")
            st.text_area("Markdown Output", result_markdown, height=400)

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
