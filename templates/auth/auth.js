async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const result = await response.json();
    if (response.ok && result.success) {
        window.location.href = '/'; 
    } else {
        alert(result.message || '로그인에 실패했습니다.');
    }
}
