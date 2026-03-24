import os
from config import input_dir, output_dir, supported_formats
from img_preprocessor import preprocess, extract_text
from clean_text import clean_text
from file_handling import load_file

# crop the header of the first page
def crop_header(pil_image):
    width, height = pil_image.size
    top_crop = int(height * 0.20)
    return pil_image.crop((0, top_crop, width, height))


# process each file
def process_file(filepath):
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]
    print(f"\nProcessing: {filename}")

    pages = load_file(filepath)
    if not pages:
        return

    all_text = []

    for i, pil_image in enumerate(pages):
        print(f"  → Page {i + 1}/{len(pages)}")

        if i == 0:
            pil_image = crop_header(pil_image)

        processed = preprocess(pil_image)
        text = extract_text(processed)
        text = clean_text(text)
        all_text.append(f"--- Page {i + 1} ---\n{text}")

    # Join all pages into one string
    final_text = "\n\n".join(all_text)

    # save output
    output_path = os.path.join(output_dir, f"{name_without_ext}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"  ✓ Saved: {output_path}")

# main function
if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)

    # Collect all supported files from input folder
    all_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if os.path.splitext(f)[1].lower() in supported_formats
    ]

    if not all_files:
        print("No supported files found in inputs folder.")
    else:
        print(f"Found {len(all_files)} file(s) to process.")
        for filepath in all_files:
            process_file(filepath)