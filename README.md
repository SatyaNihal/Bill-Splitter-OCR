# Bill Splitter with OCR (Deployed - Streamlit Cloud)

https://bill-splitter-satyanihal.streamlit.app/

A simple web app to split bills among friends by extracting item names and prices from scanned images using OCR.  
Created by **Satya Nihal Kodukula**.

## Features

- Upload bill image and extract text with OCR
- Edit or add item details (name, price, quantity)
- Assign items to people
- Calculate how much each person owes

## Requirements

- Python 3.7+
- Streamlit
- pandas
- Pillow
- pytesseract

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
