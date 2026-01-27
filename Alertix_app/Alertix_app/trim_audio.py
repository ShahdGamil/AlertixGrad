"""
Audio Trimmer Script
Trims alarm.mp3 to 3 seconds
"""

from pydub import AudioSegment
import os

# File paths
input_file = r"assets\sounds\alarm.mp3"
output_file = r"assets\sounds\alarm_trimmed.mp3"
backup_file = r"assets\sounds\alarm_original.mp3"

# Check if file exists
if not os.path.exists(input_file):
    print(f"❌ File not found: {input_file}")
    exit(1)

print(f"📂 Loading audio from: {input_file}")

# Load the audio file
audio = AudioSegment.from_file(input_file)

print(f"⏱️  Original duration: {len(audio) / 1000:.2f} seconds")

# Trim to first 3 seconds (3000 milliseconds)
trimmed_audio = audio[:3000]

print(f"✂️  Trimmed to: {len(trimmed_audio) / 1000:.2f} seconds")

# Backup original
print(f"💾 Backing up original to: {backup_file}")
os.rename(input_file, backup_file)

# Save trimmed version with original name
print(f"💾 Saving trimmed audio to: {input_file}")
trimmed_audio.export(input_file, format="mp3")

print("✅ Done! alarm.mp3 is now 3 seconds long")
print(f"📝 Original file backed up as: {backup_file}")
