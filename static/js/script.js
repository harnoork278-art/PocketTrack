/**
 * PocketTrack – Student Expense & Budget Manager
 * Vanilla JavaScript for Dashboard Charts, Modals, Dynamic Filters, and Interactivity
 */

document.addEventListener('DOMContentLoaded', function () {
    // -------------------------------------------------------------
    // 1. Mobile Sidebar Toggle
    // -------------------------------------------------------------
    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.getElementById('appSidebar');

    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });

        // Close sidebar if user clicks outside of it on mobile
        document.addEventListener('click', function (event) {
            if (
                window.innerWidth <= 992 &&
                sidebar.classList.contains('open') &&
                !sidebar.contains(event.target) &&
                !mobileToggle.contains(event.target)
            ) {
                sidebar.classList.remove('open');
            }
        });
    }

    // -------------------------------------------------------------
    // 2. Auto-dismiss Flash Alerts
    // -------------------------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        // Close button click
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 250);
            });
        }

        // Automatic dismiss after 5 seconds
        setTimeout(function () {
            if (document.body.contains(alert)) {
                alert.style.transition = 'opacity 0.4s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 400);
            }
        }, 5000);
    });

    // -------------------------------------------------------------
    // 3. Budget Modal Handling
    // -------------------------------------------------------------
    const budgetModal = document.getElementById('budgetModal');
    const openBudgetButtons = document.querySelectorAll('[data-open-modal="budgetModal"]');
    const closeBudgetButtons = document.querySelectorAll('[data-close-modal="budgetModal"]');

    function openModal() {
        if (budgetModal) {
            budgetModal.classList.add('show');
            const amountInput = budgetModal.querySelector('input[name="amount"]');
            if (amountInput) amountInput.focus();
        }
    }

    function closeModal() {
        if (budgetModal) {
            budgetModal.classList.remove('show');
        }
    }

    openBudgetButtons.forEach(btn => btn.addEventListener('click', openModal));
    closeBudgetButtons.forEach(btn => btn.addEventListener('click', closeModal));

    if (budgetModal) {
        // Close when clicking on backdrop
        budgetModal.addEventListener('click', function (e) {
            if (e.target === budgetModal) {
                closeModal();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && budgetModal.classList.contains('show')) {
                closeModal();
            }
        });
    }

    // -------------------------------------------------------------
    // 4. Delete Confirmation Handler
    // -------------------------------------------------------------
    const deleteForms = document.querySelectorAll('.delete-expense-form');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const confirmed = confirm('Are you sure you want to delete this expense? This action cannot be undone.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });

    // -------------------------------------------------------------
    // 5. Chart.js Category Breakdown (Dynamic Database Values)
    // -------------------------------------------------------------
    const chartCanvas = document.getElementById('categoryChart');
    if (chartCanvas && typeof Chart !== 'undefined') {
        const labelsData = chartCanvas.getAttribute('data-labels');
        const valuesData = chartCanvas.getAttribute('data-values');

        let labels = [];
        let values = [];

        try {
            labels = labelsData ? JSON.parse(labelsData) : [];
            values = valuesData ? JSON.parse(valuesData) : [];
        } catch (e) {
            console.error('Error parsing category chart data:', e);
        }

        if (labels.length > 0 && values.length > 0) {
            // Category-tailored color palette
            const colorMap = {
                'Food': '#f97316',
                'Travel': '#3b82f6',
                'Education': '#8b5cf6',
                'Shopping': '#ec4899',
                'Entertainment': '#6366f1',
                'Health': '#10b981',
                'Bills': '#f59e0b',
                'Other': '#64748b'
            };

            const backgroundColors = labels.map(label => colorMap[label] || '#94a3b8');

            new Chart(chartCanvas, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: backgroundColors,
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 14,
                                font: {
                                    family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                                    size: 12
                                },
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const value = context.parsed;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                    return ` ${context.label}: ₹${value.toLocaleString('en-IN', { minimumFractionDigits: 2 })} (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '68%'
                }
            });
        }
    }

    // -------------------------------------------------------------
    // 6. Client-side Real-time Search Filter for Expenses Table
    // -------------------------------------------------------------
    const clientSearchInput = document.getElementById('clientQuickSearch');
    const expensesTableBody = document.getElementById('expensesTableBody');

    if (clientSearchInput && expensesTableBody) {
        clientSearchInput.addEventListener('keyup', function () {
            const query = this.value.toLowerCase();
            const rows = expensesTableBody.querySelectorAll('tr');

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});
