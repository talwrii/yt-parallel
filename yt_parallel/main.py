#!/usr/bin/env python3
#
# yt-parallel
# Downloads two specified VTT subtitles for a given YouTube URL,
# generates IPA for the first language (if supported by eSpeak), merges the content,
# and outputs the final parallel HTML transcript to standard out.
#
# Dependencies: yt-dlp, espeak, python 're', 'os', 'subprocess', 'tempfile'
#
# Usage: ./yt-parallel <YouTube URL> <L1_code> <L2_code> > transcript.html
# Example: ./yt-parallel "https://www.youtube.com/watch?v=..." da en > da-en-transcript.html

import sys
import re
import os
import subprocess
import tempfile
import atexit

# Global variables for temporary directory and files
TEMP_DIR = None
TEMP_FILES = []

# --- Temporary File Cleanup (Ensures files are deleted on script exit) ---
@atexit.register
def cleanup_temp_files():
    """Removes all files created in the temporary directory."""
    for filepath in TEMP_FILES:
        try:
            os.remove(filepath)
        except:
            pass
    try:
        if TEMP_DIR:
            os.rmdir(TEMP_DIR)
    except:
        pass

# --- eSpeak IPA Generation Function ---
def generate_ipa(text, lang_code):
    """
    Generates IPA for the given text using the espeak command-line tool.
    """
    if not text:
        return ""
        
    try:
        # Command: -v<lang_code> (Language), -q (quiet), --ipa=2 (IPA with stress markers)
        command = ['espeak', f'-v{lang_code}', '-q', '--ipa=2', text]
        
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True,
            encoding='utf-8'
        )
        ipa = result.stdout.strip().strip("'").strip('"')
        return re.sub(r'\s+', ' ', ipa).strip()
        
    except FileNotFoundError:
        sys.stderr.write("\n! FATAL ERROR: 'espeak' command not found. IPA generation failed.\n")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Warning: eSpeak failed for language '{lang_code}'. Output: {e.stderr.strip()}\n")
        return ""
    except Exception as e:
        sys.stderr.write(f"Warning: Unexpected error during IPA generation: {e}\n")
        return ""

# --- Subtitle Download Function ---
def download_subtitles(url, temp_dir, lang_codes):
    """
    Downloads VTT subtitles for the required languages to the temporary directory.
    Returns a tuple of paths: (path_to_L1_vtt, path_to_L2_vtt).
    """
    global TEMP_FILES

    l1_code, l2_code = lang_codes
    sub_langs_arg = f'{l1_code},{l2_code}'
    sub_format = 'vtt'

    output_template = os.path.join(temp_dir, 'temp.%(ext)s')
    
    # Get cookie source from environment variable, defaulting to 'chrome'
    cookies_source = os.environ.get('YT_PARALLEL_COOKIES', 'chrome')

    command = [
        'yt-dlp',
        url,
        '--cookies-from-browser', cookies_source,
        '--write-sub',
        '--write-auto-sub',
        '--sub-langs', sub_langs_arg,
        '--sub-format', sub_format,
        '--skip-download',
        '--retries', '3',
        '--impersonate', 'Safari',
        '-o', output_template
    ]

    sys.stderr.write(f"--- Downloading Subtitles ({l1_code}/{l2_code}) for {url} ---\n")
    try:
        # Use stderr for yt-dlp's output to keep stdout clean for HTML
        subprocess.run(command, check=True, text=True, stdout=sys.stderr, stderr=sys.stderr)
        sys.stderr.write("✅ Subtitle download complete.\n")
    except subprocess.CalledProcessError:
        sys.stderr.write("\n! FATAL ERROR: Subtitle download failed. yt-dlp output above.\n")
        sys.exit(1)
    except FileNotFoundError:
        sys.stderr.write("\n! FATAL ERROR: 'yt-dlp' command not found. Please install it.\n")
        sys.exit(1)
    
    # Check for created files
    l1_path = os.path.join(temp_dir, f'temp.{l1_code}.{sub_format}')
    l2_path = os.path.join(temp_dir, f'temp.{l2_code}.{sub_format}')

    if not os.path.exists(l1_path):
        sys.stderr.write(f"\n! FATAL ERROR: Primary subtitle file ({l1_code}) not found at {l1_path}. Check language code or if subtitles are available.\n")
        sys.exit(1)
    
    # L2 is not strictly required to exist, but if it doesn't, we warn the user
    if not os.path.exists(l2_path):
        sys.stderr.write(f"\n! WARNING: Secondary subtitle file ({l2_code}) not found. Proceeding with L1 only.\n")
        l2_path = None 

    # Register temp files for cleanup
    TEMP_FILES.append(l1_path)
    if l2_path:
        TEMP_FILES.append(l2_path)

    return l1_path, l2_path

# --- Subtitle Merge Function ---
def merge_vtt_to_html(file1_path, file2_path, l1_code, l2_code):
    """
    Takes two VTT files, merges their text cues, adds IPA for L1,
    and returns the complete HTML content string.
    """
    
    with open(file1_path, 'r', encoding='utf-8') as f1:
        content1 = f1.read()
    
    content2 = ""
    if file2_path:
        with open(file2_path, 'r', encoding='utf-8') as f2:
            content2 = f2.read()

    cue_pattern = re.compile(
        r'(\d{2}:\d{2}:\d{2}\.\d{3} --> .*?\n)(.*?)(?=\n\n|\Z)', 
        re.DOTALL
    )

    cues1 = cue_pattern.findall(content1)
    # If L2 file doesn't exist, create placeholders to maintain alignment
    cues2 = cue_pattern.findall(content2) if content2 else [('', '')] * len(cues1)

    if len(cues1) != len(cues2):
        sys.stderr.write("! FATAL ERROR: Cue counts do not match. Files are misaligned.\n")
        sys.exit(1)

    html_content = []
    cue_count = len(cues1)

    for i, ((header1, text1), (header2, text2)) in enumerate(zip(cues1, cues2)):
        
        clean_text_l1 = re.sub(r'<.*?>', '', text1.strip())
        clean_text_l2 = re.sub(r'<.*?>', '', text2.strip())
        
        ipa_text = generate_ipa(clean_text_l1, l1_code)
        
        paragraph_block = '    <p>'
        
        if clean_text_l1:
            paragraph_block += f'<b>{clean_text_l1}</b>'
        
        if ipa_text or clean_text_l2:
            paragraph_block += ' \n        <br> '
        
        if ipa_text:
            paragraph_block += f'<span class="ipa">/{ipa_text}/</span>'
        
        if ipa_text and clean_text_l2:
            paragraph_block += ' \n        <br> '
        
        if clean_text_l2:
            paragraph_block += clean_text_l2
        
        paragraph_block += '</p>'
        html_content.append(paragraph_block)
        
        if i < cue_count - 1:
            html_content.append('    <hr>\n')
        
        html_content.append('\n')

    html_template = f"""<!DOCTYPE html>
<html lang="{l2_code}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parallel Transcript: {l1_code.upper()} / {l2_code.upper()} with IPA</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        p {{
            margin: 1em 0; 
            white-space: normal;
        }}
        .ipa {{
            font-family: "Lucida Sans Unicode", "Arial Unicode MS", sans-serif; 
            font-size: 0.9em;
            color: #555;
            font-style: italic;
        }}
        hr {{
            border: 0;
            height: 1px;
            background: #ccc;
            margin: 15px 0; 
        }}
    </style>
</head>
<body>
    <h1>Parallel Transcript: {l1_code.upper()} in Bold, IPA, and {l2_code.upper()}</h1>
{f'<p>Error: No cues found. Check VTT content.</p>' if not html_content else ''.join(html_content).strip()}
</body>
</html>
"""
    return html_template

def main():
    """Handles argument parsing, file downloading, merging, and output. Arguments are now mandatory."""
    global TEMP_DIR
    
    if len(sys.argv) != 4:
        sys.stderr.write("! FATAL ERROR: Missing mandatory arguments.\n")
        sys.stderr.write("Usage: ./yt-parallel <YouTube URL> <L1_code> <L2_code>\n")
        sys.stderr.write("Example: ./yt-parallel \"https://www.youtube.com/watch?v=...\" da en > da-en-transcript.html\n")
        sys.exit(1)
    
    url = sys.argv[1]
    l1_code = sys.argv[2] # Primary language (L1) is now mandatory
    l2_code = sys.argv[3] # Secondary language (L2) is now mandatory
    
    # 1. Create temporary directory
    TEMP_DIR = tempfile.mkdtemp()
    sys.stderr.write(f"Using temporary directory: {TEMP_DIR}\n")
    
    # 2. Download subtitles
    lang_codes = [l1_code, l2_code]
    l1_vtt_path, l2_vtt_path = download_subtitles(url, TEMP_DIR, lang_codes)

    # 3. Merge and process subtitles
    sys.stderr.write("--- Merging and processing subtitles ---\n")
    final_html = merge_vtt_to_html(l1_vtt_path, l2_vtt_path, l1_code, l2_code)

    # 4. Print HTML to standard output (stdout)
    sys.stdout.write(final_html)

if __name__ == '__main__':
    main()
