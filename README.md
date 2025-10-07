# 399_automated
I did not want to do this, so I spent several weeks automating it instead!

# Hackathon Question Generator

> **Fully automated question generator**  
> Generate 50 questions per week (25 steganography + 25 encoding) in <5 minutes

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Steghide Compatible](https://img.shields.io/badge/steghide-compatible-green.svg)](https://steghide.sourceforge.net/)

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [File Structure](#-file-structure)
- [Question Types](#-question-types)
- [Verification](#-verification)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## Features

### Steganography Questions
- Uses **actual steghide** (100% Futureboy-compatible) (Ask me how I know that some are not)
- Fetches random cat images via AP
- Embeds CAHSI-formatted flags in JPEG images
- Automatic verification of every imag
- Generates proper metadata spreadsheet

### Encoding Questions
- **7 cipher types:** base64, Caesar (3/7/13), ROT13, Atbash, reverse
- **Multiple difficulty levels:**
  - Single encodings (60%)
  - Double encodings (30%)
  - Triple encodings (10%)
- Automatic flag generation with required format

### Automation Features
- Interactive prompts (no command-line arguments needed!)
- Validates student ID from file
- Auto-creates organized folder structure
- Generates Excel spreadsheets in required format
- Built-in error handling and retry logic
- Progress indicators and detailed output

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/kevinViers/399_automated.git
cd 399_automated

# 2. Install Python dependencies
pip install requests pillow pandas openpyxl

# 3. Download steghide
# Download: https://sourceforge.net/projects/steghide/files/steghide/0.5.1/steghide-0.5.1-win32.zip
# Extract and copy the "steghide" folder from the zip into the same directory as this script

# 4. Create your student ID file also in this directory
echo YOUR_STUDENT_ID > STUDENT_ID.txt

# 5. Run the generator
python steghide_generator.py
```

---

## Installation

### Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Windows 11** (tested on Windows 11, should work on Windows 10)
- **Internet connection** (for cat image API)

### Step 1: Install Python Packages

```bash
pip install requests pillow pandas openpyxl
```

### Step 2: Download Steghide

1. Download: [steghide-0.5.1-win32.zip](https://sourceforge.net/projects/steghide/files/steghide/0.5.1/steghide-0.5.1-win32.zip)
2. Extract the ZIP file
3. Inside you'll find a folder called `steghide`
4. Copy that entire `steghide` folder to your project directory

### Step 3: Configure Student ID

Create a file named `STUDENT_ID.txt` with your student ID number:

```
JOEMAMA1@gmail.com would become JOEMAMA1
```

## 💻 Usage

### Interactive Mode (Recommended)

Simply run the script:

```bash
python steghide_generator.py
```

The script will prompt you for:
1. **Student ID confirmation** (reads from `STUDENT_ID.txt`)
2. **Week number** (1-8)
3. **Number of questions** (defaults: 25 steg, 25 encoding)
4. **Theme** (default: Cats)

### Example Session

```
######################################################################
#  CAHSI HACKATHON QUESTION GENERATOR
#  Steghide Version (Futureboy-Compatible)
######################################################################

Student ID from STUDENT_ID.txt: 123456789
Is this correct? (Y/N): Y

Enter week number (1-8): 1
Steganography questions (default 25): 
Encoding questions (default 25): 
Theme (default 'Cats'): 

Generating 50 total questions:
   • 25 steganography questions
   • 25 encoding questions

GENERATING 25 ENCODING QUESTIONS
✓ Generated 15 single encodings
✓ Generated 7 double encodings
✓ Generated 3 triple encodings

GENERATING 25 STEGANOGRAPHY QUESTIONS
Question 1/25... ✅
Question 2/25... ✅
...
Question 25/25... ✅

✅ COMPLETE! Generated 50 questions in 287.3 seconds
```

---

## File Structure

### Your Project Directory

```
399_automated/
├── steghide/                    # Steghide executable and DLLs
│   ├── steghide.exe
│   └── everything else etc.
├── steghide_generator.py  # Main generator script
├── STUDENT_ID.txt              # Your student ID (you create this)
├── README.md                   # This file
└── week_1/                     # Generated (after running)
    ├── encodings/
    │   └── 123456789_encodings.xlsx
    └── steganography/
        ├── original_images/    # Cat images (reference)
        ├── stegged_images/     # Steg'd images
        │   ├── cats_001_steg.jpg
        │   ├── cats_002_steg.jpg
        │   └── ... (25 total)
        └── 123456789_stegs.xlsx
```

### Generated Output

After running, you'll have:

- `week_X/steganography/stegged_images/` → 25 JPG files
- `week_X/steganography/STUDENTID_stegs.xlsx` → Metadata spreadsheet
- `week_X/encodings/STUDENTID_encodings.xlsx` → Encoding questions spreadsheet

---

## Question Types

### Steganography Questions

| Field | Description | Example |
|-------|-------------|---------|
| Challenge-Name | Numbered series | CatsSteg001 |
| File-Name | Stegged image filename | cats_001_steg.jpg |
| Flag | Hidden message | CAHSI-CATa1B2c3D4e5F6 |
| Method | Steganography tool | steghide |
| Value | Points awarded | 1 |
| Verified | Auto-verified | ✓ |

### Encoding Questions

| Type | Example Method | Difficulty |
|------|---------------|------------|
| Single | base64 | 1 point |
| Single | caesar7 | 1 point |
| Double | base64→rot13 | 1 point |
| Triple | base64→caesar3→rot13 | 2 points |

**Cipher Types:**
- Base64 encoding
- Caesar cipher (shifts: 3, 7, 13)
- ROT13
- Atbash (reverse alphabet)
- String reversal

---

## Verification

### Test Steganography Images with Futureboy

1. Go to: [Futureboy Decoder](https://futureboy.us/stegano/decinput.html)
2. Upload a stegged JPG file
3. **Password:** Leave blank
4. Select: "View raw output as: MIME-type (TEXT/PLAIN)"
5. Click **Submit**
6. You should see your `CAHSI-XXX` flag! ✅

### Command-Line Verification

```bash
# Extract flag from image
steghide extract -sf cats_001_steg.jpg -p "" -xf output.txt
cat output.txt
```

### Automated Verification

The script automatically verifies every image during generation. Check the `Verified` column in your spreadsheet:
- ✓ = Successfully verified
- ✗ = Verification failed (rare, just regenerate)

---

**Pro Tip:** Read through `question_generator_steghide.py` - it's well-commented and teaches you how everything works!
