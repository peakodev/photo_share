
const formRef = document.querySelector('form');


async function login(e) {
    // const formData = new FormData(document.querySelector('form'));
    print(e);
    const response = await fetch('/api/auth/signin', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    if (response.ok) {
        print(data);
        localStorage.setItem('access_token', data.access_token);
        window.location.href = '/protected';
    } else {
        print("!!!! error auth", data.detail)
        alert('Login failed: ' + data.detail);
    }
}


form.addEventListener('submit', (e) => {
    e.preventDefault();
    login(e.data);
})