function login(){
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault(); // Prevent default form submission

      const formData = new FormData(loginForm); // Collect form data
      const data = new URLSearchParams(formData); // Convert to x-www-form-urlencoded

      try {
        const response = await fetch('http://your-api-domain/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded', // Important for OAuth2PasswordRequestForm
          },
          body: data,
        });

        if (response.ok) {
          const result = await response.json();
          console.log('Login Successful:', result);
        } else {
          const error = await response.json();
          console.error('Login Failed:', error);
        }
      } catch (err) {
        console.error('Error:', err);
      }
    });
}
