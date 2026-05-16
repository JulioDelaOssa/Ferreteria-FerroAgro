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

document.querySelectorAll("[data-menu-toggle]").forEach(function (button) {
    const menuId = button.getAttribute("data-menu-toggle");
    const menu = document.getElementById(menuId);
    const container = button.closest(".landing-header, .sidebar");

    if (!menu || !container) {
        return;
    }

    button.addEventListener("click", function (event) {
        event.stopPropagation();

        const isOpen = container.classList.toggle("menu-open");
        button.setAttribute("aria-expanded", isOpen ? "true" : "false");

        const icon = button.querySelector("i");
        if (icon) {
            icon.className = isOpen ? "ri-close-line" : "ri-menu-line";
        }
    });

    menu.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", function () {
            container.classList.remove("menu-open");
            button.setAttribute("aria-expanded", "false");

            const icon = button.querySelector("i");
            if (icon) {
                icon.className = "ri-menu-line";
            }
        });
    });

    container.addEventListener("click", function (event) {
        event.stopPropagation();
    });
});

document.addEventListener("click", function () {
    document.querySelectorAll("[data-menu-toggle]").forEach(function (button) {
        const menuId = button.getAttribute("data-menu-toggle");
        const menu = document.getElementById(menuId);
        const container = button.closest(".landing-header, .sidebar");

        if (!menu || !container || !container.classList.contains("menu-open")) {
            return;
        }

        container.classList.remove("menu-open");
        button.setAttribute("aria-expanded", "false");

        const icon = button.querySelector("i");
        if (icon) {
            icon.className = "ri-menu-line";
        }
    });
});

document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") {
        return;
    }

    document.querySelectorAll("[data-menu-toggle]").forEach(function (button) {
        const menuId = button.getAttribute("data-menu-toggle");
        const menu = document.getElementById(menuId);
        const container = button.closest(".landing-header, .sidebar");

        if (!menu || !container) {
            return;
        }

        container.classList.remove("menu-open");
        button.setAttribute("aria-expanded", "false");

        const icon = button.querySelector("i");
        if (icon) {
            icon.className = "ri-menu-line";
        }
    });
});
