import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from Bio.Seq import Seq
import random
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Genomik Evrim Laboratuvarı", layout="wide")
st.title("🧬 Evrimsel Kanser Antidotu Simülatörü")
st.markdown("Bu yazılım, kanseri durduran ve yan etkisi en az olan DNA dizisini evrimsel yöntemlerle arar.")

# --- SİMÜLASYON AYARLARI (Sidebar) ---
st.sidebar.header("Parametreler")
dna_length = st.sidebar.slider("DNA Dizilim Uzunluğu", 20, 100, 45)
pop_size = st.sidebar.slider("Popülasyon Büyüklüğü", 10, 100, 40)
mutation_rate = st.sidebar.slider("Mutasyon Oranı", 0.01, 0.20, 0.05)

# --- SİSTEM DEĞİŞKENLERİ ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'running' not in st.session_state:
    st.session_state.running = False

# --- TEMEL FONKSİYONLAR ---
def calculate_fitness(dna):
    # Kanser azaltma skoru (Kurgusal hedef motif: GGC ve AAA)
    score = (dna.count("GGC") * 8) + (dna.count("AAA") * 4)
    # Yan etki (Gereksiz C ve T artışı toksisite simülasyonu)
    toxicity = (dna.count("CCCC") * 10) + (dna.count("TTT") * 5)
    return max(0, score - toxicity), toxicity

def start_sim():
    st.session_state.running = True
    st.session_state.history = []

# --- ARAYÜZÜN OLUŞTURULMASI ---
col1, col2 = st.columns([1, 2])

with col1:
    if st.button("Simülasyonu Başlat", on_click=start_sim):
        st.write("Veriler işleniyor...")
    
    status_text = st.empty()
    dna_display = st.empty()

with col2:
    chart_placeholder = st.empty()

# --- SİMÜLASYON DÖNGÜSÜ ---
if st.session_state.running:
    # Başlangıç Popülasyonu
    population = ["".join(random.choice("ATGC") for _ in range(dna_length)) for _ in range(pop_size)]
    
    for gen in range(1, 201): # 200 Nesil çalışsın
        # Skorlama
        scored_pop = []
        for dna in population:
            fit, tox = calculate_fitness(dna)
            scored_pop.append((dna, fit, tox))
        
        scored_pop.sort(key=lambda x: x[1], reverse=True)
        best_dna, best_fit, best_tox = scored_pop[0]
        
        # Geçmişe kaydet (Grafik için)
        st.session_state.history.append({"Nesil": gen, "Başarı Skoru": best_fit, "Toksisite": best_tox})
        
        # Canlı Güncelleme
        status_text.metric("Güncel Nesil", gen, delta=f"Skor: {best_fit}")
        dna_display.info(f"**En İyi Aday DNA:** \n\n {best_dna}")
        
        # Grafik Çizimi
        df = pd.DataFrame(st.session_state.history)
        fig = px.line(df, x="Nesil", y=["Başarı Skoru", "Toksisite"], 
                      title="Evrimsel Gelişim Süreci",
                      color_discrete_map={"Başarı Skoru": "green", "Toksisite": "red"})
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Seçilim ve Yeni Nesil
        next_gen = [x[0] for x in scored_pop[:10]] # Elitler
        while len(next_gen) < pop_size:
            parent = random.choice(next_gen)
            mutated = list(parent)
            for i in range(len(mutated)):
                if random.random() < mutation_rate:
                    mutated[i] = random.choice("ATGC")
            next_gen.append("".join(mutated))
        
        population = next_gen
        time.sleep(0.1) # Görsel akış için küçük bir bekleme
