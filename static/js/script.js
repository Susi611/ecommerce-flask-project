console.log("E-Commerce Loaded");

// Simple toast notification
function showMessage(msg){
    alert(msg);
}

// Smooth scroll for buttons (optional UX improvement)
document.addEventListener("DOMContentLoaded", function(){
    const links = document.querySelectorAll("a");

    links.forEach(link => {
        link.addEventListener("click", function(){
            console.log("Navigating...");
        });
    });
});