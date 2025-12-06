/**
 * Funciones específicas para gestión de Stock
 */

// Validar código de rollo
function validateStockCode(code) {
    const pattern = /^AT-[A-Z0-9]{8}$/;
    return pattern.test(code);
}

// Calcular disponibilidad
function calculateAvailability(total, used) {
    const available = total - used;
    const percentage = (available / total) * 100;
    
    let status = 'available';
    let color = 'success';
    
    if (available === 0) {
        status = 'depleted';
        color = 'danger';
    } else if (available < total) {
        status = 'partial';
        color = 'warning';
    }
    
    return {
        available: available,
        percentage: percentage.toFixed(2),
        status: status,
        color: color
    };
}

// Actualizar barra de progreso de stock
function updateStockProgress(stockId, total, used) {
    const result = calculateAvailability(total, used);
    const progressBar = document.querySelector(`#stock-${stockId} .progress-bar`);
    
    if (progressBar) {
        progressBar.style.width = `${result.percentage}%`;
        progressBar.classList.remove('bg-success', 'bg-warning', 'bg-danger');
        progressBar.classList.add(`bg-${result.color}`);
        progressBar.textContent = `${result.available}/${total}`;
    }
}

// Generar vista previa de importación
function previewStockImport(quantity) {
    const totalCodes = quantity * 15;
    const preview = document.getElementById('import-preview');
    
    if (preview) {
        preview.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Se crearán:
                <ul class="mb-0 mt-2">
                    <li><strong>${quantity}</strong> rollo(s) padre</li>
                    <li><strong>${totalCodes}</strong> códigos de garantía (15 por rollo)</li>
                </ul>
            </div>
        `;
    }
}

// Inicializar eventos de stock
document.addEventListener('DOMContentLoaded', function() {
    // Preview de importación
    const quantityInput = document.querySelector('input[name="quantity"]');
    if (quantityInput) {
        quantityInput.addEventListener('input', debounce(function() {
            const quantity = parseInt(this.value) || 0;
            if (quantity > 0) {
                previewStockImport(quantity);
            }
        }, 300));
    }

    // Filtros de tabla de stock
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filterStockTable(this.value);
        });
    }
});

// Filtrar tabla de stock por estado
function filterStockTable(status) {
    const rows = document.querySelectorAll('.stock-table tbody tr');
    
    rows.forEach(function(row) {
        const rowStatus = row.getAttribute('data-status');
        
        if (status === 'all' || rowStatus === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Exportar stock a CSV
function exportStockToCSV() {
    // TODO: Implementar exportación
    showToast('Exportando stock...', 'info');
}
