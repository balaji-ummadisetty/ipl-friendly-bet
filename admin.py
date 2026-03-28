import streamlit as st
from database import (get_all_users, get_matches, update_match_winner, split_money,
                      get_match_predictions, set_setting, get_setting, get_all_balances,
                      settle_user, close_predictions, get_match_assigned_teams,
                      get_predictions_for_match, undo_match_winner, get_match_winners, reset_db)
from auth import register_member, is_admin

def admin_dashboard():
    if not is_admin():
        st.error("Access denied")
        return

    st.title("Admin Dashboard")

    tabs = ["Manage Matches", "Settlement", "View Predictions", "Manage Members", "Settings"]
    selected = st.radio("Navigation", tabs, horizontal=True, label_visibility="collapsed",
                        key="admin_tab")

    st.divider()

    if selected == "Manage Members":
        manage_members()
    elif selected == "Manage Matches":
        manage_matches()
    elif selected == "View Predictions":
        view_predictions()
    elif selected == "Settlement":
        settlement()
    elif selected == "Settings":
        manage_settings()

def manage_matches():
    st.subheader("Matches")
    matches = get_matches()

    upcoming = [m for m in matches if m[7] in ('upcoming', 'predictions_closed')]
    finished = [m for m in matches if m[7] == 'finished']

    if upcoming:
        st.markdown("#### Upcoming")
        for match in upcoming:
            col1, col2, col3 = st.columns([4, 3, 2])
            with col1:
                st.write(f"**{match[0]}**: {match[4]} vs {match[5]} — {match[1]} {match[3]}")
            with col2:
                if match[7] == 'upcoming':
                    if st.button("Close Predictions", key=f"close_{match[0]}", type="primary"):
                        close_predictions(match[0])
                        st.rerun()
                else:
                    # Show team assignments
                    assignments = get_match_assigned_teams(match[0])
                    if assignments:
                        conn_users = get_all_users()
                        uid_to_name = {u[0]: u[1] for u in conn_users}
                        team_groups = {}
                        for uid, team in assignments.items():
                            team_groups.setdefault(team, []).append(uid_to_name.get(uid, str(uid)))
                        for team, members in team_groups.items():
                            st.caption(f"{team}: {', '.join(members)}")

                    winner = st.selectbox("Select Winner", [match[4], match[5]], key=f"winner_{match[0]}")
                    if st.button("Set Winner", key=f"set_{match[0]}", type="primary"):
                        update_match_winner(match[0], winner)
                        split_money(match[0], winner)
                        st.success("Winner set!")
                        st.rerun()
            with col3:
                predictions = get_match_predictions(match[0])
                total = sum(count for _, count in predictions)
                for team, count in predictions:
                    st.write(f"{team}: {count}")
                st.caption(f"Total predictions: {total}")

    if finished:
        st.markdown("#### Finished")
        for match in finished:
            with st.expander(f"Match {match[0]}: {match[4]} vs {match[5]} — Winner: {match[8]} | {match[1]}"):
                winners = get_match_winners(match[0])
                if winners:
                    st.markdown("**Winners (received):**")
                    for username, amount in winners:
                        st.write(f"- {username}: ₹{amount:.2f}")
                else:
                    st.write("No winners recorded.")
                st.divider()
                if st.button("Undo Winner", key=f"undo_{match[0]}", type="secondary"):
                    undo_match_winner(match[0])
                    st.warning(f"Match {match[0]} result undone. Transactions deleted.")
                    st.rerun()

def settlement():
    st.subheader("Settlement")
    st.caption("Positive profit = admin pays the member. Negative = member owes admin.")

    balances = get_all_balances()
    if not balances:
        st.info("No members found.")
        return

    total_admin_pay = sum(b['profit'] for b in balances if b['profit'] > 0)
    total_admin_recv = sum(-b['profit'] for b in balances if b['profit'] < 0)

    c1, c2 = st.columns(2)
    c1.metric("Admin needs to pay out", f"₹{total_admin_pay:.2f}")
    c2.metric("Admin will receive", f"₹{total_admin_recv:.2f}")

    st.divider()

    for b in balances:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
        col1.write(f"**{b['username']}**")
        col2.write(f"Invested: ₹{b['invested']:.2f}")
        col3.write(f"Won: ₹{b['winnings']:.2f}")
        if b['profit'] >= 0:
            col4.markdown(f"**Admin pays: ₹{b['profit']:.2f}**")
        else:
            col4.markdown(f"**Member owes: ₹{abs(b['profit']):.2f}**")
        with col5:
            if b['profit'] != 0:
                if st.button("Settle", key=f"settle_{b['id']}"):
                    settle_user(b['id'])
                    st.success(f"{b['username']} settled!")
                    st.rerun()
            else:
                st.write("Settled ✓")

    st.divider()
    if st.button("Settle ALL", type="primary"):
        for b in balances:
            if b['profit'] != 0:
                settle_user(b['id'])
        st.success("All members settled!")
        st.rerun()

def view_predictions():
    st.subheader("Predictions")
    matches = get_matches()
    for match in matches:
        if match[7] == 'finished':
            label = f"Match {match[0]}: {match[4]} vs {match[5]} — Winner: {match[8]}"
        else:
            label = f"Match {match[0]}: {match[4]} vs {match[5]} — {match[1]} {match[3]}"
        with st.expander(label):
            preds = get_predictions_for_match(match[0])
            if preds:
                import pandas as pd
                df = pd.DataFrame(preds, columns=['Member', 'Predicted Team'])
                st.table(df)
                counts = get_match_predictions(match[0])
                for team, count in counts:
                    st.write(f"{team}: {count} prediction(s)")
            else:
                st.write("No predictions yet.")

def manage_members():
    st.subheader("Add New Member")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Add Member"):
        if register_member(username, password):
            st.success("Member added successfully!")
        else:
            st.error("Username already exists")

    st.subheader("All Members")
    users = get_all_users()
    for user in users:
        if user[2] != 'admin':
            st.write(f"**{user[1]}** — Balance: ₹{user[3]:.2f}")

def manage_settings():
    st.subheader("Settings")

    invest_amount = st.number_input(
        "Investment Amount per Match (₹)",
        min_value=1,
        value=int(get_setting('invest_amount') or 10)
    )
    if st.button("Update Investment Amount"):
        set_setting('invest_amount', str(invest_amount))
        st.success("Investment amount updated!")

    st.divider()

    pred_open_hours = st.number_input(
        "Open predictions X hours before match",
        min_value=1, max_value=72,
        value=int(get_setting('prediction_open_hours') or 24),
        help="Members can start predicting this many hours before match time"
    )
    pred_close_hours = st.number_input(
        "Close predictions X hours before match",
        min_value=0, max_value=24,
        value=int(get_setting('prediction_close_hours') or 2),
        help="Prediction box closes this many hours before match time"
    )
    if st.button("Update Prediction Window"):
        set_setting('prediction_open_hours', str(pred_open_hours))
        set_setting('prediction_close_hours', str(pred_close_hours))
        st.success("Prediction window updated!")

    st.divider()
    st.caption(f"Prediction window: opens {pred_open_hours}h before match, closes {pred_close_hours}h before match")

    st.divider()
    st.subheader("Danger Zone")
    st.warning("This will delete ALL predictions, transactions, and reset all match results. Users and match schedule will be kept.")
    confirm = st.checkbox("I understand, reset everything")
    if confirm:
        if st.button("Reset Database", type="primary"):
            reset_db()
            st.success("Database reset! All predictions and transactions cleared.")
            st.rerun()
