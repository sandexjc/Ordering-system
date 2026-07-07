(function () {
    const manualSealCheckbox = document.getElementById("id_vitrine_manual_seal");
    const manualSealTable = document.getElementById("manual-seal-table-wrapper");
    const autoModeRadio = document.getElementById("manual-seal-auto-mode");
    const customModeRadio = document.getElementById("manual-seal-custom-mode");

    if (!manualSealCheckbox || !manualSealTable || !autoModeRadio || !customModeRadio) {
        return;
    }

    function toggleManualSealTable() {
        manualSealTable.classList.toggle("is-open", manualSealCheckbox.checked);
    }

    function syncRadiosWithCheckbox() {
        if (manualSealCheckbox.checked) {
            customModeRadio.checked = true;
        } else {
            autoModeRadio.checked = true;
        }
    }

    function setManualSealMode(isManual) {
        manualSealCheckbox.checked = isManual;
        syncRadiosWithCheckbox();
        toggleManualSealTable();
    }

    autoModeRadio.addEventListener("change", function () {
        if (autoModeRadio.checked) {
            setManualSealMode(false);
        }
    });

    customModeRadio.addEventListener("change", function () {
        if (customModeRadio.checked) {
            setManualSealMode(true);
        }
    });

    manualSealCheckbox.addEventListener("change", toggleManualSealTable);
    syncRadiosWithCheckbox();
    toggleManualSealTable();
})();
