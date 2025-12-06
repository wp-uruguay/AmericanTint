/**
 * Funciones específicas para gestión de Garantías
 */

// Validar código de garantía
function validateWarrantyCode(code) {
    // Formato: AT-XXXXXXXX-NNN
    const pattern = /^AT-[A-Z0-9]{8}-\d{3}$/;
    return pattern.test(code);
}

// Buscar garantía en tiempo real
const warrantySearchInput = document.getElementById('warranty-search');
if (warrantySearchInput) {
    warrantySearchInput.addEventListener('input', debounce(function() {
        const code = this.value.trim().toUpperCase();
        
        if (code.length >= 5) {
            searchWarrantyByCode(code);
        }
    }, 500));
}

// Buscar garantía por código (AJAX)
function searchWarrantyByCode(code) {
    const resultsDiv = document.getElementById('search-results');
    
    if (!resultsDiv) return;
    
    // Mostrar loading
    resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
    
    // TODO: Implementar búsqueda AJAX
    fetch(`/warranty/search?code=${code}`)
        .then(response => response.json())
        .then(data => {
            if (data.warranty) {
                displayWarrantyResult(data.warranty);
            } else {
                resultsDiv.innerHTML = '<div class="alert alert-warning">Garantía no encontrada</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultsDiv.innerHTML = '<div class="alert alert-danger">Error en la búsqueda</div>';
        });
}

// Mostrar resultado de búsqueda
function displayWarrantyResult(warranty) {
    const resultsDiv = document.getElementById('search-results');
    
    const statusClass = {
        'active': 'success',
        'pending': 'warning',
        'expired': 'danger',
        'cancelled': 'secondary'
    }[warranty.status] || 'secondary';
    
    resultsDiv.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">
                    <span class="warranty-code">${warranty.code}</span>
                    <span class="badge bg-${statusClass} float-end">${warranty.status}</span>
                </h5>
                <hr>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Cliente:</strong> ${warranty.customer_name || 'No asignado'}</p>
                        <p><strong>Vehículo:</strong> ${warranty.vehicle_info || 'N/A'}</p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Activación:</strong> ${warranty.activation_date || 'Pendiente'}</p>
                        <p><strong>Vencimiento:</strong> ${warranty.expiration_date || 'N/A'}</p>
                    </div>
                </div>
                <a href="/warranty/${warranty.id}" class="btn btn-primary btn-sm mt-2">
                    <i class="fas fa-eye me-1"></i>Ver Detalles
                </a>
            </div>
        </div>
    `;
}

// Calcular días restantes
function calculateDaysRemaining(expirationDate) {
    const today = new Date();
    const expiration = new Date(expirationDate);
    const diffTime = expiration - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return Math.max(0, diffDays);
}

// Activar garantía (AJAX)
function activateWarranty(warrantyCode, customerData, vehicleInfo) {
    const formData = {
        warranty_code: warrantyCode,
        customer: customerData,
        vehicle_info: vehicleInfo
    };
    
    fetch('/warranty/activate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Garantía activada exitosamente', 'success');
            setTimeout(() => {
                window.location.href = `/warranty/${data.warranty_id}`;
            }, 1500);
        } else {
            showToast(data.message || 'Error al activar garantía', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al activar garantía', 'danger');
    });
}

// Copiar código de garantía
function copyWarrantyCode(code) {
    copyToClipboard(code);
    showToast(`Código ${code} copiado`, 'success');
}

// Inicializar eventos de garantías
document.addEventListener('DOMContentLoaded', function() {
    // Botones de copiar código
    const copyButtons = document.querySelectorAll('.copy-warranty-code');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const code = this.getAttribute('data-code');
            copyWarrantyCode(code);
        });
    });

    // Validación en tiempo real del código
    const codeInput = document.getElementById('warranty-code-input');
    if (codeInput) {
        codeInput.addEventListener('input', function() {
            const code = this.value.toUpperCase();
            this.value = code;
            
            if (validateWarrantyCode(code)) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else if (code.length > 0) {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    }
});

// Filtrar garantías por estado
function filterWarrantiesByStatus(status) {
    const rows = document.querySelectorAll('.warranty-table tbody tr');
    
    rows.forEach(function(row) {
        const rowStatus = row.getAttribute('data-status');
        
        if (status === 'all' || rowStatus === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Mostrar alerta de garantías próximas a vencer
function checkExpiringWarranties() {
    // TODO: Implementar verificación de garantías próximas a vencer
    fetch('/warranty/expiring?days=30')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                showToast(`${data.count} garantía(s) vencen en los próximos 30 días`, 'warning');
            }
        })
        .catch(error => console.error('Error:', error));
}
