import streamlit as st
import pandas as pd
import datetime
import time
import base64
import requests
from io import StringIO

# --- JAPANDI KONFIGURATION & STIL ---
st.set_page_config(page_title="Rehab Studio", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #F7F5F0;
        color: #2C2A29;
    }
    h1, h2, h3 {
        color: #2C2A29;
        font-weight: 500;
        letter-spacing: -0.5px;
    }
    .exercise-card {
        background-color: #EFECE6;
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #6B7B63;
        margin-bottom: 12px;
    }
    .cue-text {
        color: #5A5753;
        font-size: 0.92rem;
        margin-top: 4px;
    }
    .stButton>button {
        background-color: #6B7B63;
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        padding: 10px 18px;
        width: 100%;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #56634F;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

CSV_FILE = "rehab_log.csv"

# --- FUNKTIONER FÖR LAGRING (LOKALT + GITHUB SYNK) ---
def load_data():
    if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        url = f"https://api.github.com/repos/{repo}/contents/{CSV_FILE}"
        headers = {"Authorization": f"token {token}"}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"]).decode("utf-8")
            return pd.read_csv(StringIO(content))
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "Datum", "Kontakt_Säte", "Smärta_Höft_Knä", 
            "Stelhet_Rygg_Ljumske", "Naproxen", "Kommentar"
        ])

def save_data(df):
    csv_string = df.to_csv(index=False)
    # Spara lokalt i sessionen
    df.to_csv(CSV_FILE, index=False)
    
    # Synka automatiskt till GitHub om Secrets är inlagda
    if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        url = f"https://api.github.com/repos/{repo}/contents/{CSV_FILE}"
        headers = {"Authorization": f"token {token}"}
        
        r = requests.get(url, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None
        
        payload = {
            "message": f"Loggat rehabpass {datetime.date.today()}",
            "content": base64.b64encode(csv_string.encode("utf-8")).decode("utf-8")
        }
        if sha:
            payload["sha"] = sha
        requests.put(url, headers=headers, json=payload)

df = load_data()

# --- HEADER ---
st.title("🌿 Rehab Studio")
st.caption("Knäartros & Trokanterit • Onsdagar & Söndagar (15–20 min)")

tab1, tab2, tab3 = st.tabs(["🏋️ Kör Pass", "📝 Logga", "📈 Utveckling"])

# --- FLIK 1: AKTIVT PASS ---
with tab1:
    st.subheader("Dagens 6 steg")
    st.caption("Börja alltid med höger sida. Kvalitet före kvantitet.")

    exercises = [
        ("1. Bollmassage (QL) + Höftböjarstretch", "2–3 min totalt", 
         "Släpp höger ländrygg med boll (1 min). Gå ner på ett knä, knip skinkan och tippa bäckenet bakåt för att sträcka höger ljumske (1 min)."),
        ("2. Sittande knäpendling", "45 sekunder", 
         "Sitt fritt med benen och pendla mjukt fram och tillbaka för att smörja knäleden innan belastning."),
        ("3. Modifierad Mussla med gummiband", "2 set x 10–15 reps/sida", 
         "Ha en tjock kudde mellan knäna (noll-adduktion). Peta fingrarna i höger skinka innan du lyfter. Håll ryggen avslappnad."),
        ("4. Väggövningen", "3 set x 10–20 sek/sida", 
         "Stå med sidan mot väggen, pressa inre knät i 90° utåt mot väggen. Ståbenets knä lätt böjt (15°) och stolt hållning."),
        ("5. Enbens raka marklyft", "2–3 set x 5–10 reps/ben", 
         "Ta stöd i en stol vid behov. Stå som en staty mitt i foten, tyngden i hälen, skjut skinkan bakåt med rak rygg."),
        ("6. Modifierad Hip Airplane", "2–3 set x 5–10 reps/sida", 
         "Fäll fram, pressa bort golvet och öppna höften mot taket. Stanna direkt i vågrätt läge på vägen ner (vinglas på höften).")
    ]

    completed = 0
    for title, dose, cue in exercises:
        st.markdown(f"""
        <div class="exercise-card">
            <strong>{title}</strong> — <span>{dose}</span>
            <div class="cue-text">{cue}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.checkbox(f"Klar med {title.split('.')[0]}", key=title):
            completed += 1

    st.progress(completed / len(exercises))
    if completed == len(exercises):
        st.success("Snyggt jobbat! Gå till fliken '📝 Logga' för att spara passet.")

    st.divider()
    st.subheader("⏱️ Snabb-timer")
    col1, col2, col3 = st.columns(3)
    timer_placeholder = st.empty()

    def run_timer(seconds):
        for rem in range(seconds, 0, -1):
            timer_placeholder.metric("Tid kvar", f"{rem} sek")
            time.sleep(1)
        timer_placeholder.success("🎉 Tiden är ute!")

    if col1.button("20s (Vägg)"):
        run_timer(20)
    if col2.button("45s (Pendling)"):
        run_timer(45)
    if col3.button("60s (Stretch)"):
        run_timer(60)

# --- FLIK 2: LOGGA PASSET ---
with tab2:
    st.subheader("Logga dagens pass")
    with st.form("log_form"):
        datum = st.date_input("Datum", datetime.date.today())
        kontakt = st.slider("Muskelkontakt i höger säte (1 = Död, 10 = Helt vaken)", 1, 10, 5)
        smarta = st.slider("Smärta/ömhet i höft & knä (1 = Smärtfri, 10 = Hög smärta)", 1, 10, 4)
        stelhet = st.slider("Stelhet i ländrygg/ljumske (1 = Mjuk, 10 = Låst)", 1, 10, 4)
        naproxen = st.checkbox("Tagit Naproxen idag?")
        kommentar = st.text_input("Kort notering (t.ex. hur det kändes att ligga på sidan)")
        
        submitted = st.form_submit_button("Spara pass")
        if submitted:
            new_row = pd.DataFrame([{
                "Datum": str(datum),
                "Kontakt_Säte": kontakt,
                "Smärta_Höft_Knä": smarta,
                "Stelhet_Rygg_Ljumske": stelhet,
                "Naproxen": "Ja" if naproxen else "Nej",
                "Kommentar": kommentar
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("✅ Passet är loggat och sparat!")

# --- FLIK 3: UTVECKLING & HISTORIK ---
with tab3:
    st.subheader("4-veckorsmål (8 pass)")
    antal_pass = len(df)
    st.progress(min(antal_pass / 8, 1.0))
    st.write(f"Du har genomfört **{antal_pass} av 8** grundpass.")

    if not df.empty:
        st.subheader("Trend: Kontakt vs. Smärta")
        chart_df = df.set_index("Datum")[["Kontakt_Säte", "Smärta_Höft_Knä", "Stelhet_Rygg_Ljumske"]]
        st.line_chart(chart_df)

        st.subheader("Logghistorik")
        st.dataframe(df.iloc[::-1], use_container_width=True)
