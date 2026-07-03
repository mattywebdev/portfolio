(function () {
    function getCookie(name) {
        const cookies = document.cookie ? document.cookie.split(";") : [];

        for (const cookie of cookies) {
            const trimmedCookie = cookie.trim();

            if (trimmedCookie.startsWith(`${name}=`)) {
                return decodeURIComponent(trimmedCookie.substring(name.length + 1));
            }
        }

        return "";
    }

    function flashUpdatedRow(row) {
        const originalBackground = row.style.backgroundColor;

        row.style.transition = "background-color 180ms ease";
        row.style.backgroundColor = "#ecfdf5";

        window.setTimeout(() => {
            row.style.backgroundColor = originalBackground;
        }, 700);
    }

    function bindQuickStatusButtons() {
        document.querySelectorAll(".field-status_actions a").forEach((link) => {
            if (link.dataset.quickStatusBound === "true") {
                return;
            }

            link.dataset.quickStatusBound = "true";

            link.addEventListener("click", async (event) => {
                event.preventDefault();

                const row = link.closest("tr");
                const statusCell = row.querySelector(".field-status_badge");
                const actionsCell = row.querySelector(".field-status_actions");

                link.style.opacity = "0.55";
                link.style.pointerEvents = "none";

                try {
                    const response = await fetch(link.href, {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCookie("csrftoken"),
                            "X-Requested-With": "XMLHttpRequest",
                        },
                    });

                    if (!response.ok) {
                        window.location.href = link.href;
                        return;
                    }

                    const data = await response.json();
                    statusCell.innerHTML = data.status_badge_html;
                    actionsCell.innerHTML = data.status_actions_html;
                    flashUpdatedRow(row);
                    bindQuickStatusButtons();
                } catch (error) {
                    window.location.href = link.href;
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", bindQuickStatusButtons);
})();
