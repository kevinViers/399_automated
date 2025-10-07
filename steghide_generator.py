"""
CAHSI Hackathon Question Generator - STEGHIDE VERSION
======================================================
Uses actual steghide command-line tool (Futureboy-compatible!)

PREREQUISITES:
1. Download steghide: https://sourceforge.net/projects/steghide/files/steghide/0.5.1/steghide-0.5.1-win32.zip
2. Extract and copy the "steghide" folder to the same directory as this script
3. pip install requests pillow pandas openpyxl
4. Create STUDENT_ID.txt with your student ID number

USAGE:
    python question_generator_steghide.py
    
    (No arguments needed - it will prompt you for everything!)
"""

import requests
import random
import string
import pandas as pd
from pathlib import Path
from PIL import Image
import io
import time
import base64
import subprocess
import os
from datetime import datetime

class SteghideGenerator:
    """Generates steganography questions using actual steghide"""
    
    def __init__(self, output_dir="steg_output", student_id="student"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.student_id = student_id
        self.images_dir = self.output_dir / "original_images"
        self.stegged_dir = self.output_dir / "stegged_images"
        self.images_dir.mkdir(exist_ok=True)
        self.stegged_dir.mkdir(exist_ok=True)
        
        # Check if steghide is available
        self.steghide_path = self.find_steghide()
        
    def find_steghide(self):
        """Find steghide executable"""
        # Check common folder locations
        possible_paths = [
            Path("steghide") / "steghide.exe",  # Most common: extracted steghide folder
            Path("steghide-0.5.1-win32") / "steghide.exe",  # If user renamed it
            Path("steghide.exe"),  # Current directory
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"Found steghide at: {path.parent if path.parent.name != '.' else 'current directory'}")
                return path.absolute()
        
        # Check if in PATH
        try:
            result = subprocess.run(["steghide", "--version"], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                print("Found steghide in system PATH")
                return "steghide"
        except:
            pass
        
        print("\n" + "="*70)
        print("ERROR: steghide.exe not found!")
        print("="*70)
        print("\nPlease download and extract steghide:")
        print("1. Go to: https://sourceforge.net/projects/steghide/files/steghide/0.5.1/")
        print("2. Download: steghide-0.5.1-win32.zip")
        print("3. Extract the ZIP file")
        print("4. Inside you'll find a 'steghide' folder - copy that entire folder")
        print("   to the same directory as this script")
        print("\nYour folder structure should be:")
        print("  your_folder/")
        print("    ├── steghide/              <- The extracted folder")
        print("    │   ├── steghide.exe")
        print("    │   └── *.dll files")
        print("    └── question_generator_steghide.py")
        print("\nOr install via Chocolatey: choco install steghide")
        print("="*70 + "\n")
        raise FileNotFoundError("steghide.exe not found")
        
    def generate_flag(self, theme_prefix="CAT", length=12):
        """Generate a random flag"""
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        random_part = ''.join(random.choices(chars, k=length))
        return f"CAHSI-{theme_prefix}{random_part}"
    
    def fetch_cat_image(self, filename):
        """Fetch cat image from API and save as JPEG"""
        max_attempts = 10
        
        for attempt in range(max_attempts):
            try:
                response = requests.get("https://cataas.com/cat", timeout=15)
                response.raise_for_status()
                
                img = Image.open(io.BytesIO(response.content))
                
                # Convert to RGB for JPEG
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        rgb_img.paste(img, mask=img.split()[-1])
                    else:
                        rgb_img.paste(img)
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as JPEG (steghide supports JPEG)
                filepath = self.images_dir / filename
                img.save(filepath, 'JPEG', quality=95)
                
                # Resize if too large
                if filepath.stat().st_size > 2 * 1024 * 1024:
                    img.thumbnail((1920, 1920), Image.Resampling.LANCZOS)
                    img.save(filepath, 'JPEG', quality=90)
                
                return filepath
                
            except Exception as e:
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue
                print(f"✗ Failed to fetch image: {e}")
                return None
        
        return None
    
    def steg_with_steghide(self, cover_image, flag, output_image):
        """Embed flag using steghide (no password)"""
        try:
            # Create temp file with flag
            flag_file = self.images_dir / "temp_flag.txt"
            flag_file.write_text(flag, encoding='utf-8')
            
            # Run steghide embed command
            # Use -p "" to explicitly set empty password
            cmd = [
                str(self.steghide_path),
                "embed",
                "-ef", str(flag_file),
                "-cf", str(cover_image),
                "-sf", str(output_image),
                "-p", "",  # Empty password explicitly
                "-f"  # Force overwrite
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,  # Reduced timeout
                input=""  # Send empty input to stdin
            )
            
            # Clean up temp file
            if flag_file.exists():
                flag_file.unlink()
            
            if result.returncode == 0 and Path(output_image).exists():
                return output_image
            else:
                # Try to print actual error
                if result.stderr:
                    print(f"\nSteghide stderr: {result.stderr[:100]}")
                if result.stdout:
                    print(f"Steghide stdout: {result.stdout[:100]}")
                return None
                
        except subprocess.TimeoutExpired:
            print("(timeout)", end=" ")
            if flag_file.exists():
                flag_file.unlink()
            return None
        except Exception as e:
            print(f"Error: {e}")
            if flag_file.exists():
                flag_file.unlink()
            return None
    
    def verify_with_steghide(self, steg_image, expected_flag):
        """Verify stegged image using steghide"""
        try:
            # Extract to temp file
            extract_file = self.images_dir / "temp_extract.txt"
            
            cmd = [
                str(self.steghide_path),
                "extract",
                "-sf", str(steg_image),
                "-xf", str(extract_file),
                "-p", "",  # Empty password
                "-f"  # Force overwrite
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,  # Reduced timeout
                input=""  # Send empty input
            )
            
            if result.returncode == 0 and extract_file.exists():
                extracted_flag = extract_file.read_text(encoding='utf-8').strip()
                if extract_file.exists():
                    extract_file.unlink()
                return extracted_flag == expected_flag
            
            if extract_file.exists():
                extract_file.unlink()
            return False
            
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            return False
    
    def generate_questions(self, num_questions=25, theme="Cats"):
        """Generate all steganography questions"""
        questions = []
        
        print(f"\n{'='*70}")
        print(f"GENERATING {num_questions} STEGANOGRAPHY QUESTIONS")
        print(f"Using: steghide (Futureboy-compatible!)")
        print(f"{'='*70}\n")
        
        for i in range(1, num_questions + 1):
            print(f"Question {i}/{num_questions}...", end=" ")
            
            challenge_name = f"{theme}Steg{i:03d}"
            original_filename = f"{theme.lower()}_{i:03d}.jpg"
            stegged_filename = f"{theme.lower()}_{i:03d}_steg.jpg"
            flag = self.generate_flag(theme[:3].upper(), 12)
            
            # Download image
            image_path = self.fetch_cat_image(original_filename)
            if not image_path:
                print("Failed to download")
                continue
            
            # Steg with steghide
            steg_path = self.stegged_dir / stegged_filename
            result = self.steg_with_steghide(image_path, flag, steg_path)
            if not result:
                print("Failed to steg")
                continue
            
            # Verify
            verified = self.verify_with_steghide(steg_path, flag)
            
            questions.append({
                'Challenge-Name': challenge_name,
                'File-Name': steg_path.name,
                'Flag': flag,
                'Method': 'steghide',
                'Value': 1,
                'Verified': '✓' if verified else '✗'
            })
            
            print("✅" if verified else "⚠️")
            
            # Rate limiting
            if i % 10 == 0:
                time.sleep(1)
        
        # Save spreadsheet
        df = pd.DataFrame(questions)
        spreadsheet_path = self.output_dir / f"{self.student_id}_stegs.xlsx"
        df.to_excel(spreadsheet_path, index=False)
        
        verified_count = len([q for q in questions if q['Verified'] == '✓'])
        
        print(f"\n{'='*70}")
        print(f"✓ Generated {len(questions)}/{num_questions} questions")
        print(f"✓ Verified: {verified_count}/{len(questions)}")
        print(f"✓ Spreadsheet: {spreadsheet_path}")
        print(f"✓ Stegged images: {self.stegged_dir}")
        print(f"{'='*70}\n")
        
        return df


class CompleteEncodingGenerator:
    """Generates encoding questions with multiple cipher types"""
    
    def __init__(self, output_dir="encoding_output", student_id="student"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.student_id = student_id
        
    def generate_flag(self, theme_prefix="ENC", length=12):
        """Generate a random flag"""
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        random_part = ''.join(random.choices(chars, k=length))
        return f"CAHSI-{theme_prefix}{random_part}"
    
    def caesar_cipher(self, text, shift):
        """Apply Caesar cipher"""
        result = []
        for char in text:
            if char.isupper():
                result.append(chr((ord(char) - 65 + shift) % 26 + 65))
            elif char.islower():
                result.append(chr((ord(char) - 97 + shift) % 26 + 97))
            else:
                result.append(char)
        return ''.join(result)
    
    def rot13(self, text):
        """Apply ROT13"""
        return self.caesar_cipher(text, 13)
    
    def base64_encode(self, text):
        """Base64 encode"""
        return base64.b64encode(text.encode()).decode()
    
    def atbash(self, text):
        """Apply Atbash cipher"""
        result = []
        for char in text:
            if char.isupper():
                result.append(chr(90 - (ord(char) - 65)))
            elif char.islower():
                result.append(chr(122 - (ord(char) - 97)))
            else:
                result.append(char)
        return ''.join(result)
    
    def reverse(self, text):
        """Reverse string"""
        return text[::-1]
    
    def generate_single(self, flag):
        """Generate single encoding"""
        encodings = [
            ("base64", self.base64_encode),
            ("caesar3", lambda x: self.caesar_cipher(x, 3)),
            ("caesar7", lambda x: self.caesar_cipher(x, 7)),
            ("caesar13", lambda x: self.caesar_cipher(x, 13)),
            ("rot13", self.rot13),
            ("atbash", self.atbash),
            ("reverse", self.reverse),
        ]
        
        method_name, encoder = random.choice(encodings)
        return method_name, encoder(flag), 1
    
    def generate_double(self, flag):
        """Generate double encoding"""
        encoded = self.base64_encode(flag)
        
        second = [
            ("caesar3", lambda x: self.caesar_cipher(x, 3)),
            ("caesar7", lambda x: self.caesar_cipher(x, 7)),
            ("rot13", self.rot13),
        ]
        
        method2, encoder2 = random.choice(second)
        final = encoder2(encoded)
        
        return f"base64->{method2}", final, 1
    
    def generate_triple(self, flag):
        """Generate triple encoding"""
        encoded1 = self.base64_encode(flag)
        shift = random.choice([3, 7, 13])
        encoded2 = self.caesar_cipher(encoded1, shift)
        encoded3 = self.rot13(encoded2)
        
        return f"base64->caesar{shift}->rot13", encoded3, 2
    
    def generate_questions(self, num_questions=25, theme="Cipher"):
        """Generate all encoding questions"""
        questions = []
        
        print(f"\n{'='*70}")
        print(f"GENERATING {num_questions} ENCODING QUESTIONS")
        print(f"{'='*70}\n")
        
        num_single = int(num_questions * 0.6)
        num_double = int(num_questions * 0.3)
        num_triple = num_questions - num_single - num_double
        
        question_num = 1
        
        # Single encodings
        for i in range(num_single):
            flag = self.generate_flag(theme[:3].upper(), 12)
            method, encoded, points = self.generate_single(flag)
            
            questions.append({
                'Challenge-Name': f"{theme}{question_num:03d}",
                'Flag': flag,
                'Method': method,
                'Cipher': method,
                'Value': encoded,
                'Points': points
            })
            question_num += 1
        
        print(f"✓ Generated {num_single} single encodings")
        
        # Double encodings
        for i in range(num_double):
            flag = self.generate_flag(theme[:3].upper(), 12)
            method, encoded, points = self.generate_double(flag)
            
            questions.append({
                'Challenge-Name': f"{theme}{question_num:03d}",
                'Flag': flag,
                'Method': method,
                'Cipher': method,
                'Value': encoded,
                'Points': points
            })
            question_num += 1
        
        print(f"✓ Generated {num_double} double encodings")
        
        # Triple encodings
        for i in range(num_triple):
            flag = self.generate_flag(theme[:3].upper(), 12)
            method, encoded, points = self.generate_triple(flag)
            
            questions.append({
                'Challenge-Name': f"{theme}{question_num:03d}",
                'Flag': flag,
                'Method': method,
                'Cipher': method,
                'Value': encoded,
                'Points': points
            })
            question_num += 1
        
        print(f"✓ Generated {num_triple} triple encodings")
        
        # Save spreadsheet
        df = pd.DataFrame(questions)
        spreadsheet_path = self.output_dir / f"{self.student_id}_encodings.xlsx"
        df.to_excel(spreadsheet_path, index=False)
        
        print(f"\n{'='*70}")
        print(f"✓ Total: {len(questions)} encoding questions")
        print(f"✓ Spreadsheet: {spreadsheet_path}")
        print(f"{'='*70}\n")
        
        return df


def main():
    print(f"\n{'#'*70}")
    print(f"#  CAHSI HACKATHON QUESTION GENERATOR")
    print(f"#  Steghide Version (Futureboy-Compatible)")
    print(f"{'#'*70}\n")
    
    # Read student ID from file
    student_id_file = Path("STUDENT_ID.txt")
    
    if not student_id_file.exists():
        print("ERROR: STUDENT_ID.txt not found!")
        print("\nPlease create a file named STUDENT_ID.txt")
        print("and paste your student ID number in it.")
        print("\nExample content: 123456789\n")
        input("Press Enter to exit...")
        return 1
    
    # Read student ID
    student_id = student_id_file.read_text().strip()
    
    if not student_id:
        print("ERROR: STUDENT_ID.txt is empty!")
        print("Please add your student ID number to the file.\n")
        input("Press Enter to exit...")
        return 1
    
    # Confirm student ID
    print(f"Student ID from STUDENT_ID.txt: {student_id}")
    confirm = input("Is this correct? (Y/N): ").strip().upper()
    
    if confirm != 'Y':
        print("\nPlease update STUDENT_ID.txt with your correct student ID.")
        input("Press Enter to exit...")
        return 1
    
    # Get week number
    print()
    while True:
        week_input = input("Enter week number (1-8): ").strip()
        try:
            week = int(week_input)
            if 1 <= week <= 8:
                break
            else:
                print("Please enter a number between 1 and 8.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get question counts (with defaults)
    print()
    steg_input = input("Steganography questions (default 25): ").strip()
    steg = int(steg_input) if steg_input else 25
    
    encoding_input = input("Encoding questions (default 25): ").strip()
    encoding = int(encoding_input) if encoding_input else 25
    
    # Get theme (with default)
    theme_input = input("Theme (default 'Cats'): ").strip()
    theme = theme_input if theme_input else 'Cats'
    
    # Create week directory
    week_dir = Path(f"week_{week}")
    week_dir.mkdir(exist_ok=True)
    
    start_time = time.time()
    
    print(f"\n{'#'*70}")
    print(f"#  WEEK {week} - STARTING GENERATION")
    print(f"#  Student: {student_id}")
    print(f"#  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}\n")
    
    total = steg + encoding
    print(f"Generating {total} total questions:")
    print(f"   • {steg} steganography questions")
    print(f"   • {encoding} encoding questions\n")
    
    # Generate encoding questions
    try:
        encoding_gen = CompleteEncodingGenerator(
            output_dir=str(week_dir / "encodings"),
            student_id=student_id
        )
        encoding_df = encoding_gen.generate_questions(encoding, f"{theme}Code")
    except Exception as e:
        print(f"\nERROR generating encoding questions: {e}")
        input("\nPress Enter to exit...")
        return 1
    
    # Generate steganography questions
    try:
        steg_gen = SteghideGenerator(
            output_dir=str(week_dir / "steganography"),
            student_id=student_id
        )
        steg_df = steg_gen.generate_questions(steg, theme)
    except Exception as e:
        print(f"\nERROR generating steganography questions: {e}")
        print(f"\nMake sure the 'steghide' folder is in the same directory as this script!")
        input("\nPress Enter to exit...")
        return 1
    
    elapsed = time.time() - start_time
    
    print(f"\n{'#'*70}")
    print(f"#  COMPLETE!")
    print(f"#  Generated {len(encoding_df) + len(steg_df)} questions in {elapsed:.1f} seconds")
    print(f"#  Output directory: {week_dir.absolute()}")
    print(f"{'#'*70}\n")
    
    print("NEXT STEPS:")
    print(f"1. Find your files in: {week_dir.absolute()}")
    print(f"2. Test with Futureboy: https://futureboy.us/stegano/decinput.html")
    print(f"3. Upload stegged images from: {week_dir / 'steganography' / 'stegged_images'}")
    print(f"4. Upload spreadsheets to your Google Drive folder")
    print(f"5. Submit your bi-weekly report on Canvas\n")
    
    input("Press Enter to exit...")
    return 0


if __name__ == "__main__":
    exit(main())