function switchInputType(type) {
    const textInput = document.getElementById('inputText');
    const newsUrlInput = document.getElementById('newsUrlInput');
    const youtubeUrlInput = document.getElementById('youtubeUrlInput');
    const buttons = document.querySelectorAll('.type-button');
    
    // Hide all inputs
    textInput.style.display = 'none';
    newsUrlInput.style.display = 'none';
    youtubeUrlInput.style.display = 'none';
    
    // Remove active class from all buttons
    buttons.forEach(button => button.classList.remove('active'));
    
    // Show selected input and activate corresponding button
    switch(type) {
        case 'newsUrl':
            newsUrlInput.style.display = 'block';
            buttons[1].classList.add('active');
            break;
        case 'youtubeUrl':
            youtubeUrlInput.style.display = 'block';
            buttons[2].classList.add('active');
            break;
        default: // text
            textInput.style.display = 'block';
            buttons[0].classList.add('active');
    }
}

function validateUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}
