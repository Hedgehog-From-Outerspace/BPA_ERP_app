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
});
