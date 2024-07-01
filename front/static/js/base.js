async function loadProtectedPage(page) {
    // e.preventDefault();
    // print(e, page);

    const token = localStorage.getItem('access_token');

    console.log("token: ", token)
    // console.log("Start loadProtectedPage...")
    if (token) {
        try {
            const headers = new Headers();
            headers.append('Authorization', `Bearer ${token}`);

            // console.log("!!!headers: ", headers)
            // const headersLog = {};
            // headers.forEach((value, key) => {
            //     headersLog[key] = value;
            // });
            // console.log("new headers=", headersLog);


            const response = await fetch(`${page}`, {
                headers: headers
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
        // console.error('Token not found in local storage');
        window.location.href = page;
        // window.history.pushState({}, '', page);
    }
}

const logoutSite = async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user_id');
    window.location.href = '/';
}