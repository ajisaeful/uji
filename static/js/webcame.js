// Dapatkan elemen video dan tombol start webcam
const videoElement = document.getElementById('webcam-video');
const startWebcamButton = document.getElementById('start-webcam-btn');

// Fungsi untuk memulai webcam
function startWebcam() {
    // Izinkan akses ke webcam pengguna
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            // Tampilkan video dari webcam pada elemen video
            videoElement.srcObject = stream;
        })
        .catch((error) => {
            console.error('Gagal mengakses webcam: ', error);
        });
}

// Fungsi untuk menghentikan webcam
function stopWebcam() {
    // Dapatkan objek media stream dari video
    const stream = videoElement.srcObject;
    // Dapatkan semua track dari media stream
    const tracks = stream.getTracks();

    // Hentikan setiap track
    tracks.forEach((track) => {
        track.stop();
    });

    // Set objek media stream pada video ke null
    videoElement.srcObject = null;
}

// Tambahkan event listener untuk menangani tombol q
document.addEventListener('keydown', (event) => {
    // Jika tombol yang ditekan adalah huruf q (kode 81)
    if (event.keyCode === 81) {
        // Hentikan webcam
        stopWebcam();
    }
});
