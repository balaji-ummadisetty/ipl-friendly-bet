# IPL Friendly Betting App

A Streamlit application for managing friendly betting on IPL matches.

## Features

- Admin and member authentication
- Match schedule display
- Prediction submission for members
- Admin can add members and manage match results
- Automatic money splitting after matches
- Balance sheet for members

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `streamlit run app.py`

## Rules

- 100 Rs per person for first 10 matches
- Minimum 3 members per predicted team
- Winnings split among members of winning team
- Balance sheet shows invested, winnings, profit, debt

## Database

Uses SQLite database `ipl_betting.db` with tables for users, matches, predictions, transactions.# ipl-friendly-bet
