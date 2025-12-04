#!/bin/bash

# WARNING: This script permanently deletes the GitHub repositories listed below.
# Review the REPOS_TO_DELETE list carefully before running this script.
# This action is irreversible.

# List of repositories to delete.
REPOS_TO_DELETE=(
    v2i0s2h2/motoko-starter
    v2i0s2h2/mbc_final_project
    v2i0s2h2/ayurveda_body_test
    v2i0s2h2/Ts_canister_dbank
    v2i0s2h2/tweet_icp
    v2i0s2h2/Doc-Reg-CLI
    v2i0s2h2/icp-azle-ns
    v2i0s2h2/ic-ts-kanban
    v2i0s2h2/developer
    v2i0s2h2/azle
    v2i0s2h2/typescript-bootcamp
    v2i0s2h2/ICP-Bootcamp-FinalCase
    v2i0s2h2/canister_azle_app
    v2i0s2h2/ICP-RUST0
    v2i0s2h2/task_manager
    v2i0s2h2/icp-rust
    v2i0s2h2/ICP
    v2i0s2h2/program1
    v2i0s2h2/icpcalculator
    v2i0s2h2/simple_task_manager
    v2i0s2h2/rust-canister
    v2i0s2h2/Rust-101
    v2i0s2h2/rust-challenge
    v2i0s2h2/smartcontract-rs
    v2i0s2h2/Fitness_Tracker_RUST
    v2i0s2h2/ICPChallenge
    v2i0s2h2/Youth_Chamaa_RUST
    v2i0s2h2/Azienda
    v2i0s2h2/rust_1
    v2i0s2h2/dairy
    v2i0s2h2/Crypto-Wallet
    v2i0s2h2/icp_kes_swap
    v2i0s2h2/icp-mock-api
    v2i0s2h2/Ic_Time_capsule_Rust
    v2i0s2h2/testicp
    v2i0s2h2/testICP1
    v2i0s2h2/icp-rust1
    v2i0s2h2/ICP-Project
    v2i0s2h2/ic-commons-v2
    v2i0s2h2/template
    # v2i0s2h2/ICP_Web3Jobs
    # v2i0s2h2/IC-EventMarketplace
    # v2i0s2h2/ICP_Gym_Membership
    # v2i0s2h2/ICP_Men_Saloon
    # v2i0s2h2/tweet_icpv2i0s2h2/Doc-Reg-CLI
    # v2i0s2h2/vote-canister
    # v2i0s2h2/company-service-log-canister
    # v2i0s2h2/icp_blog
    # v2i0s2h2/Subscription-canister
    # v2i0s2h2/LinkedIn-ICP-Canister
    # v2i0s2h2/icp_shoeStore
    # v2i0s2h2/Antiques
    # v2i0s2h2/Sports-Team-Management
    # v2i0s2h2/icp-product-review
    # v2i0s2h2/ICP-JobPortal
    # v2i0s2h2/Game-Platform
    # v2i0s2h2/transit-cannister
    # v2i0s2h2/family-expense-canister
    # v2i0s2h2/budget_management
    # v2i0s2h2/AI_Powered_Health_Assistant
    # v2i0s2h2/jingle_all_the_way
    # v2i0s2h2/virtual_healthcare_assistant
    # v2i0s2h2/food_waste_reduction
    # v2i0s2h2/social-feed-contract
    # v2i0s2h2/Wings-Publishers
    # v2i0s2h2/Home_Energy_Efficiency_Analyzer
    # v2i0s2h2/smart_recipe
    # v2i0s2h2/inventory-smart-contract
    # v2i0s2h2/icp-rust-task-management
    # v2i0s2h2/ic-book-library
    # v2i0s2h2/ICP_Fuel_Pump_Station
    # v2i0s2h2/flight-booking-system
    # v2i0s2h2/food-delivery-tracking
    # v2i0s2h2/ic-show-book-manager
    # v2i0s2h2/legal-consultation-and-advisory-management
    # v2i0s2h2/agri-insurance-system
    # v2i0s2h2/hospital_system
    # v2i0s2h2/small_biz
    # v2i0s2h2/decentralized_voting_system
    # v2i0s2h2/school_management
    # v2i0s2h2/RealEstate-Property
    # v2i0s2h2/RealEstateICPBackend
    # v2i0s2h2/bookyie
    # v2i0s2h2/Mood-Enhancing-Fragrance-Canister
    # v2i0s2h2/ICP-Lottery-DApp
    # v2i0s2h2/icp-azle-201
    # v2i0s2h2/Dvote
    # v2i0s2h2/ICP-DAO-DApp
    # v2i0s2h2/real_estate_property_ownership_manager_rust
    # v2i0s2h2/community_bulletin
    # v2i0s2h2/Decentralized-Cloud-Storage
    # v2i0s2h2/digital-land--registry
    # v2i0s2h2/EduCredVerifier
    # v2i0s2h2/OnlineVetCare
    # v2i0s2h2/Restaurant_Management_System
    # v2i0s2h2/decentralized-election-campaign-manager
    # v2i0s2h2/Pharma_Chain
    # v2i0s2h2/pig-farm-management-system
    # v2i0s2h2/Elderly-Care-Platform
    # v2i0s2h2/Garage_Management_rust-
    # v2i0s2h2/icp-101-job_searchers
    # v2i0s2h2/Court-Case-Manager
    # v2i0s2h2/icp-random-password-canister
    # v2i0s2h2/EPL_Transfer_Market_Platform
    # v2i0s2h2/rust_busbooking
    # v2i0s2h2/d_crab
    # v2i0s2h2/decentralized--digital--art-marketplace
    # v2i0s2h2/icp-azle-forum-rust
    # v2i0s2h2/service-desk-IT-management-system
    # v2i0s2h2/decentralized_e-commerce_marketplace_rust
    # v2i0s2h2/timetabling_system
    # v2i0s2h2/employee-leave-management-system
    # v2i0s2h2/ICPSimpleBank
    # v2i0s2h2/decentralized-book-filter
    # v2i0s2h2/greenhouse-sensor-data-manager
    # v2i0s2h2/random-art-generator
    # v2i0s2h2/crop_yield_system
    # v2i0s2h2/traffic
    # v2i0s2h2/decentralized_storage_system
    # "v2i0s2h2/language-learning-canister"
    # "v2i0s2h2/OrganiksICP"
    # "v2i0s2h2/health-record-management-system"
    # "v2i0s2h2/doctor-patient-app"
    # "v2i0s2h2/Flo_project"
    # "v2i0s2h2/event_sphere"
    # "v2i0s2h2/socity"
    # "v2i0s2h2/leave-management-system"
    # "v2i0s2h2/rust-decentralized-marketplace"
    # "v2i0s2h2/https-github.com-v2i0s2h2-ICP-Flight-Booking-Dapp1"
    # "v2i0s2h2/real-estate-management-system"
    # "v2i0s2h2/car-rental-system"
    # "v2i0s2h2/Community-Sphere"
    # "v2i0s2h2/reviewz"
    # "v2i0s2h2/D-CAMPUS_ATTENDANCE"
    # "v2i0s2h2/ICP-Flight-Booking-Dapp"
    # "v2i0s2h2/d-epl"
    # "v2i0s2h2/hospital-management-sui"
    # "v2i0s2h2/zero_laundry"
    # "v2i0s2h2/Lottery_game_RUST_ICP"
    # "v2i0s2h2/suionicp"
    # "v2i0s2h2/ICP-rust-learning-platform-dapp"
    # "v2i0s2h2/flight-booking-rust-canister"
    # "v2i0s2h2/k-bet-decentralized-system"
    # "v2i0s2h2/Community_Garden_Management_System_RUST"
    # "v2i0s2h2/Proof-of-agreement"
    # "v2i0s2h2/Food_Share_101"
    # "v2i0s2h2/formal-models"
    # "v2i0s2h2/Inventory_Management_Rust"
    # "v2i0s2h2/Train_Ticket_Rust"
    # "v2i0s2h2/icp_women_saloon"
    # "v2i0s2h2/Health_Track_Rust"
)

echo "--- Starting bulk deletion of ${#REPOS_TO_DELETE[@]} repositories ---"
echo "WARNING: This action is permanent and cannot be undone."
echo "You have 5 seconds to cancel this operation (press Ctrl+C)..."
sleep 5

for repo in "${REPOS_TO_DELETE[@]}"; do
    echo "-----------------------------------------------------"
    echo "Attempting to delete repository: $repo"
    gh repo delete "$repo" --yes
    if [ $? -eq 0 ]; then
        echo "✅ Successfully deleted $repo"
    else
        echo "❌ Failed to delete $repo. It might not exist or you may lack permissions."
    fi
done

echo "-----------------------------------------------------"
echo "Bulk deletion script finished."
