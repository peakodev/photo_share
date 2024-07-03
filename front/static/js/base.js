function getBaseNetloc() {
    const currentUrl = window.location.href;
    const url = new URL(currentUrl);
    const netloc = url.host;
    // console.log('global get netloc: ', netloc)
    return netloc
}



function getBaseHeaders() {
    const baseNetloc = getBaseNetloc()

    const headers = new Headers();
    const token = localStorage.getItem('access_token');
    console.log('global get token: ', token)
    headers.append('Host', baseNetloc)
    // headers.append('Host', baseNetloc)
    headers.append('Authorization', `Bearer ${token}`)
    return headers
}

async function loadProtectedPage(page) {
    // e.preventDefault();
    // print(e, page);

    const token = localStorage.getItem('access_token');



    console.log("token: ", token)
    // console.log("Start loadProtectedPage...")
    if (token) {
        const baseNetloc = getBaseNetloc()
        try {
            const headers = new Headers();
            headers.append('Authorization', `Bearer ${token}`);
            headers.append('Host', baseNetloc)
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



document.addEventListener('DOMContentLoaded', () => {
    const testAuthNav = document.querySelector('.auth-nav');
    const navLogoutRef = document.querySelector('.nav-logout');
    const navSigninRef = document.querySelector('.nav-signin');
    const navSignupRef = document.querySelector('.nav-signup');
    const navMyPostRef = document.querySelector('.nav-my-post');
    const navAddPostRef = document.querySelector('.nav-add-post');

    testAuthNav.classList.remove("d-none");

    let is_user_login = false
    const iser_id = localStorage.getItem('user_id')
    // console.log("iser_id: ", iser_id)

    if (iser_id) {
        is_user_login = true
    }
    // console.log("is_user_login: ", is_user_login)
    if (is_user_login) {
        navLogoutRef.classList.remove("d-none");
        navSigninRef.classList.add("d-none");
        navSignupRef.classList.add("d-none");
        navMyPostRef.classList.remove("d-none");
        navAddPostRef.classList.remove("d-none");
    } else {
        navLogoutRef.classList.add("d-none");
        navSigninRef.classList.remove("d-none");
        navSignupRef.classList.remove("d-none");
        navMyPostRef.classList.add("d-none");
        navAddPostRef.classList.add("d-none");
    }

    console.log("navLogoutRef: ", navLogoutRef)
    // const authLogoutRef = document.querySelector('#auth-logout'); 

    console.log("testAuthNav: ", testAuthNav)
})