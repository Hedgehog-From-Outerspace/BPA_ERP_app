document.addEventListener('DOMContentLoaded', function() {
    // Your existing functions and code here

    // Function to handle updating order status via AJAX
    function updateOrderCorrectStatus(orderId, isChecked, type) {
        fetch("/update_order_status", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ order_id: orderId, correct: isChecked, type: type })
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

    // Event listener for checkbox change
    var checkboxes = document.querySelectorAll('input.form-check-input[type="checkbox"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var orderId = this.dataset.orderId;
            var isChecked = this.checked;
            var type = this.dataset.type;
            updateOrderCorrectStatus(orderId, isChecked, type);
        });
    });
});