document.addEventListener('DOMContentLoaded', function() {
    // Function to handle updating order status via AJAX
    function updateOrderCorrectStatus(orderId, isChecked, type, actualDeliveryPeriod = null) {
        fetch("/update_order_status", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                order_id: orderId, 
                correct: isChecked, 
                type: type, 
                actual_delivery_period: actualDeliveryPeriod 
            })
        })
        .then(response => {
            if (response.ok) {
                console.log('Order status updated successfully');
            } else {
                console.error('Failed to update order status');
            }
        })
        .catch(error => {
            console.error('Error updating order status:', error);
        });
    }

    // Function to handle updating supply order status
    function updateSupplyOrderStatus(supply_order_id, isChecked) {
        fetch("/update_supply_order_status", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                supply_order_id: supply_order_id, 
                correct: isChecked
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Failed to update supply order status:', data.error);
            } else {
                console.log('Supply order status updated successfully');
                document.getElementById('blue').textContent = 'Blauw: ' + data.current_stock.blue;
                document.getElementById('red').textContent = 'Rood: ' + data.current_stock.red;
                document.getElementById('grey').textContent = 'Grijs: ' + data.current_stock.grey;
            }
        })
        .catch(error => {
            console.error('Error updating supply order status:', error);
        });
    }

    // Function to enable/disable checkbox based on actual delivery period input
    function updateCheckboxState(orderId) {
        var input = document.querySelector('#actual_delivery_period_' + orderId);
        var checkbox = document.querySelector('#correct_' + orderId);
        
        if (input && checkbox) {
            if (input.value !== '') {
                checkbox.disabled = false;
            } else {
                checkbox.disabled = true;
                checkbox.checked = false; // Uncheck the checkbox if input is empty
            }
        }
    }

    // Function to update stock
    function resetStock() {
        fetch("/reset_stock", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Failed to update stock:', data.error);
            } else {
                console.log('Stock updated successfully');
                document.getElementById('blue').textContent = 'Blauw: ' + data.current_stock.blue;
                document.getElementById('red').textContent = 'Rood: ' + data.current_stock.red;
                document.getElementById('grey').textContent = 'Grijs: ' + data.current_stock.grey;
            }
        })
        .catch(error => {
            console.error('Error updating stock:', error);
        });
    }

    // Event listener for input change on actual delivery period
    var inputs = document.querySelectorAll('input.actual-delivery-input');
    inputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var orderId = this.dataset.orderId;
            updateCheckboxState(orderId);
        });
    });

    // Initially update checkbox state for existing inputs
    inputs.forEach(function(input) {
        var orderId = input.dataset.orderId;
        updateCheckboxState(orderId);
    });

    // Event listener for checkbox change
    var checkboxes = document.querySelectorAll('input.correct-checkbox');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var orderId = this.dataset.orderId;
            var isChecked = this.checked;
            var type = this.dataset.type;
            var actualDeliveryPeriod = document.querySelector('#actual_delivery_period_' + orderId) ? document.querySelector('#actual_delivery_period_' + orderId).value : null;
            
            if (isChecked && type === 'accountmanager') {
                updateOrderCorrectStatus(orderId, isChecked, type, actualDeliveryPeriod);
            } else {
                updateOrderCorrectStatus(orderId, isChecked, type);
            }
        });
    });

    // Event listener for supply checkbox change
    var checkboxes = document.querySelectorAll('input.supply-checkbox');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var supply_order_id = this.dataset.orderId;
            var isChecked = this.checked;
            updateSupplyOrderStatus(supply_order_id, isChecked);
        });
    });

    // Event listener for reset stock button click
    var resetButton = document.getElementById('reset-stock');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            resetStock();
        });
    }
});
