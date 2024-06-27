async function loadProtectedPage(page) {
    // e.preventDefault();
    // print(e, page);
    const token = localStorage.getItem('access_token');
    // console.log("Start loadProtectedPage...")
    if (token) {
        try {
            const response = await fetch(`${page}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const html = await response.text();
                document.open();
                document.write(html);
                document.close();
                window.history.pushState({}, '', page);
            } else {
                console.error('!!!Error:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    } else {
        console.error('Token not found in local storage');
        window.location.href = page;
        // window.history.pushState({}, '', page);
    }
}

const logoutSite = async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_type');
    window.location.href = '/';
}