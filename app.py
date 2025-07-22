import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ------------------- Config -------------------
st.set_page_config(page_title="Weekly Sentiment Analyzer", layout="centered")
DATA_FILE = "habit_data.csv"
SENTIMENTS = ["Happy", "Sad", "Frustrated", "Confused"]

# ------------------- Utils -------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            return df
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["date", "sleep", "water", "mood", "energy", "stress", "sentiment"])
    else:
        return pd.DataFrame(columns=["date", "sleep", "water", "mood", "energy", "stress", "sentiment"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def classify_sentiment(row):
    mood = row["mood"]
    stress = row["stress"]
    energy = row["energy"]
    sleep = row["sleep"]
    water = row["water"]

    # Simple rule-based sentiment
    if mood == "Happy" and stress in ["Not at all", "Little"] and energy in ["Mostly", "Fully"]:
        return "Happy"
    elif mood == "Sad" or sleep == "<4 hours":
        return "Sad"
    elif stress == "Very":
        return "Frustrated"
    else:
        return "Confused"

def show_pie_chart(df):
    sentiment_counts = df["sentiment"].value_counts()
    colors = ['#90ee90', '#ffcccb', '#f4b942', '#add8e6']
    fig, ax = plt.subplots()
    ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    st.pyplot(fig)
    
# ------------------- Main App -------------------
def main():
    st.title("🌈 Weekly Sentiment Analyzer")
    st.caption("Track your habits and mood daily for 7 days to get an emotional insight 📊")

    data = load_data()

    # ----- Reset Data Option -----

    st.markdown("---")
    st.subheader("🧹 Data Management")

    confirm = st.checkbox("✅ Yes, I want to delete all my entries permanently")
    if st.button("🗑️ Reset All Data"):
        if confirm:
            save_data(pd.DataFrame(columns=["date", "sleep", "water", "mood", "energy", "stress", "sentiment"]))
            st.warning("⚠️ All data has been reset. Start fresh!")
            st.rerun()  # Optional: refresh app after reset
        else:
            st.error("☝️ Please check the box to confirm before resetting data.")

    # ----- Date Input -----
    st.subheader("📅 Select Date")
    date = st.date_input("Choose the date for entry", value=datetime.today())
    date_str = str(date)

    # Check if date already submitted
    if date_str in data["date"].values:
        st.warning("📌 You've already submitted an entry for this date.")
    else:
        # ----- MCQ Questions -----
        st.subheader("📝 Daily Questions")

        sleep = st.selectbox("1. How many hours did you sleep?", ["<4 hours", "4-6 hours", "6-8 hours", ">8 hours"])
        water = st.selectbox("2. How much water did you drink today?", ["<1L", "1-2L", "2-3L", ">3L"])
        mood = st.selectbox("3. How was your mood today?", SENTIMENTS)
        energy = st.selectbox("4. Did you feel energetic today?", ["Not at all", "A little", "Mostly", "Fully"])
        stress = st.selectbox("5. Did you feel stressed today?", ["Very", "Moderate", "Little", "Not at all"])

        if st.button("✅ Submit Today's Entry"):
            new_entry = {
                "date": date_str,
                "sleep": sleep,
                "water": water,
                "mood": mood,
                "energy": energy,
                "stress": stress
            }
            new_entry["sentiment"] = classify_sentiment(new_entry)
            new_df = pd.DataFrame([new_entry])
            data = pd.concat([data, new_df], ignore_index=True)
            save_data(data)
            st.success("🎉 Entry saved successfully!")

    # ----- Report Section -----
    st.markdown("---")
    st.subheader("📈 Sentiment Report")

    total_entries = len(data)
    if total_entries < 7:
        st.info(f"📅 You’ve entered **{total_entries}** day(s). Come back after **{7 - total_entries}** more day(s) to get your **Week 1** report.")
        return

    # Sort and convert date
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(by='date').reset_index(drop=True)

    # Week handling
    week_count = total_entries // 7
    week_options = [f"Week {i + 1}" for i in range(week_count)]
    selected_week = st.selectbox("Select week for analysis:", week_options)
    week_index = week_options.index(selected_week)

    start = week_index * 7
    end = start + 7
    week_data = data.iloc[start:end]

    # Pie Chart
    show_pie_chart(week_data)

    # Dominant sentiment
    dominant = week_data["sentiment"].mode()[0]
    st.info(f"🧠 You mostly felt **{dominant}** during **{selected_week}**.")

    # Weekly Motivational Messages
    st.markdown(f"### ✨ Your {selected_week} Report is Ready!")

    if dominant == "Happy":
        st.success("🌟 You're doing great! Keep up the positive habits. Stay consistent and inspire others too!")
    elif dominant == "Sad":
        st.error("💛 It's okay to feel low. Try doing one thing you love today — even a small act of self-care can help. 🌈")
    elif dominant == "Frustrated":
        st.warning("😣 You might be under some pressure. Take a short break, listen to music, or talk to someone. You deserve peace. 🌿")
    elif dominant == "Confused":
        st.info("🌀 Seems like you're juggling a lot. Try journaling or setting a small goal for tomorrow. You’ve got this! 💪")

if __name__ == "__main__":
    main()



