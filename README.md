# Document_processing_Automation
OCR + NLP to extract data from invoices, contracts
This Streamlit app allows users to upload images, PDF documents, or Excel files, and extracts their content as clean Markdown text using Together AI’s powerful multimodal model (LLaMA 3.2 - Vision Instruct Turbo).
Features
📸 Image OCR
Upload image files (.png, .jpg, .jpeg, .webp, .gif) and extract structured content such as:

Headings

Paragraphs

Tables

Subtexts and footers

Visual layout retained in Markdown

📄 PDF Document Support
Converts each page of a PDF into images, processes them with Together AI, and generates a markdown section per page.

📊 Excel File Parsing
Reads each sheet in .xlsx or .xls files using pandas, converts tables to markdown using .to_markdown().


TEHNOLOGIES

Python

Streamlit – Interactive UI

Together AI API – Vision-based LLM processing

Pandas – Excel sheet handling

pdf2image – PDF to image conversion (requires Poppler)

PIL – Image manipulation

Base64 + imghdr – File handling
