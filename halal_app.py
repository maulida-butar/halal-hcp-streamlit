from datetime import date
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# Prototype Streamlit
# Model Identifikasi Halal Critical Point Berbasis Python
# Alat bantu pra-sertifikasi halal pada proses produksi UMKM pangan
# ============================================================

st.set_page_config(
    page_title="HCP Halal Risk Scoring",
    page_icon="✅",
    layout="wide",
)


# ------------------------------------------------------------
# Styling sederhana
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #555;
        margin-bottom: 1rem;
    }
    .risk-low {
        background-color: #E8F5E9;
        color: #1B5E20;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }
    .risk-medium {
        background-color: #FFF8E1;
        color: #E65100;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }
    .risk-high {
        background-color: #FFEBEE;
        color: #B71C1C;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }
    .risk-critical {
        background-color: #4A0000;
        color: white;
        padding: 0.25rem 0.55rem;
        border-radius: 999px;
        font-weight: 700;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# Konstanta model
# ------------------------------------------------------------
RISK_COLUMNS: List[str] = [
    "Risiko Bahan",
    "Risiko Kontaminasi",
    "Risiko Alat",
    "Risiko Dokumen",
    "Risiko Sanitasi",
]

RISK_SHORT_LABELS: Dict[str, str] = {
    "Risiko Bahan": "Bahan",
    "Risiko Kontaminasi": "Kontaminasi",
    "Risiko Alat": "Alat",
    "Risiko Dokumen": "Dokumen",
    "Risiko Sanitasi": "Sanitasi",
}

DEFAULT_WEIGHTS: Dict[str, float] = {
    "Risiko Bahan": 0.35,
    "Risiko Kontaminasi": 0.25,
    "Risiko Alat": 0.20,
    "Risiko Dokumen": 0.10,
    "Risiko Sanitasi": 0.10,
}

DEFAULT_VETO_THRESHOLD = 85


# ------------------------------------------------------------
# Data default untuk simulasi
# ------------------------------------------------------------
def get_default_process_data() -> pd.DataFrame:
    """Membuat contoh data tahapan proses produksi UMKM pangan."""
    return pd.DataFrame(
        [
            {
                "Tahap Produksi": "Penerimaan bahan baku",
                "Risiko Bahan": 95,
                "Risiko Kontaminasi": 70,
                "Risiko Alat": 30,
                "Risiko Dokumen": 90,
                "Risiko Sanitasi": 40,
                "Catatan Risiko": "Sebagian bahan belum memiliki sertifikat halal dan dokumen pemasok belum lengkap.",
            },
            {
                "Tahap Produksi": "Penyimpanan bahan baku",
                "Risiko Bahan": 60,
                "Risiko Kontaminasi": 80,
                "Risiko Alat": 40,
                "Risiko Dokumen": 50,
                "Risiko Sanitasi": 55,
                "Catatan Risiko": "Ada potensi tercampur antara bahan berbeda karena area penyimpanan belum dipisah.",
            },
            {
                "Tahap Produksi": "Persiapan dan pencampuran",
                "Risiko Bahan": 70,
                "Risiko Kontaminasi": 65,
                "Risiko Alat": 75,
                "Risiko Dokumen": 40,
                "Risiko Sanitasi": 60,
                "Catatan Risiko": "Alat pencampur digunakan bersama dan prosedur pembersihan belum terdokumentasi.",
            },
            {
                "Tahap Produksi": "Pengolahan atau pemasakan",
                "Risiko Bahan": 45,
                "Risiko Kontaminasi": 35,
                "Risiko Alat": 40,
                "Risiko Dokumen": 30,
                "Risiko Sanitasi": 35,
                "Catatan Risiko": "Risiko relatif terkendali, tetapi SOP sanitasi perlu diperjelas.",
            },
            {
                "Tahap Produksi": "Pengemasan",
                "Risiko Bahan": 60,
                "Risiko Kontaminasi": 55,
                "Risiko Alat": 45,
                "Risiko Dokumen": 70,
                "Risiko Sanitasi": 45,
                "Catatan Risiko": "Bahan kemasan kontak langsung belum tervalidasi dokumen pendukungnya.",
            },
            {
                "Tahap Produksi": "Penyimpanan produk jadi",
                "Risiko Bahan": 25,
                "Risiko Kontaminasi": 30,
                "Risiko Alat": 20,
                "Risiko Dokumen": 35,
                "Risiko Sanitasi": 30,
                "Catatan Risiko": "Risiko rendah, namun pelabelan dan pemisahan produk tetap perlu dipantau.",
            },
            {
                "Tahap Produksi": "Distribusi atau penjualan",
                "Risiko Bahan": 20,
                "Risiko Kontaminasi": 25,
                "Risiko Alat": 15,
                "Risiko Dokumen": 25,
                "Risiko Sanitasi": 20,
                "Catatan Risiko": "Risiko rendah selama produk dikemas baik dan tidak bercampur dengan produk lain.",
            },
        ]
    )


# ------------------------------------------------------------
# Fungsi model
# ------------------------------------------------------------
def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Menormalkan bobot agar totalnya menjadi 1."""
    total = sum(weights.values())
    if total == 0:
        return DEFAULT_WEIGHTS.copy()
    return {key: value / total for key, value in weights.items()}


def classify_risk(score: float) -> str:
    """Mengklasifikasikan skor risiko menjadi empat kategori."""
    if score <= 25:
        return "Low Risk"
    if score <= 50:
        return "Medium Risk"
    if score <= 75:
        return "High Risk"
    return "Critical Point"


def get_recommendation(status: str, dominant_risk: str, veto_factors: str = "") -> str:
    """Memberikan rekomendasi awal berdasarkan kategori risiko, faktor dominan, dan logika veto."""
    factor = dominant_risk.lower()

    if status == "Low Risk":
        return (
            "Risiko rendah. Proses dapat dipertahankan, tetapi pemantauan rutin dalam kerangka "
            "Sistem Jaminan Produk Halal tetap diperlukan."
        )

    if status == "Medium Risk":
        return (
            f"Perlu verifikasi tambahan pada aspek {factor}. Lengkapi bukti pendukung, periksa SOP, "
            "dan pastikan proses terdokumentasi sebagai bagian dari pemantauan dan evaluasi SJPH."
        )

    if status == "High Risk":
        return (
            f"Wajib menyusun tindakan koreksi (corrective action) sebelum pengajuan sertifikasi. "
            f"Fokus utama pada aspek {factor}, termasuk pengendalian proses, pemisahan area/alat, "
            "kelengkapan dokumen, dan pelibatan penyelia halal internal."
        )

    if veto_factors:
        return (
            f"Critical Point terdeteksi karena indikator veto: {veto_factors}. "
            "Wajib menyusun tindakan koreksi (corrective action), menghentikan penggunaan bahan/proses berisiko "
            "hingga tervalidasi, melibatkan penyelia halal internal, melengkapi dokumen pendukung, dan melakukan evaluasi ulang."
        )

    return (
        f"Titik kritis wajib dikendalikan. Aspek dominan adalah {factor}. "
        "Wajib menyusun tindakan koreksi (corrective action), memvalidasi bahan/proses, melengkapi dokumen, "
        "melibatkan penyelia halal internal, dan melakukan pemeriksaan ulang sebelum pengajuan sertifikasi."
    )


def calculate_hcp(
    df: pd.DataFrame,
    weights: Dict[str, float],
    veto_threshold: int = DEFAULT_VETO_THRESHOLD,
) -> pd.DataFrame:
    """Menghitung skor risiko HCP dan membuat kolom hasil analisis."""
    result = df.copy()

    for col in RISK_COLUMNS:
        if col not in result.columns:
            result[col] = 0
        result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0).clip(0, 100)

    if "Tahap Produksi" not in result.columns:
        result["Tahap Produksi"] = "Tahap belum diberi nama"

    if "Catatan Risiko" not in result.columns:
        result["Catatan Risiko"] = ""

    risk_score = 0
    for col, weight in weights.items():
        risk_score += result[col] * weight

    result["Skor Risiko"] = risk_score.round(2)

    # Logika veto/override:
    # Jika satu indikator bernilai sangat kritis, status otomatis Critical Point,
    # meskipun skor rata-rata berbobotnya tidak terlalu tinggi.
    def get_veto_factors(row: pd.Series) -> str:
        factors = [RISK_SHORT_LABELS[col] for col in RISK_COLUMNS if row[col] > veto_threshold]
        return ", ".join(factors)

    def apply_veto_classification(row: pd.Series) -> str:
        if row["Faktor Veto"]:
            return "Critical Point"
        return classify_risk(row["Skor Risiko"])

    result["Faktor Veto"] = result.apply(get_veto_factors, axis=1)
    result["Status"] = result.apply(apply_veto_classification, axis=1)
    result["Faktor Risiko Dominan"] = result[RISK_COLUMNS].idxmax(axis=1).map(RISK_SHORT_LABELS)
    result["Rekomendasi Awal"] = result.apply(
        lambda row: get_recommendation(row["Status"], row["Faktor Risiko Dominan"], row["Faktor Veto"]),
        axis=1,
    )

    result = result.sort_values("Skor Risiko", ascending=False).reset_index(drop=True)
    result.insert(0, "Prioritas", range(1, len(result) + 1))
    return result


def status_badge(status: str) -> str:
    """Mengubah status menjadi badge HTML berwarna."""
    class_map = {
        "Low Risk": "risk-low",
        "Medium Risk": "risk-medium",
        "High Risk": "risk-high",
        "Critical Point": "risk-critical",
    }
    return f'<span class="{class_map.get(status, "risk-low")}">{status}</span>'


def make_html_table(df: pd.DataFrame) -> str:
    """Membuat tabel HTML ringkas dengan badge status."""
    cols = [
        "Prioritas",
        "Tahap Produksi",
        "Faktor Risiko Dominan",
        "Faktor Veto",
        "Skor Risiko",
        "Status",
        "Rekomendasi Awal",
    ]
    table_df = df[cols].copy()
    table_df["Status"] = table_df["Status"].apply(status_badge)
    table_df["Faktor Veto"] = table_df["Faktor Veto"].replace("", "-")

    html = "<table style='width:100%; border-collapse: collapse;'>"
    html += "<thead><tr>"
    for col in cols:
        html += (
            "<th style='text-align:left; padding:10px; border-bottom:2px solid #DDE4EA; "
            "background:#F7F9FB;'>" + col + "</th>"
        )
    html += "</tr></thead><tbody>"

    for _, row in table_df.iterrows():
        html += "<tr>"
        for col in cols:
            value = row[col]
            html += f"<td style='vertical-align:top; padding:10px; border-bottom:1px solid #EEF2F5;'>{value}</td>"
        html += "</tr>"

    html += "</tbody></table>"
    return html


def make_markdown_report(
    company_name: str,
    product_name: str,
    assessment_date: date,
    df_result: pd.DataFrame,
    weights: Dict[str, float],
    veto_threshold: int = DEFAULT_VETO_THRESHOLD,
) -> str:
    """Membuat laporan markdown sederhana untuk diunduh."""
    total_process = len(df_result)
    critical_count = int((df_result["Status"] == "Critical Point").sum())
    high_count = int((df_result["Status"] == "High Risk").sum())
    avg_score = df_result["Skor Risiko"].mean() if total_process else 0

    lines = []
    lines.append("# Laporan Identifikasi Halal Critical Point Berbasis Python")
    lines.append("")
    lines.append(f"**Nama Usaha:** {company_name or '-'}")
    lines.append(f"**Nama Produk:** {product_name or '-'}")
    lines.append(f"**Tanggal Penilaian:** {assessment_date}")
    lines.append("")
    lines.append("## Ringkasan")
    lines.append(f"- Jumlah tahap proses: {total_process}")
    lines.append(f"- Jumlah Critical Point: {critical_count}")
    lines.append(f"- Jumlah High Risk: {high_count}")
    lines.append(f"- Rata-rata skor risiko: {avg_score:.2f}")
    lines.append(f"- Ambang veto indikator tunggal: > {veto_threshold}")
    lines.append("")
    lines.append("## Bobot Penilaian")
    for col, w in weights.items():
        lines.append(f"- {RISK_SHORT_LABELS[col]}: {w:.2f}")
    lines.append("")
    lines.append("## Hasil Prioritas HCP")

    for _, row in df_result.iterrows():
        veto_note = row["Faktor Veto"] if row["Faktor Veto"] else "Tidak ada"
        lines.append(f"### Prioritas {row['Prioritas']} - {row['Tahap Produksi']}")
        lines.append(f"- Skor risiko: {row['Skor Risiko']}")
        lines.append(f"- Status: {row['Status']}")
        lines.append(f"- Faktor dominan: {row['Faktor Risiko Dominan']}")
        lines.append(f"- Faktor veto: {veto_note}")
        lines.append(f"- Catatan: {row.get('Catatan Risiko', '-')}")
        lines.append(f"- Rekomendasi awal: {row['Rekomendasi Awal']}")
        lines.append("")

    lines.append("## Catatan Penting")
    lines.append(
        "Prototype ini hanya merupakan alat bantu pra-sertifikasi untuk memetakan risiko proses. "
        "Hasil aplikasi ini tidak menentukan status halal produk dan tidak menggantikan kewenangan BPJPH, LPH, auditor halal, atau fatwa halal yang berlaku."
    )

    return "\n".join(lines)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Mengubah dataframe menjadi file CSV bytes."""
    return df.to_csv(index=False).encode("utf-8-sig")


def safe_read_csv(uploaded_file) -> pd.DataFrame:
    """Membaca CSV yang diunggah pengguna."""
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="latin-1")


def highlight_critical_factory(veto_threshold: int):
    """Membuat fungsi styling untuk menandai skor indikator yang melewati ambang veto."""
    def highlight_critical(val):
        if isinstance(val, (int, float)) and val > veto_threshold:
            return "color: white; background-color: #B71C1C; font-weight: bold"
        return ""

    return highlight_critical


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown(
    '<div class="main-title">Model Identifikasi <i>Halal Critical Point</i> Berbasis Python</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">Alat bantu pra-sertifikasi halal untuk memetakan risiko proses produksi UMKM pangan.</div>',
    unsafe_allow_html=True,
)

st.warning(
    "Aplikasi ini adalah prototype akademik untuk pemetaan risiko awal. "
    "Aplikasi ini bukan alat penentu status halal dan bukan pengganti proses sertifikasi resmi BPJPH/LPH."
)


# ------------------------------------------------------------
# Sidebar: metadata, bobot, dan logika veto
# ------------------------------------------------------------
with st.sidebar:
    st.header("Identitas Penilaian")
    company_name = st.text_input("Nama usaha/UMKM", value="UMKM Contoh")
    product_name = st.text_input("Nama produk", value="Produk Pangan Contoh")
    assessment_date = st.date_input("Tanggal penilaian", value=date.today())

    st.divider()
    st.header("Bobot Risiko")
    st.caption("Bobot otomatis dinormalkan agar total = 1.")

    weight_bahan = st.slider("Bahan", 0.0, 1.0, DEFAULT_WEIGHTS["Risiko Bahan"], 0.05)
    weight_kontaminasi = st.slider("Kontaminasi silang", 0.0, 1.0, DEFAULT_WEIGHTS["Risiko Kontaminasi"], 0.05)
    weight_alat = st.slider("Alat produksi", 0.0, 1.0, DEFAULT_WEIGHTS["Risiko Alat"], 0.05)
    weight_dokumen = st.slider("Dokumen", 0.0, 1.0, DEFAULT_WEIGHTS["Risiko Dokumen"], 0.05)
    weight_sanitasi = st.slider("Sanitasi", 0.0, 1.0, DEFAULT_WEIGHTS["Risiko Sanitasi"], 0.05)

    raw_weights = {
        "Risiko Bahan": weight_bahan,
        "Risiko Kontaminasi": weight_kontaminasi,
        "Risiko Alat": weight_alat,
        "Risiko Dokumen": weight_dokumen,
        "Risiko Sanitasi": weight_sanitasi,
    }
    weights = normalize_weights(raw_weights)

    st.caption("Bobot aktif setelah normalisasi:")
    st.json({RISK_SHORT_LABELS[k]: round(v, 3) for k, v in weights.items()})

    st.divider()
    st.header("Logika Veto")
    veto_threshold = st.slider(
        "Ambang Batas Kritis (Veto)",
        min_value=50,
        max_value=100,
        value=DEFAULT_VETO_THRESHOLD,
        step=5,
        help="Jika ada indikator tunggal melewati nilai ini, tahap akan otomatis dikategorikan Critical Point.",
    )
    st.caption(f"Status otomatis menjadi Critical Point jika skor indikator > {veto_threshold}.")


# ------------------------------------------------------------
# Tabs utama
# ------------------------------------------------------------
tab_input, tab_result, tab_method = st.tabs(
    ["1. Input Proses", "2. Hasil Identifikasi HCP", "3. Metode dan Formula"]
)


# ------------------------------------------------------------
# Tab Input
# ------------------------------------------------------------
with tab_input:
    st.subheader("Input Tahapan Proses Produksi")
    st.write(
        "Isi skor 0–100 untuk setiap indikator risiko. "
        "Skor 0 berarti risiko sangat rendah/terkendali, sedangkan skor 100 berarti risiko sangat tinggi."
    )

    col_upload, col_template = st.columns([1.2, 1])
    with col_upload:
        uploaded_file = st.file_uploader(
            "Unggah CSV data proses produksi, atau gunakan data contoh di bawah",
            type=["csv"],
        )
    with col_template:
        template_df = get_default_process_data()
        st.download_button(
            label="Unduh template CSV",
            data=to_csv_bytes(template_df),
            file_name="template_hcp_process.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if uploaded_file is not None:
        input_df = safe_read_csv(uploaded_file)
        required_cols = ["Tahap Produksi", *RISK_COLUMNS]
        missing_cols = [col for col in required_cols if col not in input_df.columns]
        if missing_cols:
            st.error(
                f"File CSV tidak valid. Kolom wajib berikut tidak ditemukan: {', '.join(missing_cols)}. "
                "Harap gunakan template CSV yang disediakan agar hasil penilaian tidak menyesatkan."
            )
            input_df = get_default_process_data()
        else:
            if "Catatan Risiko" not in input_df.columns:
                input_df["Catatan Risiko"] = ""
            st.success("File CSV berhasil dibaca dan tervalidasi.")
    else:
        input_df = get_default_process_data()

    edited_df = st.data_editor(
        input_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tahap Produksi": st.column_config.TextColumn(
                "Tahap Produksi",
                help="Nama tahap dalam proses produksi.",
                required=True,
            ),
            "Risiko Bahan": st.column_config.NumberColumn(
                "Risiko Bahan",
                help="Status sertifikat halal bahan, bahan tambahan, dan bahan penolong.",
                min_value=0,
                max_value=100,
                step=1,
            ),
            "Risiko Kontaminasi": st.column_config.NumberColumn(
                "Risiko Kontaminasi",
                help="Potensi kontaminasi silang dengan bahan/produk non-halal atau najis.",
                min_value=0,
                max_value=100,
                step=1,
            ),
            "Risiko Alat": st.column_config.NumberColumn(
                "Risiko Alat",
                help="Risiko dari penggunaan alat bersama, riwayat penggunaan alat, atau pembersihan alat.",
                min_value=0,
                max_value=100,
                step=1,
            ),
            "Risiko Dokumen": st.column_config.NumberColumn(
                "Risiko Dokumen",
                help="Kelengkapan dokumen pemasok, spesifikasi bahan, sertifikat, dan catatan proses.",
                min_value=0,
                max_value=100,
                step=1,
            ),
            "Risiko Sanitasi": st.column_config.NumberColumn(
                "Risiko Sanitasi",
                help="Kebersihan fasilitas, SOP pembersihan, dan pengendalian lingkungan produksi.",
                min_value=0,
                max_value=100,
                step=1,
            ),
            "Catatan Risiko": st.column_config.TextColumn(
                "Catatan Risiko",
                help="Catatan masalah atau temuan pada tahap proses tersebut.",
            ),
        },
        key="process_editor",
    )

    st.session_state["edited_df"] = edited_df
    st.session_state["weights"] = weights
    st.session_state["veto_threshold"] = veto_threshold

    st.info(
        "Setelah mengisi atau mengedit data, buka tab 'Hasil Identifikasi HCP' untuk melihat skor, status risiko, dan rekomendasi awal."
    )


# ------------------------------------------------------------
# Tab Hasil
# ------------------------------------------------------------
with tab_result:
    st.subheader("Hasil Identifikasi Halal Critical Point")

    current_df = st.session_state.get("edited_df", get_default_process_data())
    current_weights = st.session_state.get("weights", weights)
    current_veto_threshold = st.session_state.get("veto_threshold", veto_threshold)
    result_df = calculate_hcp(current_df, current_weights, current_veto_threshold)

    total_process = len(result_df)
    critical_count = int((result_df["Status"] == "Critical Point").sum())
    high_count = int((result_df["Status"] == "High Risk").sum())
    medium_count = int((result_df["Status"] == "Medium Risk").sum())
    avg_score = float(result_df["Skor Risiko"].mean()) if total_process else 0.0
    max_score = float(result_df["Skor Risiko"].max()) if total_process else 0.0

    metric_cols = st.columns(5)
    metric_cols[0].metric("Jumlah Tahap", total_process)
    metric_cols[1].metric("Critical Point", critical_count)
    metric_cols[2].metric("High Risk", high_count)
    metric_cols[3].metric("Rata-rata Skor", f"{avg_score:.2f}")
    metric_cols[4].metric("Skor Tertinggi", f"{max_score:.2f}")

    if total_process == 0:
        st.warning("Belum ada data proses produksi yang dapat dianalisis.")
        st.stop()

    st.divider()

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.markdown("### Tabel Prioritas Risiko")
        st.markdown(make_html_table(result_df), unsafe_allow_html=True)

    with right_col:
        st.markdown("### Distribusi Status Risiko")
        status_counts = (
            result_df["Status"]
            .value_counts()
            .reindex(["Critical Point", "High Risk", "Medium Risk", "Low Risk"])
            .fillna(0)
            .astype(int)
        )
        st.bar_chart(status_counts)

        st.markdown("### Skor Risiko per Tahap")
        chart_df = result_df[["Tahap Produksi", "Skor Risiko"]].set_index("Tahap Produksi")
        st.bar_chart(chart_df)

        st.markdown("### Profil Risiko per Tahap Produksi")
        selected_tahap = st.selectbox(
            "Pilih tahap produksi untuk melihat profil risiko:",
            result_df["Tahap Produksi"].tolist(),
        )
        row_data = result_df[result_df["Tahap Produksi"] == selected_tahap].iloc[0]
        radar_data = pd.DataFrame(
            {
                "Indikator": [RISK_SHORT_LABELS[col] for col in RISK_COLUMNS],
                "Skor": [row_data[col] for col in RISK_COLUMNS],
            }
        )

        fig = go.Figure()
        skor_values = radar_data["Skor"].tolist()
        indikator_values = radar_data["Indikator"].tolist()

        fig.add_trace(
            go.Scatterpolar(
                r=skor_values + [skor_values[0]],
                theta=indikator_values + [indikator_values[0]],
                fill="toself",
                fillcolor="rgba(220, 38, 38, 0.30)",
                line_color="rgb(220, 38, 38)",
                name="Skor Proses",
            )
        )

        veto_line = [current_veto_threshold] * len(radar_data)
        fig.add_trace(
            go.Scatterpolar(
                r=veto_line + [veto_line[0]],
                theta=indikator_values + [indikator_values[0]],
                mode="lines",
                line=dict(color="black", dash="dash"),
                name="Batas Veto / Kritis",
            )
        )

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title=f"Radar Risiko: {selected_tahap}",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.markdown("### Data Lengkap Hasil Perhitungan")
    display_cols = [
        "Prioritas",
        "Tahap Produksi",
        "Risiko Bahan",
        "Risiko Kontaminasi",
        "Risiko Alat",
        "Risiko Dokumen",
        "Risiko Sanitasi",
        "Skor Risiko",
        "Status",
        "Faktor Risiko Dominan",
        "Faktor Veto",
        "Catatan Risiko",
        "Rekomendasi Awal",
    ]

    styled_df = result_df[display_cols].style.map(
        highlight_critical_factory(current_veto_threshold),
        subset=RISK_COLUMNS,
    )
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    report_md = make_markdown_report(
        company_name=company_name,
        product_name=product_name,
        assessment_date=assessment_date,
        df_result=result_df,
        weights=current_weights,
        veto_threshold=current_veto_threshold,
    )

    download_col1, download_col2 = st.columns(2)
    with download_col1:
        st.download_button(
            label="Unduh hasil CSV",
            data=to_csv_bytes(result_df[display_cols]),
            file_name="hasil_identifikasi_hcp.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with download_col2:
        st.download_button(
            label="Unduh laporan Markdown",
            data=report_md.encode("utf-8"),
            file_name="laporan_identifikasi_hcp.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("### Interpretasi Singkat")
    veto_count = int((result_df["Faktor Veto"] != "").sum())
    if veto_count > 0:
        st.error(
            f"Terdapat {veto_count} tahap yang menjadi Critical Point karena logika veto. "
            "Indikator tunggal yang sangat kritis wajib dikendalikan dan tidak boleh dikompensasi oleh indikator lain yang rendah."
        )
    elif critical_count > 0:
        st.error(
            f"Terdapat {critical_count} tahap proses dengan status Critical Point. "
            "Tahap ini perlu menjadi prioritas pengendalian sebelum pengajuan sertifikasi halal."
        )
    elif high_count > 0:
        st.warning(
            f"Tidak ada Critical Point, tetapi terdapat {high_count} tahap dengan status High Risk. "
            "Tahap ini perlu tindakan koreksi dan verifikasi tambahan."
        )
    elif medium_count > 0:
        st.info(
            f"Sebagian besar risiko terkendali, namun terdapat {medium_count} tahap Medium Risk yang perlu diverifikasi."
        )
    else:
        st.success("Seluruh tahap berada pada kategori Low Risk berdasarkan input dan bobot saat ini.")


# ------------------------------------------------------------
# Tab Metode
# ------------------------------------------------------------
with tab_method:
    st.subheader("Metode Penilaian")

    st.markdown(
        """
        Prototype ini menggunakan pendekatan **rule-based scoring model** yang dilengkapi dengan **logika veto/override**.
        Setiap tahap proses produksi diberi skor risiko 0–100 pada lima indikator utama:

        1. **Risiko Bahan**: status sertifikat halal bahan baku, bahan tambahan, dan bahan penolong.
        2. **Risiko Kontaminasi**: potensi tercampur dengan bahan/produk non-halal atau najis.
        3. **Risiko Alat**: penggunaan alat bersama, riwayat penggunaan alat, dan validasi pembersihan.
        4. **Risiko Dokumen**: kelengkapan dokumen pemasok, spesifikasi bahan, dan catatan proses.
        5. **Risiko Sanitasi**: kebersihan fasilitas, SOP pembersihan, dan pengendalian lingkungan produksi.
        """
    )

    st.markdown("### Formula Skor Risiko")
    st.latex(
        r"Risk\ Score = (w_B \times B) + (w_K \times K) + (w_A \times A) + (w_D \times D) + (w_S \times S)"
    )

    st.markdown(
        """
        Keterangan:
        - **B** = risiko bahan
        - **K** = risiko kontaminasi silang
        - **A** = risiko alat produksi
        - **D** = risiko dokumen
        - **S** = risiko sanitasi
        - **w** = bobot masing-masing indikator
        """
    )

    st.markdown("### Logika Veto/Override")
    st.markdown(
        f"""
        Selain skor rata-rata berbobot, prototype menerapkan logika **veto**. Jika salah satu indikator memiliki skor lebih dari **{veto_threshold}**,
        maka status tahap produksi otomatis menjadi **Critical Point**. Logika ini digunakan karena dalam prinsip jaminan halal,
        risiko yang sangat kritis pada satu aspek, misalnya bahan yang terindikasi bermasalah, tidak boleh dikompensasi oleh indikator lain yang rendah.
        """
    )

    st.markdown("### Klasifikasi Risiko")
    classification_df = pd.DataFrame(
        [
            {"Rentang Skor": "0–25", "Kategori": "Low Risk", "Interpretasi": "Risiko rendah, tetap dipantau."},
            {"Rentang Skor": ">25–50", "Kategori": "Medium Risk", "Interpretasi": "Perlu verifikasi dokumen atau prosedur."},
            {"Rentang Skor": ">50–75", "Kategori": "High Risk", "Interpretasi": "Wajib menyusun tindakan koreksi sebelum sertifikasi."},
            {"Rentang Skor": f">75–100 atau indikator > {veto_threshold}", "Kategori": "Critical Point", "Interpretasi": "Wajib dikendalikan karena dapat mengganggu kesiapan sertifikasi halal."},
        ]
    )
    st.dataframe(classification_df, use_container_width=True, hide_index=True)

    st.markdown("### Batasan Prototype")
    st.markdown(
        """
        - Bobot risiko dan ambang veto interaktif masih bersifat konseptual dan dapat disesuaikan melalui validasi pakar.
        - Prototype belum menentukan status halal produk.
        - Prototype tidak menggantikan proses audit halal, verifikasi LPH, keputusan BPJPH, atau fatwa halal.
        - Hasil penilaian bergantung pada kualitas input pengguna.
        - Untuk penelitian lanjutan, model dapat divalidasi menggunakan data UMKM nyata atau penilaian pakar halal.
        """
    )

    st.markdown("### Contoh Sitasi Metode dalam Paper")
    st.markdown(
        """
        Model dikembangkan sebagai alat bantu pra-sertifikasi dengan pendekatan *rule-based scoring* yang dilengkapi logika veto.
        Tahapan proses produksi dipetakan ke dalam indikator risiko bahan, kontaminasi, alat, dokumen, dan sanitasi.
        Skor risiko dihitung menggunakan formula berbobot, kemudian dikoreksi dengan aturan veto apabila terdapat indikator tunggal yang sangat kritis.
        Hasil akhir diklasifikasikan ke dalam empat kategori, yaitu *Low Risk*, *Medium Risk*, *High Risk*, dan *Critical Point*.
        Pendekatan ini dimaksudkan sebagai *decision support tool* untuk membantu pelaku usaha mengidentifikasi prioritas pengendalian sebelum pengajuan sertifikasi halal.
        """
    )
