const notificationButton = document.getElementById("notificationButton");
const notificationMenu = document.getElementById("notificationMenu");

if (notificationButton && notificationMenu) {
    notificationButton.addEventListener("click", function (event) {
        event.stopPropagation();
        notificationMenu.classList.toggle("show");
    });

    document.addEventListener("click", function () {
        notificationMenu.classList.remove("show");
    });

    notificationMenu.addEventListener("click", function (event) {
        event.stopPropagation();
    });
}