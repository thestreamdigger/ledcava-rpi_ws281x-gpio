#!/bin/bash

# =============================================================================
# STANDARD CONFIGURATION
# =============================================================================
DEFAULT_USER="pi"
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_NAME="LEDCAVA-WS2812"
REQUIRED_GROUPS="gpio"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo "[ERROR] Please run as root (sudo)"
        exit 1
    fi
}

log_info() {
    echo "[INFO] $1"
}

log_warn() {
    echo "[WARN] $1"
}

log_error() {
    echo "[ERROR] $1"
    exit 1
}

log_ok() {
    echo "[OK] $1"
}

# =============================================================================
# INITIAL CHECKS
# =============================================================================
log_info "Setting up $PROJECT_NAME permissions..."
check_root

# Define target user
TARGET_USER=${SUDO_USER:-$DEFAULT_USER}
if [ "$TARGET_USER" = "root" ]; then
    TARGET_USER=$DEFAULT_USER
fi
log_info "Target user: $TARGET_USER"

# =============================================================================
# BASIC PERMISSIONS
# =============================================================================
# Owner and group
log_info "Setting owner and group..."
chown -R "$TARGET_USER:$TARGET_USER" "$BASE_DIR" || log_error "Failed to set ownership"

# Directories
log_info "Setting directory permissions..."
find "$BASE_DIR" -type d -exec chmod 755 {} \; || log_error "Failed to set directory permissions"

# Python files
log_info "Setting Python files permissions..."
find "$BASE_DIR" -type f -name "*.py" -exec chmod 644 {} \; || log_error "Failed to set Python file permissions"

# =============================================================================
# PROJECT SPECIFIC PERMISSIONS
# =============================================================================
# Main executables
log_info "Setting executable permissions..."
for script in \
    "$BASE_DIR/fix_permissions.sh" \
    "$BASE_DIR/main.py"
do
    if [ -f "$script" ]; then
        chmod 755 "$script" || log_error "Failed to set executable permission for $script"
        log_ok "Set executable: $(basename "$script")"
    fi
done

# Configuration files
log_info "Setting configuration files permissions..."
for config in \
    "$BASE_DIR/settings.json" \
    "$BASE_DIR/requirements.txt" \
    "$BASE_DIR/ROADMAP.md"
do
    if [ -f "$config" ]; then
        chmod 644 "$config" || log_error "Failed to set permissions for $config"
        log_ok "Set permissions: $(basename "$config")"
    fi
done

# =============================================================================
# GROUP PERMISSIONS
# =============================================================================
log_info "Adding user to required groups..."
IFS=',' read -ra GROUPS <<< "$REQUIRED_GROUPS"
for group in "${GROUPS[@]}"; do
    if getent group "$group" >/dev/null; then
        usermod -a -G "$group" "$TARGET_USER" || log_error "Failed to add user to group $group"
        log_ok "Added user to group: $group"
    else
        log_warn "Group $group does not exist, skipping..."
    fi
done

# =============================================================================
# SUMMARY
# =============================================================================
log_ok "Permissions successfully configured!"
log_info "Permissions summary:"
log_info "- Owner/Group: $TARGET_USER:$TARGET_USER"
log_info "- Directories: 755 (drwxr-xr-x)"
log_info "- Python files: 644 (-rw-r--r--)"
log_info "- Executable scripts: 755 (-rwxr-xr-x)"
log_info "- Configuration files: 644 (-rw-r--r--)"
log_info "- User groups: $REQUIRED_GROUPS" 