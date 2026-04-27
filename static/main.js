function submitAuth(action) {
    const email = document.getElementById(action + '-email').value;
    const pass = document.getElementById(action + '-pass').value;
    
    if (!email || !pass) {
        alert('Please fill in all fields');
        return;
    }
    
    // Construct the URL with query parameters
    const url = new URL(window.location.href);
    url.searchParams.set('action', action);
    url.searchParams.set('email', email);
    url.searchParams.set('pass', pass);
    
    // Redirect the parent window
    window.location.href = url.href;
}
