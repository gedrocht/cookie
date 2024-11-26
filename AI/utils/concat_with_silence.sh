#!/bin/bash

rm silence.wav
rm ${1}/output.wav
# Create a list file for concatenation
echo "# Create a list of all wav files" > filelist.txt
for f in ${1}/*_*.wav; do
  # Add each wav file and 1 second of silence to the list
  echo "file '$f'" >> filelist.txt
  echo "file 'silence.wav'" >> filelist.txt
done

# Generate a 1-second silent wav file (16-bit PCM, 44.1kHz sample rate)
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 silence.wav

# Concatenate all files in the list into a single output file
ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy ${1}/output.wav

# Remove the temporary silence.wav and filelist.txt
rm filelist.txt
