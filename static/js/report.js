/**
 * static/js/report.js
 * Filtro de busca em tempo real na tabela de resultados.
 * totalRows e injetado pelo template via data attribute.
 */
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const table       = document.getElementById('data-table');
    const countLabel  = document.getElementById('count-label');
    const totalRows   = parseInt(document.getElementById('data-table')?.dataset.total ?? '0', 10);

    if (!searchInput || !table) return;

    searchInput.addEventListener('input', () => {
        const q    = searchInput.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        let visible = 0;

        rows.forEach(tr => {
            const match = tr.textContent.toLowerCase().includes(q);
            tr.classList.toggle('hidden-row', !match);
            if (match) visible++;
        });

        if (countLabel) {
            countLabel.textContent = q
                ? `${visible} de ${totalRows} registros`
                : `${totalRows} registros`;
        }
    });
});
