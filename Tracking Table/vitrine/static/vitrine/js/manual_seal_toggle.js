function setupManualSealToggle(root)
{
    const scope = root || document;
    const manualSealCheckbox = scope.querySelector("#id_vitrine_manual_seal");
    const manualSealTable = scope.querySelector("#manual-seal-table-wrapper");
    const autoModeRadio = scope.querySelector("#manual-seal-auto-mode");
    const customModeRadio = scope.querySelector("#manual-seal-custom-mode");

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
}

document.addEventListener("DOMContentLoaded", function () {
    setupManualSealToggle(document);
});
