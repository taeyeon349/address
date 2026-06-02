document.addEventListener('DOMContentLoaded', () => loadContacts());

// 주소록 목록 및 검색 기능 호출
async function loadContacts() {
    const searchQuery = document.getElementById('searchInp').value;
    const url = `/api/contacts?search=${encodeURIComponent(searchQuery)}`;
    
    const response = await fetch(url);
    const contacts = await response.json();
    
    const tbody = document.getElementById('contactTableBody');
    tbody.innerHTML = ''; 

    if (contacts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:15px; color:#999;">검색 결과가 없습니다.</td></tr>';
        return;
    }

    contacts.forEach(c => {
        const row = `<tr>
            <td style="padding: 10px; border: 1px solid #ddd;">${c.name}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">${c.phone}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">${c.email || '-'}</td>
        </tr>`;
        tbody.insertAdjacentHTML('beforeend', row);
    });
}

function resetSearch() {
    document.getElementById('searchInp').value = '';
    loadContacts();
}

async function addContact() {
    const name = document.getElementById('name').value;
    const phone = document.getElementById('phone').value;
    const email = document.getElementById('email').value;

    if(!name || !phone) { return alert('이름과 전화번호를 입력하세요.'); }

    const response = await fetch('/api/contacts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone, email })
    });

    if (response.ok) {
        document.getElementById('name').value = '';
        document.getElementById('phone').value = '';
        document.getElementById('email').value = '';
        loadContacts();
    }
}

async function logout() {
    const response = await fetch('/api/logout', { method: 'POST' });
    if (response.ok) window.location.reload();
}
