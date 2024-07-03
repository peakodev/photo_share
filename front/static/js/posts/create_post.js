const formNewPostRef = document.querySelector('form')
// const formMessagesRef = document.getElementById('messages');
const formMessagesRef = document.querySelector('.messages-text')

console.log('formMessagesRef: ', formMessagesRef)
console.log('formNewPostRef: ', formNewPostRef)

async function formCreatePostHandler(event) {
    event.preventDefault()
    // console.log('!!!!!! ')
    // console.log(event)
    // console.log(`api_create_url: ${api_create_url}`)

    const token = localStorage.getItem('access_token')

    if (token) {
        const headers = new Headers()
        headers.append('Authorization', `Bearer ${token}`)

        const formData = new FormData(event.target)
        for (let [name, value] of formData.entries()) {
            console.log(`${name}: ${value}`)
        }
        try {
            const res = await fetch(api_create_url, {
                method: 'POST',
                body: formData,
                headers: headers
            })
            const response_json = await res.json()
            if (res.ok) {
                console.log('OK')
                console.log('redirect_url_create_post: ', redirect_url_create_post)
                red_url = redirect_url_create_post + 'posts/' + response_json.id
                console.log('red_url=', red_url)
                window.location.href = red_url
            } else {
                console.log('Error')
                console.log(res)
                formMessagesRef.textContent = res.status + ': ' + res.statusText
            }
        } catch (error) {
            console.log(error)
        }
    }
}

// formNewPostRef.addEventListener('submit', formCreatePostHandler)