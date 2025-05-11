import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re

def import_items_from_image(uploaded_file):
    items = []

    # 1) PRE-PROCESS
    img = Image.open(uploaded_file).convert("L")
    img = img.point(lambda x: 0 if x < 140 else 255)

    # 2) RUN TESSERACT
    raw = pytesseract.image_to_string(img, config="--psm 6")
    st.text_area("OCR output", raw, height=250)

    # 3) NORMALIZE & EXTRACT “NAME    12.34”
    for line in raw.splitlines():
        line = line.strip()
        # fix cases like “7 99” → “7.99”
        line = re.sub(r'(\d)\s+(?=\d{2}$)', r'\1.', line)
        # capture “item name” + price at EOL
        m = re.search(r"(.+?)\s+(\d+(?:[.,]\d{2}))$", line)
        if m:
            name  = m.group(1).strip()
            price = float(m.group(2).replace(",", "."))
            items.append({"item": name, "price": price, "qty": 1})

    return items

# Main app
def main():
    st.title("Bill Splitter with OCR")

    # 1) Number of people
    num_people = st.number_input(
        "How many people to split the bill amongst?",
        min_value=1, value=2, step=1
    )
    people = [
        st.text_input(f"Name of Person {i+1}", f"Person {i+1}")
        for i in range(num_people)
    ]
    st.markdown("---")

    # 2) Upload + OCR
    uploaded = st.file_uploader(
        "Upload a scanned photo of your bill (Optional)",
        type=["png", "jpg", "jpeg"]
    )
    ocr_items = []
    if uploaded:
        st.info("Running OCR…")
        ocr_items = import_items_from_image(uploaded)
        st.success(f"Imported {len(ocr_items)} line(s)")
        st.info("Please check raw OCR output above - and verify Name, Price and Quantity before proceeding")
    st.markdown("---")

    # 3) Item entry / pre-fill from OCR
    num_items = st.number_input(
        "How many items?",
        min_value=1,
        value=max(1, len(ocr_items)),
        step=1
    )
    items = []
    for i in range(int(num_items)):
        st.write(f"#### Item #{i+1}")
        default = ocr_items[i] if i < len(ocr_items) else {"item": "", "price": 0.0, "qty": 1}
        name  = st.text_input("Item name", value=default["item"], key=f"name_{i}")
        price = st.number_input(
            "Price",
            min_value=0.0,
            format="%.2f",
            value=default["price"],
            key=f"price_{i}"
        )
        qty   = st.number_input(
            "Quantity",
            min_value=1,
            step=1,
            value=default["qty"],
            key=f"qty_{i}"
        )
        if name:
            items.append({"item": name, "price": price, "qty": qty})
    st.markdown("---")

    # 4) Assign shares
    assignment = {}
    for idx, row in enumerate(items):
        cost = row["price"] * row["qty"]
        assignment[row["item"]] = st.multiselect(
            f"{row['item']} — ${row['price']:.2f} ×{row['qty']} = ${cost:.2f}",
            people,
            key=f"share_{idx}"
        )
    st.markdown("---")

    # 5) Split result
    if st.button("Calculate split"):
        results = {p: 0.0 for p in people}
        total   = sum(r["price"] * r["qty"] for r in items)

        for row in items:
            cost    = row["price"] * row["qty"]
            sharers = assignment[row["item"]]
            if sharers:
                share = cost / len(sharers)
                for p in sharers:
                    results[p] += share

        st.write(f"**Total bill:** ${total:.2f}")
        df = pd.DataFrame.from_dict(results, orient="index", columns=["Owed"])
        df["% of Bill"] = (df["Owed"] / total * 100).round(1).astype(str) + "%"
        st.table(df)

if __name__ == "__main__":
    main()