from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import io
import base64

# Menggunakan backend 'Agg' agar matplotlib tidak membuka window GUI (penting untuk web server)
matplotlib.use('Agg')

app = Flask(__name__)

# --- Load Data Sekali Saja saat Aplikasi Start ---
try:
    df = pd.read_csv('data_diabetes.csv')
    
    # Pre-processing dasar (seperti di soal sebelumnya)
    def kategori_dm(jumlah):
        if jumlah < 50000: return 'Rendah'
        elif jumlah < 100000: return 'Sedang'
        else: return 'Tinggi'
    
    df['kategori_dm'] = df['jumlah_penderita_dm'].apply(kategori_dm)
    
except FileNotFoundError:
    print("Error: File 'data_dm_jabar.csv' tidak ditemukan.")
    df = pd.DataFrame() # Dataframe kosong untuk mencegah error fatal

# --- Fungsi Helper untuk Membuat Plot menjadi Gambar URL ---
def create_plot_url(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig) # Tutup plot agar memori tidak penuh
    return 'data:image/png;base64,{}'.format(plot_url)

@app.route('/')
def dashboard():
    if df.empty:
        return "Data tidak ditemukan. Pastikan file csv ada."

    # --- 1. Analisis Ringkas (Cards) ---
    total_penderita_all = df['jumlah_penderita_dm'].sum()
    total_kabupaten = df['nama_kabupaten_kota'].nunique()
    tahun_tersedia = sorted(df['tahun'].unique())
    tahun_terbaru = tahun_tersedia[-1]
    
    # Data Tahun Terbaru (misal 2019)
    df_latest = df[df['tahun'] == tahun_terbaru].copy()
    total_penderita_latest = df_latest['jumlah_penderita_dm'].sum()

    # --- 2. Membuat Grafik (Visualisasi) ---
    
    # Grafik 1: Bar Chart Top 10 Kota (Tahun Terbaru)
    top_10 = df_latest.sort_values(by='jumlah_penderita_dm', ascending=True).tail(10)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.barh(top_10['nama_kabupaten_kota'], top_10['jumlah_penderita_dm'], color='teal')
    ax1.set_title(f'Top 10 Wilayah Penderita Tertinggi ({tahun_terbaru})')
    ax1.grid(axis='x', linestyle='--', alpha=0.7)
    plot_bar = create_plot_url(fig1)

    # Grafik 2: Line Chart Tren Tahunan
    total_per_tahun = df.groupby('tahun')['jumlah_penderita_dm'].sum().reset_index()
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(total_per_tahun['tahun'], total_per_tahun['jumlah_penderita_dm'], marker='o', color='darkred', linestyle='-')
    ax2.set_title('Tren Total Penderita per Tahun')
    ax2.set_xticks(total_per_tahun['tahun'])
    ax2.grid(True, linestyle='--')
    plot_line = create_plot_url(fig2)

    # Grafik 3: Pie Chart Proporsi Kategori
    proporsi = df_latest['kategori_dm'].value_counts()
    fig3, ax3 = plt.subplots(figsize=(6, 6))
    ax3.pie(proporsi, labels=proporsi.index, autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99'], startangle=90)
    ax3.set_title(f'Proporsi Kategori DM ({tahun_terbaru})')
    plot_pie = create_plot_url(fig3)

    # --- 3. Tabel Ringkasan (Data Table) ---
    # Kita kirim data tabel top 10 dalam format dictionary
    top_10_table = df_latest.sort_values(by='jumlah_penderita_dm', ascending=False).head(10)[['nama_kabupaten_kota', 'jumlah_penderita_dm', 'kategori_dm']].to_dict(orient='records')

    return render_template('dashboard.html', 
                           plot_bar=plot_bar, 
                           plot_line=plot_line, 
                           plot_pie=plot_pie,
                           total_all=f"{total_penderita_all:,}",
                           total_latest=f"{total_penderita_latest:,}",
                           tahun_latest=tahun_terbaru,
                           data_table=top_10_table)

if __name__ == '__main__':
    app.run(debug=True)