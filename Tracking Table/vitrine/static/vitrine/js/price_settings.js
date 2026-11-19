/**
 * Keep the settings page viewport behavior aligned with other account/admin forms.
 */
const MIN_VIEWPORT_WIDTH = 600;
const viewport_width = window.innerWidth;
set_viewport_scale(viewport_width, MIN_VIEWPORT_WIDTH);

function normalizeDecimal(value) {
    const cleaned = String(value ?? "")
        .trim()
        .replace(",", ".");
    if (cleaned === "") {
        return "";
    }
    const numeric = Number(cleaned);
    return Number.isFinite(numeric) ? numeric.toFixed(2) : cleaned;
}

function setupPriceSettingsForm() {
    const form = document.getElementById("vitrine-price-settings-form");
    if (!form) {
        return;
    }

    const inputs = Array.from(form.querySelectorAll(".vitrine-price-settings-fields .form-control"));
    const submitBtn = document.getElementById("vitrine-price-settings-submit");
    const btnLabel = submitBtn?.querySelector(".btn-label");
    const spinner = submitBtn?.querySelector(".spinner-border");
    const successIcon = submitBtn?.querySelector(".btn-icon-success");
    const errorIcon = submitBtn?.querySelector(".btn-icon-error");
    const toastEl = document.getElementById("vitrine-price-settings-toast");
    const toastBody = document.getElementById("vitrine-price-settings-toast-body");
    let activeToast = null;

    const updateDirtyState = () => {
        inputs.forEach((input) => {
            const current = normalizeDecimal(input.value);
            const initial = input.dataset.initialValue || "";
            const row = input.closest(".vitrine-price-settings-row");
            const changed = current !== initial;

            if (row) {
                row.classList.toggle("is-dirty", changed);
            }
        });
    };

    const showToast = (message, type) => {
        if (!toastEl || !toastBody) {
            return;
        }
        if (activeToast) {
            activeToast.hide();
        }

        const delay = type === "success" ? 2000 : 10000;
        toastEl.classList.remove("bg-success", "bg-danger");
        toastEl.classList.add(type === "success" ? "bg-success" : "bg-danger");
        toastBody.textContent = message;
        activeToast = new bootstrap.Toast(toastEl, { delay, autohide: true });
        activeToast.show();
    };

    const setButtonState = (state) => {
        if (!submitBtn || !btnLabel || !spinner || !successIcon || !errorIcon) {
            return;
        }

        submitBtn.classList.remove("btn-primary", "btn-success", "btn-danger");
        if (state === "success") {
            submitBtn.classList.add("btn-success");
        } else if (state === "error") {
            submitBtn.classList.add("btn-danger");
        } else {
            submitBtn.classList.add("btn-primary");
        }

        submitBtn.disabled = state !== "idle";
        spinner.classList.toggle("d-none", state !== "loading");
        successIcon.classList.toggle("d-none", state !== "success");
        errorIcon.classList.toggle("d-none", state !== "error");
        btnLabel.classList.toggle("d-none", state !== "idle");
    };

    const markCurrentAsSaved = () => {
        inputs.forEach((input) => {
            input.dataset.initialValue = normalizeDecimal(input.value);
        });
        updateDirtyState();
    };

    const extractErrorMessage = async (response) => {
        try {
            const payload = await response.json();
            return payload?.message || "Възникна грешка при запазване.";
        } catch {
            return "Възникна грешка при запазване.";
        }
    };

    inputs.forEach((input) => {
        input.dataset.initialValue = normalizeDecimal(input.value);
        input.addEventListener("input", updateDirtyState);
        input.addEventListener("change", updateDirtyState);
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setButtonState("loading");

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });

            if (response.ok) {
                const payload = await response.json();
                setButtonState("success");
                markCurrentAsSaved();
                showToast(payload?.message || "Промените са запазени успешно.", "success");
            } else {
                const message = await extractErrorMessage(response);
                setButtonState("error");
                showToast(message, "error");
            }
        } catch {
            setButtonState("error");
            showToast("Няма връзка със сървъра. Опитайте отново.", "error");
        }

        setTimeout(() => {
            setButtonState("idle");
        }, 2000);
    });
}

setupPriceSettingsForm();
