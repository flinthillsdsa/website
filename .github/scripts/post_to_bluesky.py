import os
import yaml
import glob
import requests
from atproto import Client, models

TRACKING_FILE = ".bluesky_posted"

def extract_frontmatter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            return yaml.safe_load(parts[1])
    return {}

def load_posted_files():
    if not os.path.exists(TRACKING_FILE):
        return set()
    with open(TRACKING_FILE, 'r') as f:
        return set(line.strip() for line in f.readlines())

def save_posted_file(filename):
    with open(TRACKING_FILE, 'a') as f:
        f.write(f"{filename}\n")

def download_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return response.content, image_url.split("/")[-1]
    except Exception as e:
        print(f"Failed to download image: {e}")
    return None, None

def post_event_to_bluesky(frontmatter, filepath):
    caption = frontmatter.get("caption", {})
    title = caption.get("title", frontmatter.get("title", ""))
    subtitle = caption.get("subtitle", frontmatter.get("subtitle", ""))
    image_url = caption.get("thumbnail", "")

    if not title:
        print(f"Skipping {filepath}: no title found.")
        return

    filename = os.path.basename(filepath)
    slug = filename.replace('.md', '')
    website_url = os.getenv("WEBSITE_URL", "https://www.fhdsa.org")
    post_url = f"{website_url}/portfolio/{slug}"

    post_text = f"{title}\n{subtitle}\n\n{post_url}"

    client = Client()
    client.login(os.getenv("BLUESKY_HANDLE"), os.getenv("BLUESKY_PASSWORD"))

    if image_url:
        img_data, img_name = download_image(image_url)
        if img_data:
            blob_response = client.upload_blob(img_data)
            embed = models.AppBskyEmbedImages.Main(
                images=[
                    models.AppBskyEmbedImages.Image(
                        alt=title,
                        image=blob_response.blob  # ✅ this is the fix
                    )
                ]
            )
            client.send_post(text=post_text, embed=embed)
            print(f"Posted with image: {filename}")
            return

    # If no image or download fails, post plain text
    client.send_post(text=post_text)
    print(f"Posted text only: {filename}")

def main():
    posted = load_posted_files()
    md_files = glob.glob("_portfolio/*.md")

    for path in md_files:
        filename = os.path.basename(path)
        if filename in posted:
            print(f"Skipping {filename}, already posted.")
            continue

        frontmatter = extract_frontmatter(path)
        if frontmatter:
            post_event_to_bluesky(frontmatter, path)
            save_posted_file(filename)

if __name__ == "__main__":
    main()
