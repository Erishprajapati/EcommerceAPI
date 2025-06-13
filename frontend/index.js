function getData() {
    fetch('/api/hello')
        .then(response => response.json())
        .then(data => {
            document.getElementById("response").innerText = data.message;
        });
}
function registerUser() {
    const userData = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    fetch('/create_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        document.getElementById("response").innerText = `User created: ${data.name}`;
    })
    .catch(error => {
        document.getElementById("response").innerText = `Error: ${error.detail || "Unknown error"}`;
    });
}

