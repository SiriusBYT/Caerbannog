#!/bin/bash

# Global Variables
Caerbannog_Version="Ceres MK.I Rev.2"
Reload_Status=false
Running=true

declare -A Configuration=()
Clients=()
Reload_Completed=()

log() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") [Caerbannog] $1"
}

install_dependencies() {
    log "Installing missing dependencies..."
    required_cmds=("inotifywait" "uuidgen" "jq" "nc")
    
    # Detect the package manager
    if command -v apt-get &> /dev/null; then
        pkg_manager="apt-get"
        install_cmd="sudo apt-get install -y"
    elif command -v yum &> /dev/null; then
        pkg_manager="yum"
        install_cmd="sudo yum install -y"
    elif command -v dnf &> /dev/null; then
        pkg_manager="dnf"
        install_cmd="sudo dnf install -y"
    elif command -v pacman &> /dev/null; then
        pkg_manager="pacman"
        install_cmd="sudo pacman -S --noconfirm"
    elif command -v zypper &> /dev/null; then
        pkg_manager="zypper"
        install_cmd="sudo zypper install -y"
    elif command -v apk &> /dev/null; then
        pkg_manager="apk"
        install_cmd="sudo apk add"
    elif command -v emerge &> /dev/null; then
        pkg_manager="emerge"
        install_cmd="sudo emerge --ask"
    elif command -v nix-env &> /dev/null; then
        pkg_manager="nix-env"
        install_cmd="nix-env -iA nixpkgs"
    else
        log "No supported package manager found. Please install dependencies manually."
        exit 1
    fi

    log "Detected package manager: $pkg_manager"

    for cmd in "${required_cmds[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log "Installing $cmd using $pkg_manager..."
            $install_cmd "$cmd" || {
                log "Failed to install $cmd with $pkg_manager. Exiting."
                exit 1
            }
        else
            log "$cmd is already installed."
        fi
    done
}

fetch_css() {
    local folder_name="$1"
    local config_css="$2"
    local css_files=()
    local blacklisted_files=("$config_css")

    while IFS= read -r -d '' file; do
        if [[ "$file" == *".css" ]] && [[ ! " ${blacklisted_files[*]} " =~ " ${file##*/} " ]]; then
            css_files+=("$file")
        fi
    done < <(find "$folder_name" -type f -name "*.css" -print0)

    echo "${css_files[@]}"
}

combine_css() {
    local files=("$@")
    local combined=""
    for file in "${files[@]}"; do
        combined+=$'\n'"$(cat "$file")"
    done
    echo "$combined"
}

compile_css() {
    local combined="$1"
    log "Compiling CSS..."
    local compiled="$combined"
    compiled=$(echo "$compiled" | sed 's/^[ \t]*//g')
    compiled=$(echo "$compiled" | tr -d '\n')
    compiled=$(echo "$compiled" | sed 's/\/\*.*?\*\///g')
    echo "$compiled"
}

finalize_css() {
    local compiled="$1"
    local folder_name="$2"
    local config_css="$3"

    local license
    license=$(cat "${Configuration["License_File"]}")
    local cfg_css
    cfg_css=$(cat "$folder_name/$config_css")

    local compiler_notes="/* Compiled using Caerbannog $Caerbannog_Version */"
    local root_footer=":root { --Caerbannog-Version: \"$Caerbannog_Version\"; --Caerbannog-Compile_Date: \"$(date)\"; }"
    compiler_notes+=$'\n'"$root_footer"

    local production="/*\n$license\n*/\n$compiled\n$compiler_notes"
    local development="/* DEVELOPMENT BUILD */\n/* $license */\n$compiled\n$cfg_css\n$compiler_notes"

    echo "$production" > "$folder_name/Production_CSS.css"
    echo "$development" > "$folder_name/Development_CSS.css"
}

watch_folder() {
    local folder_name="$1"
    local config_css="$2"

    log "Watching folder: $folder_name"
    inotifywait -m -e modify,create,delete --format "%w%f" "$folder_name" | while read -r changed_file; do
        if [[ "$changed_file" == *".css" ]]; then
            log "File change detected: $changed_file"
            css_files=($(fetch_css "$folder_name" "$config_css"))
            combined=$(combine_css "${css_files[@]}")
            compiled=$(compile_css "$combined")
            finalize_css "$compiled" "$folder_name" "$config_css"
            Reload_Status=true
        fi
    done
}

bootstrap() {
    install_dependencies
    log "Loading configuration..."
    while IFS="=" read -r key value; do
        Configuration["$key"]="$value"
    done < <(jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' Caerbannog.json)
    
    log "Starting Watchdog..."
    for folder in "${!Configuration[@]}"; do
        watch_folder "$folder" "${Configuration[$folder]}"
    done
}

shutdown() {
    log "Shutting down Caerbannog..."
    Running=false
    exit 0
}

trap shutdown SIGINT SIGTERM

log "Starting Caerbannog..."
bootstrap

echo "Bash Rewrite by PhoenixAceVFX"
echo "Orignal script by SiriusBYT"
