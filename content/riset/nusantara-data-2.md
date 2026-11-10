---
title: Nusantara Data 2.0
subtitle: Data Warehouse dan Dashboard untuk Pemantauan Kesenjangan Digital di Indonesia
year: 2026
status: Selesai
funder: Strategic Research Grant (SRG) Tipe D 2026, DRPM ITS
summary: Data warehouse, katalog metadata DCAT, dan dashboard terbuka untuk seluruh 90 dataset telekomunikasi BPS di 38 provinsi.
hero: assets/nusantara-map.jpg
format: html
order: 2
---

<p class="lead-p">Data akses digital di Indonesia tersebar, tidak terstandar, dan kadang saling bertentangan. Proyek ini membangun portal data
terbuka dan terintegrasi untuk mendukung studi, pemantauan, dan perumusan kebijakan kesetaraan digital (SDG 10).</p>

<section>
  <h2>Hasil proyek</h2>
  <div class="grid cols-3">
    <a class="card proj-out" href="../../explorer/"><h3>Data Explorer</h3><p class="small muted">90 dataset BPS dengan peta provinsi, peringkat, dan tren.</p></a>
    <a class="card proj-out" href="../../analysis/"><h3>Analisis</h3><p class="small muted">Ringkasan nasional, perbandingan provinsi, dan profil 38 provinsi.</p></a>
    <a class="card proj-out" href="../../katalog/"><h3>Katalog data</h3><p class="small muted">Metadata DCAT, unduhan CSV, glosarium, dan data warehouse.</p></a>
  </div>
</section>

  <section>
    <h2>Pertanyaan penelitian</h2>
    <ol>
      <li>Bagaimana menyusun metadata data akses digital BPS berdasarkan kaidah Data Catalog Vocabulary (DCAT)?</li>
      <li>Apa kebutuhan dan fitur portal data terbuka yang ramah pengguna untuk analisis kesenjangan digital?</li>
      <li>Bagaimana dashboard dirancang agar mendukung visualisasi, unduhan, dan interaksi dengan data, sambil menjaga asal-usul (provenance) dan keandalan data?</li>
    </ol>
  </section>

  <section>
    <h2>Arsitektur sistem</h2>
    <div class="flow">
      <div><strong>1. Sumber</strong>PDF BPS <em>Statistik Telekomunikasi Indonesia 2024</em>: 72 lampiran, 6 tabel, 21 gambar</div>
      <div><strong>2. Ekstraksi</strong>pdfplumber, penyaringan watermark, rekonstruksi tabel dari posisi kata</div>
      <div><strong>3. Standardisasi</strong>kode wilayah BPS, label kolom terverifikasi, koreksi format, glosarium</div>
      <div><strong>4. Metadata</strong>inventaris DCAT 90 dataset (CSV + JSON-LD)</div>
      <div><strong>5. Warehouse</strong>skema bintang SQLite, ETL + 8 uji kualitas, 13.788 fakta</div>
      <div><strong>6. Penyajian</strong>Data Explorer, Analisis, Katalog, unduhan terbuka</div>
    </div>
    <p class="small muted">Seluruh skrip dapat dijalankan ulang untuk edisi publikasi berikutnya; setiap angka dapat ditelusuri ke halaman sumbernya.</p>
  </section>

  <section id="kualitas">
    <h2>Temuan kualitas data</h2>
    <p class="muted" style="max-width:780px">Membangun warehouse sekaligus menjadi audit terhadap data sumber. Temuan ini memperkuat argumen penelitian:
      data publik perlu metadata dan pemeriksaan konsistensi sebelum dipakai untuk kebijakan.</p>
    <ol class="findings">
      <li><strong>Inkonsistensi di dalam satu publikasi.</strong> Jumlah ISP tahun 2021 tercatat 611 (Gambar 18) dan 828 (Tabel 6).
        Kepemilikan telepon seluler perdesaan 2021 tercatat 57,42% (Gambar 5) dan 57,24% (Lampiran 6). Dari 35 pasangan angka yang dicek silang, 33 cocok.</li>
      <li><strong>Format angka tidak seragam.</strong> Sebagian sel di Lampiran 18 dan 36 memakai titik desimal, bukan koma; tanpa penanganan khusus,
        96,94 terbaca sebagai 9.694. 262 nilai dikoreksi.</li>
      <li><strong>Struktur tabel bermasalah.</strong> Indeks kolom tercetak ganda (Lampiran 43–45), label baris keliru (Lampiran 71), judul tidak sesuai isi
        (Lampiran 72 berisi jumlah pelanggan, bukan penyelenggara), dan nama provinsi tertukar (kode 53 tercetak “Nusa Tenggara Barat”).</li>
      <li><strong>Watermark sebagai teks.</strong> Tanda air PDF ikut terbaca sebagai karakter dan merusak angka bila diekstrak biasa.</li>
      <li><strong>Pemekaran wilayah.</strong> Empat provinsi baru di Papua (2022) hanya memiliki data 2023–2024, sehingga deret waktu perlu harmonisasi.</li>
    </ol>
  </section>
