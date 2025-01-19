document.addEventListener("DOMContentLoaded", () => {
    const registerSection = document.getElementById("register-section");
    const loginSection = document.getElementById("login-section");
    const fileSection = document.getElementById("file-section");
    const userInfoSection = document.getElementById("user-info");  
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");

    const toRegisterButton = document.getElementById("to-register");
    const toLoginButton = document.getElementById("to-login");

    const logoutButton = document.getElementById("logout-btn");  
    const loggedInUsername = document.getElementById("logged-in-username"); 
    toRegisterButton.addEventListener("click", () => {
        loginSection.style.display = "none";
        registerSection.style.display = "block";
    });

    toLoginButton.addEventListener("click", () => {
        registerSection.style.display = "none";
        loginSection.style.display = "block";
    });

    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("reg-username").value;
        const password = document.getElementById("reg-password").value;
        const email = document.getElementById("reg-email").value;
        const firstName = document.getElementById("reg-first-name").value;
        const lastName = document.getElementById("reg-last-name").value;

        try {
            const response = await fetch("/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ 
                    username, 
                    password, 
                    email, 
                    first_name: firstName,   
                    last_name: lastName     
                }),
            });

            if (response.ok) {
                alert("Registration successful! Please log in.");
                toLoginButton.click();
            } else {
                const errorData = await response.json();
                alert(`Registration failed: ${errorData.message}`);
            }
        } catch (error) {
            console.error("Error during registration:", error);
            alert("An error occurred. Please try again later.");
        }
    });

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem("token", data.access_token);
                
                const token = data.access_token;
                const userPayload = JSON.parse(atob(token.split('.')[1]));
                const userName = userPayload.preferred_username;

                loggedInUsername.textContent = userName;
                loginSection.style.display = "none";
                userInfoSection.style.display = "block";
                fileSection.style.display = "block";
            } else {
                const errorData = await response.json();
            }
        } catch (error) {
        }
    });

    logoutButton.addEventListener("click", () => {
        localStorage.removeItem("token");
        userInfoSection.style.display = "none";
        loginSection.style.display = "block";
    });
});
