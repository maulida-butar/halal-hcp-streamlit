# halal-hcp-streamlit
Python/Streamlit-based Decision Support System for Halal Critical Point (HCP) identification in MSME food production.

## 📊 Metodologi dan Formula

Skor risiko total awal pada tiap tahapan dihitung menggunakan metode rata-rata berbobot konvensional:

$$
\text{Risk Score} = (w_B \times B) + (w_K \times K) + (w_A \times A) + (w_D \times D) + (w_S \times S)
$$

Di mana $w$ merupakan bobot kepentingan relatif masing-masing indikator. Logika model kemudian mengaplikasikan fungsi pembatas (constraint):

$$
\text{Status} = \begin{cases} 
\text{Critical Point}, & \text{jika } \exists X \in \{B, K, A, D, S\} > T_v \\ 
\text{Classify}(X), & \text{jika } \forall X \le T_v 
\end{cases}
$$

Di mana $T_v$ merupakan *Veto Threshold* (ambang batas kritis dinamis) yang diatur interaktif oleh pakar/pendamping halal.

## Sitasi Akademik
Jika Anda menggunakan prototype atau memodifikasi kode dalam repositori ini untuk keperluan riset ilmiah, mohon cantumkan sitasi berikut:

Butar Butar, M., Irvansyah, D. A., Armando, J., Syehan, S., & Putri, N. T. (2026). Model Identifikasi Halal Critical Point Berbasis Python sebagai Alat Bantu Pra-Sertifikasi Halal pada Proses Produksi UMKM Pangan. Makalah disajikan dalam Konferensi Halal Universitas Airlangga: Harmonisasi Lintas Sektor dan Kesiapan Industri Nasional, Surabaya, Indonesia.

## Lisensi
Proyek ini dilisensikan di bawah MIT License - lihat file LICENSE untuk detailnya. Penggunaan kode untuk riset, pengabdian masyarakat, dan edukasi sangat didukung.

Disclaimer: Aplikasi ini merupakan prototype akademik untuk pemetaan risiko awal (pre-assessment tool) dan tidak menggantikan otoritas fatwa atau keputusan resmi sertifikasi halal oleh BPJPH.
