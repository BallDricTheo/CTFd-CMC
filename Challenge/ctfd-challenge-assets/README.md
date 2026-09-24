# CTFd Challenge Assets

A collection of beginner-friendly Capture The Flag (CTF) challenges designed for educational purposes in a classroom environment. These challenges are designed to be deployed with [CTFd](https://ctfd.io/), an open-source CTF platform, and serve as an introduction to cybersecurity concepts for students.

## Overview

This repository contains CTF challenges for educational purposes in a classroom environment, including:

- **11 main challenges** across Web Exploitation, Cryptography, Forensics, Reverse Engineering, and Steganography
- **20 daily warmup challenges** focused on various encoding and cipher techniques

Each challenge is designed to teach fundamental security concepts in an engaging, gamified format suitable for classroom instruction.

The main challenges are hosted as static web assets via GitHub Pages and can be easily imported into any CTFd instance using the included CSV files.

## Repository Structure

```
ctfd-challenge-assets/
├── challenges.csv             # CTFd import file with all challenge definitions
├── dailies.csv                # Daily warmup challenges (hidden by default)
├── challenges/                # Challenge assets and web pages
│   ├── index.html             # Landing page (404 style)
│   ├── cookie-monster/        # Cookie manipulation challenge
│   ├── exif-tastic/           # EXIF metadata extraction challenge
│   ├── hidden-gadget/         # HTML inspection challenge
│   ├── js-jiggler/            # JavaScript manipulation challenge
│   ├── plain-sight/           # Steganography challenge
│   ├── source-sleuth/         # HTML source code inspection challenge
│   ├── string-theory/         # Binary strings extraction challenge
│   └── web-weaver/            # Advanced web challenge with obfuscation
├── LICENSE.md                 # MIT License
└── README.md                  # This file
```

## Challenge Categories

The categories in this CTF are examples of common introductory topics in cybersecurity education, and can be modified or expanded based on curriculum needs.

### Daily Challenges (20 challenges)
Quick 15-20 minute warmup challenges designed to be released one per day. All challenges are hidden by default and require no external assets.

- **Daily #1: ROT13 Warmup** (50 pts) - ROT13 substitution cipher
- **Daily #2: Binary Basics** (50 pts) - Binary to ASCII conversion
- **Daily #3: Morse Mystery** (50 pts) - Morse code decoding
- **Daily #4: ASCII Art** (50 pts) - Decimal ASCII values to text
- **Daily #5: Backwards Thinking** (50 pts) - Reversed string
- **Daily #6: Octal Oddity** (50 pts) - Octal to ASCII conversion
- **Daily #7: URL Encoded** (50 pts) - URL decoding
- **Daily #8: XOR Simple** (75 pts) - Basic XOR cipher
- **Daily #9: Atbash Cipher** (50 pts) - Alphabet reversal cipher
- **Daily #10: Leetspeak** (50 pts) - L33t speak translation
- **Daily #11: Brainfuck Intro** (75 pts) - Esoteric programming language
- **Daily #12: NATO Phonetic** (50 pts) - NATO alphabet decoding
- **Daily #13: Pig Latin** (50 pts) - Pig Latin translation
- **Daily #14: Braille Dots** (75 pts) - Braille to text
- **Daily #15: Rail Fence** (75 pts) - Rail fence cipher
- **Daily #16: Vigenère Lite** (100 pts) - Vigenère cipher
- **Daily #17: Keyboard Shift** (75 pts) - QWERTY keyboard shift pattern
- **Daily #18: Soundex Code** (100 pts) - Soundex phonetic algorithm
- **Daily #19: T9 Texting** (75 pts) - Mobile phone T9 encoding
- **Daily #20: Polybius Square** (75 pts) - Grid-based cipher

### Web Exploitation (6 challenges)
- **Source Sleuth** (100 pts) - Learn to view HTML source code
- **Cookie Monster** (200 pts) - Browser cookie manipulation
- **Hidden Gadget** (300 pts) - Inspect hidden HTML elements
- **JS Jiggler** (400 pts) - JavaScript console and manipulation
- **Web Weaver** (500 pts) - Advanced JavaScript obfuscation and riddles

### Cryptography (3 challenges)
- **Base-ic Instinct** (100 pts) - Base64 encoding/decoding
- **Caesar Shift** (100 pts) - Classic Caesar cipher
- **Hex Decoder** (100 pts) - Hexadecimal to ASCII conversion

### Forensics (1 challenge)
- **EXIF-tastic** (150 pts) - Image metadata analysis

### Reverse Engineering (1 challenge)
- **String Theory** (200 pts) - Binary file string extraction

### Steganography (1 challenge)
- **Hidden in Plain Sight** (300 pts) - Image steganography with steghide

## Getting Started

The following instructions will help you set up and deploy the challenges in your own CTFd instance.

### Prerequisites

- A CTFd instance (self-hosted or cloud-based)
- Web browser with developer tools
- Basic command-line tools (optional, for some challenges)

### Importing Challenges into CTFd

1. Log in to your CTFd instance as an administrator
2. Navigate to **Admin Panel** → **Config** → **Backup** → **Import & Export**
3. Under the **Import CSV** section, select the `challenges.csv` file from this repository
4. Click **Import** to load all main challenges, flags, hints, and categories
5. (Optional) Import `dailies.csv` for the 20 daily warmup challenges
6. Verify that all challenges appear in the challenges list

The CSV import will automatically configure:
- Challenge names and descriptions
- Point values (100-500 points)
- Categories and tags
- Flags (answers)
- Hints for students
- Challenge visibility settings

### For Students

Students can access the challenges through your CTFd instance. 

**Main challenges** are hosted at:

```
https://zachflower.github.io/ctfd-challenge-assets/<challenge-name>/
```

**Daily challenges** are self-contained in their descriptions and require no external URLs - all information needed to solve them is provided in the challenge text.

## Challenge Difficulty Progression

The challenges are designed with a learning curve in mind. This is just a suggested progression; instructors can adapt based on their students' skill levels, interests, and time constraints.

**Daily Warmups (50-100 pts):**
- Use these as quick daily exercises to build familiarity with common encoding/cipher techniques
- All 20 daily challenges are hidden by default - reveal one per day to maintain engagement
- Ideal for starting each class session or as homework assignments

**Beginner (100-150 pts):**
- Base-ic Instinct
- Caesar Shift
- Hex Decoder
- Source Sleuth
- EXIF-tastic

**Intermediate (200-300 pts):**
- Cookie Monster
- String Theory
- Hidden Gadget
- Hidden in Plain Sight

**Advanced (400-500 pts):**
- JS Jiggler
- Web Weaver

## Required Tools

Most challenges can be solved using just a web browser, but some may benefit from additional tools:

### Web Browser

- Chrome, Firefox, or Edge with Developer Tools (F12)
- Browser extensions for cookie editing (optional)

### Command-Line Tools

- `base64` - Base64 encoding/decoding
- `exiftool` - EXIF metadata extraction
- `strings` - Extract printable strings from binary files
- `steghide` - Steganography extraction tool

### Online Resources

- https://www.base64decode.org/ - Base64 decoder
- https://cryptii.com/pipes/caesar-cipher - Caesar cipher decoder
- https://www.rapidtables.com/convert/number/hex-to-ascii.html - Hex to ASCII converter
- https://exif.tools/ - Online EXIF viewers

## Customization

### Modifying Challenges

1. Clone this repository
2. Edit HTML files in the `challenges/` directory
3. Update `challenges.csv` with new flags or descriptions
4. Host on GitHub Pages or your own web server
5. Re-import the CSV into CTFd

### Adding New Challenges

1. Create a new directory under `challenges/`
2. Add challenge files (HTML, images, binaries, etc.)
3. Add a new row to `challenges.csv` with challenge details
4. Test the challenge before importing

### Hosting Options

- **GitHub Pages** (current setup) - Free, simple, version-controlled
- **Self-Hosted** - Host on your own web server for full control
- **Cloud Storage** - Use AWS S3, Azure Blob Storage, or similar

## Security Considerations

- These challenges might contain **intentional security vulnerabilities** for educational purposes
- Do **not** use any of this code in production environments
- Flags are visible in source code and files - this is by design for educational access
- Students should understand these are learning tools, not examples of secure coding practices

## Support and Contributions

### Found an Issue?

If you encounter problems with any challenge:
1. Check the hints provided in CTFd
2. Verify you're using the correct URL
3. Ensure your browser's developer tools are working
4. Try a different browser if issues persist

### Contributing

Contributions are welcome! To add new challenges or improve existing ones:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/new-challenge`)
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Additional Resources

### Learning More About CTFs
- [CTFd Documentation](https://docs.ctfd.io/)
- [CTF Field Guide](https://trailofbits.github.io/ctf/)
- [picoCTF Learning Resources](https://picoctf.org/resources)

### Cybersecurity Education
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Web Security Academy](https://portswigger.net/web-security)
- [Cybersecurity & Infrastructure Security Agency (CISA) Resources](https://www.cisa.gov/cybersecurity)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
