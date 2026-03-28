import streamlit as st
from database import (get_matches, add_prediction, get_user_predictions, get_user_balance_sheet,
                      remove_prediction, get_setting, get_team_counts_for_match,
                      get_total_members, get_max_per_team, get_match_winners,
                      get_predictions_for_match, get_all_member_names)
from auth import is_member
from datetime import datetime, timedelta

def member_dashboard():
    if not is_member():
        st.error("Access denied")
        return

    user = st.session_state['user']
    st.title(f"Welcome, {user[1]}!")

    tabs = ["View Schedule & Predict", "My Predictions", "Balance Sheet"]
    selected = st.radio("Navigation", tabs, horizontal=True, label_visibility="collapsed",
                        key="member_tab")

    st.divider()

    if selected == "View Schedule & Predict":
        view_schedule_and_predict()
    elif selected == "My Predictions":
        my_predictions()
    elif selected == "Balance Sheet":
        balance_sheet()

def view_schedule_and_predict():
    user = st.session_state['user']
    st.subheader("Match Schedule & Predictions")
    current_time = datetime.now()

    open_hours = int(get_setting('prediction_open_hours') or 24)
    close_hours = int(get_setting('prediction_close_hours') or 2)

    all_matches = get_matches()
    user_predictions = get_user_predictions(user[0])
    pred_map = {p[0]: p[3] for p in user_predictions}

    upcoming, finished = [], []
    for match in all_matches:
        if match[7] in ('upcoming', 'predictions_closed'):
            upcoming.append(match)
        else:
            finished.append(match)

    if upcoming:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
        for c, label in zip([col1, col2, col3, col4, col5], ["**#**", "**Teams**", "**Date & Time**", "**Venue**", "**Prediction**"]):
            c.write(label)

        for match in upcoming:
            match_datetime_str = f"{match[1]} {match[3]}"
            try:
                match_datetime = datetime.strptime(match_datetime_str, '%d-%b-%y %I:%M %p')
            except ValueError:
                match_datetime = current_time - timedelta(hours=1)

            opens_at = match_datetime - timedelta(hours=open_hours)
            closes_at = match_datetime - timedelta(hours=close_hours)
            can_predict = (match[7] == 'upcoming'
                           and opens_at <= current_time < closes_at)

            col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
            col1.write(f"{match[0]}")
            col2.write(f"{match[4]} vs {match[5]}")
            col3.write(f"{match[1]} {match[3]}")
            col4.write(match[6])

            with col5:
                if match[7] == 'predictions_closed':
                    existing = pred_map.get(match[0])
                    st.write(f"Your: {existing or 'Not picked (random)'}")
                    preds = get_predictions_for_match(match[0])
                    if preds:
                        for team in [match[4], match[5]]:
                            members = [u for u, t in preds if t == team]
                            if members:
                                st.caption(f"{team}: {', '.join(members)}")
                else:
                    existing = pred_map.get(match[0])
                    if existing:
                        st.write(f"Your: {existing}")
                        if can_predict and st.button("Remove", key=f"remove_{match[0]}"):
                            remove_prediction(user[0], match[0])
                            st.rerun()
                    elif can_predict:
                        total = get_total_members()
                        max_per_team = get_max_per_team(total)
                        counts = get_team_counts_for_match(match[0])
                        options = []
                        for team in [match[4], match[5]]:
                            filled = counts.get(team, 0) >= max_per_team
                            options.append((team, filled))
                        st.write(f"Max/team: {max_per_team}")
                        for team, filled in options:
                            if filled:
                                st.write(f"~~{team} (full)~~")
                            else:
                                if st.button(team, key=f"pick_{match[0]}_{team}"):
                                    add_prediction(user[0], match[0], team)
                                    st.rerun()
                    elif current_time < opens_at:
                        st.write(f"Opens {opens_at.strftime('%d-%b %I:%M %p')}")
                    else:
                        # Deadline passed but not closed yet — show what others picked
                        st.write("Deadline passed")
                        preds = get_predictions_for_match(match[0])
                        if preds:
                            for team in [match[4], match[5]]:
                                members = [u for u, t in preds if t == team]
                                if members:
                                    st.caption(f"{team}: {', '.join(members)}")
    else:
        st.info("No upcoming matches.")

    if finished:
        with st.expander(f"Finished Matches ({len(finished)})"):
            for match in finished:
                st.write(f"**{match[0]}** — {match[4]} vs {match[5]} | Winner: **{match[8]}** | {match[1]}")
                winners = get_match_winners(match[0])
                winner_names = {u for u, _ in winners}
                all_members = set(get_all_member_names())
                losers = all_members - winner_names
                if winner_names:
                    st.caption(f"Won: {', '.join(sorted(winner_names))}")
                if losers:
                    st.caption(f"Lost: {', '.join(sorted(losers))}")
                st.write("---")

def my_predictions():
    user = st.session_state['user']
    st.subheader("My Predictions")
    predictions = get_user_predictions(user[0])
    if predictions:
        import pandas as pd
        df = pd.DataFrame(predictions, columns=['Match ID', 'Home Team', 'Away Team', 'Predicted'])
        st.table(df)
    else:
        st.write("No predictions yet.")

def balance_sheet():
    user = st.session_state['user']
    st.subheader("Balance Sheet")
    balance = get_user_balance_sheet(user[0])
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Invested", f"₹{balance['invested']:.2f}")
    with col2:
        st.metric("Winnings", f"₹{balance['winnings']:.2f}")
    with col3:
        st.metric("Profit", f"₹{balance['profit']:.2f}")
    with col4:
        st.metric("Debt", f"₹{balance['debt']:.2f}")