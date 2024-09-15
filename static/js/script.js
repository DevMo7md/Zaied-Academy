// script.js
document.addEventListener("DOMContentLoaded", function () {
    const savedTheme = localStorage.getItem("theme") || "light-theme";
    document.body.classList.add(savedTheme);

    document
        .getElementById("theme-toggle")
        .addEventListener("click", function () {
        document.body.classList.toggle("light-theme");
        document.body.classList.toggle("dark-theme");

        const currentTheme = document.body.classList.contains("dark-theme")
            ? "dark-theme"
            : "light-theme";
        localStorage.setItem("theme", currentTheme);
        });
});
