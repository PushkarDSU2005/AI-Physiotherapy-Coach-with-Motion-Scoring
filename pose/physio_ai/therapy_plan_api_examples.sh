#!/bin/bash
#
# Therapy Plan Generation - API CURL Examples
# 
# This script demonstrates how to use the therapy plan API endpoints
# using curl commands. Useful for testing and development.
#
# Prerequisites:
# - Django server running at http://localhost:8000
# - User authenticated with JWT token
# - curl installed
#

# Configuration
API_BASE_URL="http://localhost:8000/api"
AUTH_TOKEN="your-jwt-token-here"  # Replace with actual token

# Headers
HEADERS=(
    "-H" "Authorization: Bearer $AUTH_TOKEN"
    "-H" "Content-Type: application/json"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# HELPER FUNCTIONS
# ============================================================

print_section() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# ============================================================
# API EXAMPLE 1: Generate a Therapy Plan
# ============================================================

example_generate_plan() {
    print_section "Example 1: Generate a New Therapy Plan"
    
    print_info "Creating plan for knee pain recovery..."
    
    curl -X POST "${API_BASE_URL}/therapy-plans/generate/" \
        "${HEADERS[@]}" \
        -d '{
            "injury_type": "Knee pain - ACL strain",
            "injury_severity": "moderate",
            "duration_weeks": 4,
            "difficulty_level": "intermediate",
            "goals": [
                "Reduce inflammation and pain",
                "Restore full range of motion",
                "Rebuild strength for running",
                "Return to marathon training"
            ]
        }' \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 2: List User's Therapy Plans
# ============================================================

example_list_plans() {
    print_section "Example 2: List All Therapy Plans"
    
    print_info "Fetching all active plans..."
    
    curl -X GET "${API_BASE_URL}/therapy-plans/" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 3: List Only Active Plans
# ============================================================

example_active_plans() {
    print_section "Example 3: Get Only Active Plans"
    
    print_info "Fetching active plans only..."
    
    curl -X GET "${API_BASE_URL}/therapy-plans/active/" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 4: Get Specific Plan Details
# ============================================================

example_get_plan() {
    local plan_id="$1"
    
    if [ -z "$plan_id" ]; then
        print_error "Plan ID required. Usage: example_get_plan <plan_id>"
        return 1
    fi
    
    print_section "Example 4: Get Specific Plan Details"
    
    print_info "Fetching details for plan ID: $plan_id"
    
    curl -X GET "${API_BASE_URL}/therapy-plans/${plan_id}/" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 5: Get Weekly Schedule
# ============================================================

example_weekly_schedule() {
    local plan_id="$1"
    
    if [ -z "$plan_id" ]; then
        print_error "Plan ID required. Usage: example_weekly_schedule <plan_id>"
        return 1
    fi
    
    print_section "Example 5: Get Weekly Schedule for a Plan"
    
    print_info "Fetching weekly schedule for plan ID: $plan_id"
    
    curl -X GET "${API_BASE_URL}/therapy-plans/${plan_id}/weekly-schedule/" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 6: Update Plan Progress
# ============================================================

example_update_progress() {
    local plan_id="$1"
    
    if [ -z "$plan_id" ]; then
        print_error "Plan ID required. Usage: example_update_progress <plan_id>"
        return 1
    fi
    
    print_section "Example 6: Update Plan Progress"
    
    print_info "Updating progress for plan ID: $plan_id"
    
    curl -X POST "${API_BASE_URL}/therapy-plans/${plan_id}/update-progress/" \
        "${HEADERS[@]}" \
        -d '{
            "progress_score": 65.5,
            "status": "active",
            "notes": "Pain reduced by 30%, able to walk without limp"
        }' \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 7: Export Plan
# ============================================================

example_export_plan() {
    local plan_id="$1"
    
    if [ -z "$plan_id" ]; then
        print_error "Plan ID required. Usage: example_export_plan <plan_id>"
        return 1
    fi
    
    print_section "Example 7: Export Plan as JSON"
    
    print_info "Exporting plan ID: $plan_id"
    
    curl -X GET "${API_BASE_URL}/therapy-plans/${plan_id}/export/?format=json" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 8: Compare Two Plans
# ============================================================

example_compare_plans() {
    local plan_id1="$1"
    local plan_id2="$2"
    
    if [ -z "$plan_id1" ] || [ -z "$plan_id2" ]; then
        print_error "Two plan IDs required. Usage: example_compare_plans <plan_id1> <plan_id2>"
        return 1
    fi
    
    print_section "Example 8: Compare Two Plans"
    
    print_info "Comparing plan $plan_id1 with plan $plan_id2"
    
    curl -X GET "${API_BASE_URL}/therapy-plans/${plan_id1}/comparison/?compare_with=${plan_id2}" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 9: Search Plans
# ============================================================

example_search_plans() {
    local query="$1"
    
    if [ -z "$query" ]; then
        query="knee"
    fi
    
    print_section "Example 9: Search Plans"
    
    print_info "Searching for plans matching: '$query'"
    
    curl -X GET "${API_BASE_URL}/therapy-plans/?search=${query}" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# API EXAMPLE 10: Filter Plans by Status
# ============================================================

example_filter_by_status() {
    local status="$1"
    
    if [ -z "$status" ]; then
        status="active"
    fi
    
    print_section "Example 10: Filter Plans by Status"
    
    print_info "Filtering plans with status: $status"
    
    curl -X GET "${API_BASE_URL}/therapy-plans/?status=${status}" \
        "${HEADERS[@]}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# AUTHENTICATION: Get JWT Token
# ============================================================

get_auth_token() {
    local username="$1"
    local password="$2"
    
    if [ -z "$username" ] || [ -z "$password" ]; then
        print_error "Username and password required"
        return 1
    fi
    
    print_section "Getting Authentication Token"
    
    print_info "Authenticating user: $username"
    
    curl -X POST "${API_BASE_URL}/token/" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"${username}\", \"password\": \"${password}\"}" \
        -w "\n\nStatus Code: %{http_code}\n"
}

# ============================================================
# MAIN MENU
# ============================================================

show_menu() {
    echo ""
    echo "=========================================="
    echo "  Therapy Plan API - CURL Examples"
    echo "=========================================="
    echo ""
    echo "SETUP:"
    echo "  get_token USER PASS        - Get JWT authentication token"
    echo ""
    echo "PLAN OPERATIONS:"
    echo "  generate_plan              - Create a new therapy plan"
    echo "  list_plans                 - List all user's plans"
    echo "  active_plans               - Get only active plans"
    echo "  get_plan PLAN_ID           - Get specific plan details"
    echo "  weekly_schedule PLAN_ID    - Get weekly exercise schedule"
    echo ""
    echo "PROGRESS & TRACKING:"
    echo "  update_progress PLAN_ID    - Update plan progress score"
    echo ""
    echo "ADVANCED:"
    echo "  export_plan PLAN_ID        - Export plan as JSON"
    echo "  compare_plans PLAN_ID1 PLAN_ID2  - Compare two plans"
    echo ""
    echo "SEARCH & FILTER:"
    echo "  search_plans QUERY         - Search plans (default: 'knee')"
    echo "  filter_by_status STATUS    - Filter by status (default: 'active')"
    echo ""
    echo "HELP:"
    echo "  help                       - Show this menu"
    echo "  exit                       - Exit the script"
    echo ""
}

# ============================================================
# MAIN SCRIPT
# ============================================================

main() {
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install it first."
        exit 1
    fi
    
    # Check if token is provided
    if [ "$AUTH_TOKEN" = "your-jwt-token-here" ]; then
        print_info "You need to set your JWT token first!"
        print_info "Usage: AUTH_TOKEN='your-actual-token' ./therapy_plan_api_examples.sh"
        echo ""
        print_section "Getting Token First"
        echo "To get a token, run:"
        echo "  curl -X POST http://localhost:8000/api/token/ \\"
        echo "    -H 'Content-Type: application/json' \\"
        echo "    -d '{\"username\": \"your_username\", \"password\": \"your_password\"}'"
        exit 1
    fi
    
    print_info "Using API Base URL: $API_BASE_URL"
    print_info "Authentication: Configured with JWT token"
    
    show_menu
    
    # Run examples
    case "${1:-}" in
        generate_plan)
            example_generate_plan
            ;;
        list_plans)
            example_list_plans
            ;;
        active_plans)
            example_active_plans
            ;;
        get_plan)
            example_get_plan "$2"
            ;;
        weekly_schedule)
            example_weekly_schedule "$2"
            ;;
        update_progress)
            example_update_progress "$2"
            ;;
        export_plan)
            example_export_plan "$2"
            ;;
        compare_plans)
            example_compare_plans "$2" "$3"
            ;;
        search_plans)
            example_search_plans "$2"
            ;;
        filter_by_status)
            example_filter_by_status "$2"
            ;;
        get_token)
            get_auth_token "$2" "$3"
            ;;
        help)
            show_menu
            ;;
        *)
            print_error "Unknown command: $1"
            show_menu
            exit 1
            ;;
    esac
}

# Execute main
main "$@"
