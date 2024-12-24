#!/bin/bash

# Define the home directory as the target
TARGET_DIR="/media/user/Courage/2024_backup"

# Ensure the target directory exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: Target directory $TARGET_DIR does not exist or is not a directory."
  exit 1
fi

# Define a list of file extensions for code files
CODE_EXTENSIONS=("*.py" "*.java" "*.js" "*.rb" "*.go" "*.php" "*.ts" "*.sh")

# Loop through the defined extensions and find/copy files
for ext in "${CODE_EXTENSIONS[@]}"; do
  # Find and copy files to the target directory, preserving directory structure
  find . -type f -name "$ext" ! -path "*/site-packages/*" ! -path "*/node_modules/*" ! -path "*/vcpkg_installed/*" -exec sh -c '
    for file do
      target="$1/${file#./}"
      mkdir -p "$(dirname "$target")"
      echo "Copying $file to $target"
      cp "$file" "$target"
    done
  ' sh "$TARGET_DIR" {} +
done

echo "Code files have been copied."
