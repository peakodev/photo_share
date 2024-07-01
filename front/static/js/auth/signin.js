
// const formRef = document.querySelector('form');

const markFormOnSubmit = () => {
    document.querySelector('form').onsubmit = async e => {
        e.preventDefault();

        const getUserFromServer = async () => {
            const token = localStorage.getItem('access_token');
            // console.log("read new token=", token)
            if (token) {
                try {
                    const newHeaders = new Headers();
                    newHeaders.append('Authorization', `Bearer ${token}`);

                    // console.log("___start fetch____")
                    const res = await fetch('/api/users/', {
                        method: 'GET',
                        headers: newHeaders
                    });
                    // console.log("___finish fetch____")
                    const res_json = await res.json();
                    // console.log("res_json=", res_json)
                    // console.log("new res=", res)
                    if (res.ok) {
                        localStorage.setItem('user_id', res_json.id);
                        localStorage.setItem('user', JSON.stringify(res_json));
                    } else {
                        console.error('!!!Error:', res.status, res.statusText);
                    }
                    return res_json

                } catch (error) {
                    console.log("_error fetch: ")
                    console.log('Error:', error);
                }
                return None
            }
        }

        console.log("markFormOnSubmite: ", e)
        const formData = new FormData(e.target);
        console.log("formData=", formData)

        // Заменить на имя роута */
        await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        }).then(async response => {
            if (response.status_code != 200) {
                // console.log("OK")
                data = await response.json();
                console.log(data)
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                localStorage.setItem('token_type', data.token_type);

                user = await getUserFromServer();

                window.location.href = redirect_url;
            };
        }).catch(async (error) => {
            console.log(error)
            return
            // Завершился ошибкой
        })
    };

}

markFormOnSubmit();

// Создание экземпляра MutationObserver и передача callback-функции
const observer = new MutationObserver(markFormOnSubmit);

// Выбор элемента для наблюдения
const targetNode = document.getElementById('form-login');

// Конфигурация observer для наблюдения за изменениями в элементе
const config = { childList: true, subtree: true, attributes: true };

// Начало наблюдения за выбранным элементом
observer.observe(targetNode, config);



