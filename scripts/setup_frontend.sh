#!/bin/bash

# --- Helper Functions for Colored Output ---
print_info() {
    echo -e "\e[34m\e[1m[INFO]\e[0m $1"
}

print_success() {
    echo -e "\e[32m\e[1m[SUCCESS]\e[0m $1"
}

print_error() {
    echo -e "\e[31m\e[1m[ERROR]\e[0m $1" >&2
}

# Exit immediately if a command exits with a non-zero status.
set -e

# 1. Check for Node.js and npm
print_info "Checking for Node.js and npm..."
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install it to proceed. You can download it from https://nodejs.org/"
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "Node.js found: $NODE_VERSION"

if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. This is unusual in a Node.js environment. Please reinstall Node.js."
    exit 1
fi
NPM_VERSION=$(npm --version)
print_success "npm found: $NPM_VERSION"

# 2. Check for package.json
print_info "Looking for package.json..."
if [ ! -f "package.json" ]; then
    print_error "'package.json' not found. Cannot install frontend dependencies."
    exit 1
fi
print_success "package.json found."

# 3. Install npm dependencies
print_info "Installing frontend dependencies using npm... (This might take a few minutes)"
npm install

print_success "Frontend setup complete! All dependencies are installed in the 'node_modules' directory."
print_info "You can now start the development server by running: npm run dev"
