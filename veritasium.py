import json
import yt_dlp
import re
import requests
from pathlib import Path
import urllib3
import os
import subprocess
import requests
from urllib3.exceptions import LocationParseError

def get_video_description(video_url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get("description", ""), info.get("title", "video")


def split_description(description, separator="▀▀"):
    parts = description.split(separator)

    segments = []

    for i, part in enumerate(parts, start=1):
        part = part.strip()

        if not part:
            continue

        # If a single ▀ exists, keep only the text after its first occurrence
        if "▀" in part:
            part = part.split("▀", 1)[1].strip()

        segments.append({
            "segment_number": i,
            "text": part
        })

    return segments
    parts = [part.strip() for part in description.split(separator)]

    segments = []
    for i, part in enumerate(parts, start=1):
        if part:
            segments.append({
                "segment_number": i,
                "text": part
            })

    return segments


def save_to_json(video_title, video_url, segments):
    data = {
        "video_title": video_title,
        "video_url": video_url,
        "total_segments": len(segments),
        "segments": segments
    }

    filename = "description_segments.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"\nSaved {len(segments)} segments to '{filename}'")


def main():
    video_url = input("Enter YouTube video URL: ").strip()

    try:
        description, title = get_video_description(video_url)

        if not description:
            print("No description found.")
            return

        segments = split_description(description)

        save_to_json(title, video_url, segments)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()

############################################################
import json
import re


JSON_FILE = "description_segments.json"
OUTPUT_MD = "selected_segments.md"


# ----------------------------
# Load JSON
# ----------------------------
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

segments = data["segments"]
video_url = data.get("video_url", "")


# ----------------------------
# Markdown writer
# ----------------------------
def append_markdown(text):
    with open(OUTPUT_MD, "a", encoding="utf-8") as f:
        f.write(text.strip())
        f.write("\n\n")
       # f.write("\n\n---\n\n")


# Clear previous file
#open(OUTPUT_MD, "w", encoding="utf-8").close()
with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    if video_url:
        f.write(f"youtube url: [{video_url}]({video_url})\n\n")

# ----------------------------
# Regex
# ----------------------------
reference_pattern = re.compile(r"\breferences?\b", re.IGNORECASE)

special_pattern = re.compile(
    r"\bpatreon\b|\bwritten\s+by\b|\bsponsored\b",
    re.IGNORECASE,
)


reference_segments = []
special_segments = []
normal_segments = []


# ----------------------------
# Categorize
# ----------------------------
for seg in segments:
    text = seg["text"]

    if reference_pattern.search(text):
        reference_segments.append(seg)

    elif special_pattern.search(text):
        special_segments.append(seg)

    else:
        normal_segments.append(seg)


# =====================================================
# 1. Reference Segments
# =====================================================

print("\n========== Reference Segments ==========\n")

for seg in reference_segments:

    print("=" * 80)
    print(f"Segment #{seg['segment_number']}\n")

    # Display the entire segment
    print(seg["text"])

    choice = input("\nPress ENTER to include, anything else to skip: ")

    if choice == "":
        append_markdown(seg["text"])

# Add heading for all non-reference content
with open(OUTPUT_MD, "a", encoding="utf-8") as f:
    f.write("## Others:\n\n")

# =====================================================
# 2. Patreon / Written by / Sponsored
# =====================================================

if special_segments:

    print("\n========== Special Segments ==========\n")

    for i, seg in enumerate(special_segments, 1):
        print(f"[{i}] Original Segment #{seg['segment_number']}")
        print("-" * 60)
        print(seg["text"])
        print("\n")

    selection = input(
        "Press ENTER to skip all\n"
        "or type numbers separated by spaces (e.g. 1 3): "
    )

    if selection.strip():

        chosen = {
            int(x)
            for x in selection.split()
            if x.isdigit()
        }

        for i, seg in enumerate(special_segments, 1):
            if i in chosen:
                append_markdown(seg["text"])


# =====================================================
# 3. Remaining Segments
# =====================================================

if normal_segments:

    print("\n========== Remaining Segments ==========\n")

    for i, seg in enumerate(normal_segments, 1):
        print(f"[{i}] Original Segment #{seg['segment_number']}")
        print("-" * 60)
        print(seg["text"])
        print("\n")

    selection = input(
        "Press ENTER to skip all\n"
        "or type numbers separated by spaces (e.g. 2 4 7): "
    )

    if selection.strip():

        chosen = {
            int(x)
            for x in selection.split()
            if x.isdigit()
        }

        for i, seg in enumerate(normal_segments, 1):
            if i in chosen:
                append_markdown(seg["text"])


print(f"\nDone! Markdown saved to '{OUTPUT_MD}'.")

##################################################




with open(OUTPUT_MD, "r", encoding="utf-8") as f:
    text = f.read()

pattern = r'https?://ve42\.co/([^\s)\]]+)'

matches = re.finditer(pattern, text)

for match in matches:
    path = match.group(1)

    # Check whether the path contains "ref" or "refs" (case-insensitive)
    if re.search(r"refs?", path, re.IGNORECASE):
        new_name = f"{path}.md"

        # Rename the existing files
        os.rename(OUTPUT_MD, new_name)

        # Update the variable to the new filename
        OUTPUT_MD = new_name

       

        break  # Stop after the first matching URL

if(OUTPUT_MD != "selected_segments.md"):
  INPUT_MD = OUTPUT_MD
else:
  INPUT_MD = "selected_segments.md"

################################################


def resolve_url(url):
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )
        return response.url
    except requests.RequestException:
        print(f"Could not resolve: {url}")
        return url


with open(INPUT_MD, "r", encoding="utf-8") as f:
    text = f.read()

# Match any ve42 URL
pattern = r'https?://[^\s)\]]*ve42[^\s)\]]*'

cache = {}


def replace(match):
    url = match.group(0)

    if url not in cache:
        print(f"Resolving: {url}")
        cache[url] = resolve_url(url)

    return cache[url]


new_text = re.sub(pattern, replace, text)

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(new_text)

print(f"\nDone! Saved to {OUTPUT_MD}")

####################################################

import re
import requests


def google_doc_to_export_url(url: str) -> str | None:
    match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        return None

    doc_id = match.group(1)
    return f"https://docs.google.com/document/d/{doc_id}/export?format=md"


def download_markdown(export_url: str) -> str:
    response = requests.get(export_url, timeout=30)
    response.raise_for_status()
    return response.text.strip()


def fetch_google_doc(url: str) -> str | None:
    export_url = google_doc_to_export_url(url)
    if not export_url:
        return None
    try:
        return download_markdown(export_url)
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


def replace_google_docs(markdown_text: str) -> str:
    # 1. Match markdown links: [text](url)
    md_link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")

    # 2. Match raw URLs
    url_pattern = re.compile(r"https?://[^\s\)]+")  # stops at space or )

    # --- Step 1: replace markdown links ---
    def md_replacer(match):
        text, url = match.group(1), match.group(2)

        if "docs.google" not in url:
            return match.group(0)

        content = fetch_google_doc(url)
        if content:
            return f"\n\n{content}\n\n"

        return match.group(0)

    markdown_text = md_link_pattern.sub(md_replacer, markdown_text)

    # --- Step 2: replace raw URLs ---
    def url_replacer(match):
        url = match.group(0)

        if "docs.google" not in url:
            return url

        content = fetch_google_doc(url)
        if content:
            return f"\n\n{content}\n\n"

        return url

    markdown_text = url_pattern.sub(url_replacer, markdown_text)

    return markdown_text


def process_file(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        markdown = f.read()

    result = replace_google_docs(markdown)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Saved output to {output_file}")


if __name__ == "__main__":
   
    process_file(OUTPUT_MD, OUTPUT_MD)



#####################################################


def is_inside_markdown_link(text, start_idx):
    """
    Improved check:
    Ensures we are NOT inside an existing [text](url) structure.
    """
    # Look backwards for nearest '['
    open_bracket = text.rfind('[', 0, start_idx)
    if open_bracket == -1:
        return False

    # Look for "](" after it
    mid = text.find('](', open_bracket)
    if mid == -1:
        return False

    # Closing ')'
    close = text.find(')', mid)
    if close == -1:
        return False

    return open_bracket <= start_idx <= close


def convert_links(line):
    """
    Convert ALL plain URLs into Markdown links.
    Keeps existing markdown links untouched.
    """

    # Matches ANY URL (but NOT inside markdown already)
    pattern = re.compile(r'(https?://[^\s\)\]]+|ve42\.co/[^\s\)\]]+)')

    result = []
    last_index = 0

    for match in pattern.finditer(line):
        url = match.group()
        start, end = match.span()

        result.append(line[last_index:start])

        # Skip if already inside markdown link
        if is_inside_markdown_link(line, start):
            result.append(url)
        else:
            # keep your rule: ve42 may not have http/https
            if url.startswith("ve42.co"):
                full_url = "http://" + url
            else:
                full_url = url

            # convert to markdown link format
            result.append(f"[{url}]({full_url})")

        last_index = end

    result.append(line[last_index:])
    return "".join(result)


def process_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    processed = [convert_links(line) for line in lines]

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(processed)

    print(f"Done. Output saved to: {output_path}")


if __name__ == "__main__":
    # overwrite if no output given

    process_file(OUTPUT_MD, OUTPUT_MD)

#####################################################

# INPUT_MD = "selected_segments.md"
# OUTPUT_MD = "selected_segments.md"



def resolve_url(url):
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        return response.url

    except LocationParseError:
        print(f"LocationParseError (invalid URL format): {url}")
        return url

    except requests.RequestException:
        print(f"Could not resolve: {url}")
        return url

with open(INPUT_MD, "r", encoding="utf-8") as f:
    text = f.read()

# Match any ve42 URL
pattern = r'https?://[^\s)\]]*ve42[^\s)\]]*'

cache = {}


def replace(match):
    url = match.group(0)

    if url not in cache:
        print(f"Resolving: {url}")
        cache[url] = resolve_url(url)

    return cache[url]


new_text = re.sub(pattern, replace, text)

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(new_text)

print(f"\nDone! Saved to {OUTPUT_MD}")

#################################################

with open(OUTPUT_MD, "r", encoding="utf-8") as f:
    content = f.read()

# Replace [text](url) -> [url](url)
pattern = r'\[([^\]]+)\]\(([^)]+)\)'

def replacer(match):
    url = match.group(2)
    return f'[{url}]({url})'

updated_content = re.sub(pattern, replacer, content)

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("Markdown updated successfully.")


################################################
import subprocess

uri = (
    f'obsidian://adv-uri?filepath={OUTPUT_MD}'
    f'&commandid=workspace%3Aexport-pdf&confirm=true'
)

# --- Pause for user confirmation ---
while True:
    choice = input("Do you want to change anything in the Markdown file? (yes/no): ").strip().lower()

    if choice in ["yes", "y"]:
        print("\nMake your changes to the Markdown file.")
        input("Press Enter when you're ready to proceed with export...")
        break

    elif choice in ["no", "n"]:
        break

    else:
        print("Please enter 'yes' or 'no'.")

# --- Proceed with export ---
subprocess.run(["xdg-open", uri], check=True)
print("SUCCESS")