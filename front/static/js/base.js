async function loadProtectedPage(page) {
    const token = localStorage.getItem('access_token');
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
            } else {
                console.error('Error:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    } else {
        console.error('Token not found');
    }
}