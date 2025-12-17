// === Tambahan baru: fungsi bantu format angka ===
function formatNumber(input) {
    // Simpan posisi kursor agar tidak lompat
    const start = input.selectionStart;

    // Hapus semua karakter selain angka
    let value = input.value.replace(/\D/g, '');
    if (value === '') {
        input.value = '';
        updateTotals();
        return;
    }

    // Format angka ke format ribuan Indonesia (tanpa desimal)
    input.value = parseInt(value, 10).toLocaleString('id-ID');

    // Kembalikan posisi kursor ke akhir
    input.setSelectionRange(input.value.length, input.value.length);

    // Perbarui total debit dan kredit
    updateTotals();
}

function parseNumber(value) {
    // Ubah "1.000.000" → 1000000 (integer)
    return parseInt((value || '0').replace(/\./g, ''), 10) || 0;
}


// === Fungsi kamu yang tetap ===
function addEntry() {
    const row = document.querySelector('.entry').cloneNode(true);

    // Reset semua input
    row.querySelectorAll('input').forEach(input => {
        if (input.name.includes('debit') || input.name.includes('credit')) {
            input.value = '';
        } else {
            input.value = '';
        }
    });

    // Tambahkan event listener
    const debitInput = row.querySelector('input[name="debit[]"]');
    const creditInput = row.querySelector('input[name="credit[]"]');

    debitInput.addEventListener('input', () => formatNumber(debitInput));
    creditInput.addEventListener('input', () => formatNumber(creditInput));

    // Tombol hapus
    const removeButton = row.querySelector('button');
    removeButton.onclick = function () {
        removeEntry(this);
    };

    document.getElementById('entries').appendChild(row);
    updateTotals();
}

function removeEntry(button) {
    const row = button.closest('tr');
    const rows = document.querySelectorAll('#entries .entry');

    if (rows.length > 1) {
        row.remove();
        updateTotals();
    } else {
        alert('Minimal satu baris jurnal diperlukan.');
    }
}

function updateTotals() {
    const debits = document.querySelectorAll('input[name="debit[]"]');
    const credits = document.querySelectorAll('input[name="credit[]"]');

    let totalDebit = 0, totalCredit = 0;

    debits.forEach(input => {
        totalDebit += parseNumber(input.value);
    });
    credits.forEach(input => {
        totalCredit += parseNumber(input.value);
    });

    document.getElementById('total-debit').innerText = totalDebit.toLocaleString('id-ID');
    document.getElementById('total-credit').innerText = totalCredit.toLocaleString('id-ID');
    
    // Optional: tampilkan peringatan real-time jika tidak balance
    const warning = document.getElementById('balance-warning');
    if (totalDebit !== totalCredit) {
        warning.style.display = 'block';
    } else {
        warning.style.display = 'none';
    }
}

function validateJournal() {
    const totalDebit = parseNumber(document.getElementById('total-debit').innerText);
    const totalCredit = parseNumber(document.getElementById('total-credit').innerText);

    if (totalDebit !== totalCredit) {
        alert('Total debit dan kredit harus seimbang!');
        return false;
    }

    // Hapus titik sebelum submit (agar backend terima angka polos)
    document.querySelectorAll('input[name="debit[]"], input[name="credit[]"]').forEach(input => {
        input.value = parseNumber(input.value);
    });

    return true;
}

// Inisialisasi listener awal
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[name="debit[]"]').forEach(input => {
        input.addEventListener('input', () => formatNumber(input));
    });
    document.querySelectorAll('input[name="credit[]"]').forEach(input => {
        input.addEventListener('input', () => formatNumber(input));
    });
    updateTotals();
});
