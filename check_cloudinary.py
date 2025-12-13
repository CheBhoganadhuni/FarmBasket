
import os
import django
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

from django.conf import settings
import cloudinary
import cloudinary.api

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_images():
    print("🔎 Checking Cloudinary Connection...")
    
    # Configure using settings
    config = settings.CLOUDINARY_STORAGE
    if not config.get('CLOUD_NAME'):
        print("❌ Error: CLOUDINARY_CLOUD_NAME not found in environment/settings.")
        return

    print(f"☁️  Connected to: {config['CLOUD_NAME']}")
    
    try:
        # List resources (images)
        # We look for resources in the root or usual folders
        print("\n📸 Fetching 50 recent images from Cloudinary...")
        result = cloudinary.api.resources(max_results=50, type="upload")
        
        resources = result.get('resources', [])
        
        if not resources:
            print("⚠️  No images found in your Cloudinary!")
            print("   (This might mean seeding didn't actually upload, or they are in a specific folder)")
        else:
            print(f"✅ Found {len(resources)}+ images. Here are the last few:")
            print("-" * 60)
            for res in resources:
                print(f"   📂 Public ID: {res['public_id']}")
                print(f"   🔗 URL: {res['secure_url']}")
                print("-" * 60)
            
            print("\n✅ Verification Successful: Images ARE in Cloudinary.")
            print("   If they don't show on the site, it was likely an HTTPS/Mixed Content issue.")
            print("   I have added 'SECURE': True to settings to fix that.")

    except Exception as e:
        print(f"\n❌ Error connecting to Cloudinary: {e}")
        print("   Check your API Key and Secret in .env")

if __name__ == "__main__":
    check_images()
